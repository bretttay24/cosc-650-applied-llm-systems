import mlflow
from mlflow.entities import SpanType
from typesafe_sdk import Noul, NoulCriteria, RetryPolicy, TypeSafeClient


# ============================================================================================================
#                                   Reciprocal Rank Fusion
# Rewritten from the RRF function in Adrian Raudaschl's RAG-Fusion (MIT): https://github.com/Raudaschl/rag-fusion
# ============================================================================================================


@mlflow.trace(name="reciprocal_rank_fusion", span_type=SpanType.RERANKER)
def reciprocal_rank_fusion(retrieved_chunks, rank_constant=60, top_k=None):
    """
    Fuse rankings from multiple queries and retrievers.

    Args:
        retrieved_chunks (list): A list of dictionaries containing retrieved chunks.
        rank_constant (int, optional): The constant used in the reciprocal rank fusion formula. Defaults to 60.
        top_k (int, optional): The number of top-ranked chunks to return. If None, return all. Defaults to None.
    Returns:
        list: A list of fused and ranked chunks, each containing the original chunk data along with the fused rank and RRF score.
    """
    if rank_constant <= 0:
        raise ValueError("rank_constant must be greater than 0")

    # Each retriever/query combination is one independent ranked list.
    query_rankings = {}

    for candidate in retrieved_chunks:
        ranking_key = (candidate["retriever"], candidate["search_query"])
        query_rankings.setdefault(ranking_key, []).append(candidate)

    fused_chunks = {}

    for (retriever, search_query), ranking_candidates in query_rankings.items():
        ranked_candidates = sorted(ranking_candidates, key=lambda candidate: candidate["retrieval_rank"])

        for candidate in ranked_candidates:
            chunk_uid = candidate["chunk_uid"]

            if chunk_uid not in fused_chunks:
                # Remove fields that describe only one retrieval occurrence.
                fused_chunks[chunk_uid] = {key: value for key, value in candidate.items() if key not in {"retriever", "search_query", "retrieval_rank", "raw_score", "distance"}}
                fused_chunks[chunk_uid]["rrf_score"] = 0.0
                fused_chunks[chunk_uid]["retrievals"] = []

            rank = candidate["retrieval_rank"]
            fused_chunks[chunk_uid]["rrf_score"] += 1 / (rank_constant + rank)

            fused_chunks[chunk_uid]["retrievals"].append({"retriever": retriever, "search_query": search_query, "rank": rank, "raw_score": candidate["raw_score"]})

    ranked_chunks = sorted(fused_chunks.values(), key=lambda candidate: (-candidate["rrf_score"], candidate["chunk_uid"]))

    if top_k is not None:
        ranked_chunks = ranked_chunks[:top_k]

    for fused_rank, candidate in enumerate(ranked_chunks, start=1):
        candidate["fused_rank"] = fused_rank

    return ranked_chunks


# ============================================================================================================
#                                   Jev Reranker
# Adapted from Adrian Raudaschl's RAG-Fusion Jev experiment (MIT) and Adam Hevenor's hev/reranker (Apache-2.0):
# https://github.com/Raudaschl/rag-fusion/tree/master/experiments/jev-in-the-pipeline
# https://github.com/hev/reranker
# ============================================================================================================

JEV_QUESTION = "Document `documents.{id}` is relevant to `query`: it contains information that answers or directly addresses it."

JEV_CRITERIA = {
    "true": ("The document contains information that answers the query or directly addresses what it asks about."),
    "false": ("The document is only loosely related, on a similar topic, or does not address what the query asks."),
}

jev_client = None


def _get_jev_client():
    """Create the optional JEV client only when JEV reranking is requested."""
    global jev_client
    if jev_client is None:
        jev_client = TypeSafeClient(retry=RetryPolicy(max_retries=6, backoff_max=30.0, timeout=90.0))
    return jev_client


@mlflow.trace(name="jev_rerank", span_type=SpanType.RERANKER)
def rerank_with_jev(query, candidates, *, top_n=None, threshold=None, client=None, model="jev-latest"):
    """
    Rerank retrieved candidate dictionaries by P(relevant).

    Args:
        query (str): The query string to match against candidate documents.
        candidates (list[dict]): A list of candidate document dictionaries.
        top_n (int, optional): The maximum number of top candidates to return.
        threshold (float, optional): Minimum JEV score to include a candidate.
        client (TypeSafeClient, optional): The JEV client to use.
        model (str, optional): The JEV model to use.

    Returns:
        list[dict]: The reranked list of candidate dictionaries with added
        "jev_score" and "jev_rank" fields.
    """
    if not candidates:
        return []

    if len(candidates) > 30:
        raise ValueError("This notebook adapter supports at most 30 candidates per call")

    if client is None:
        client = _get_jev_client()

    candidate_ids = {
        f"D{index:02d}": candidate for index, candidate in enumerate(candidates)
    }  # stable short ids so Jev can reference one candidate without echoing full chunk text

    state = {
        "query": query,
        "documents": {candidate_id: {"title": candidate.get("header_path", ""), "text": candidate["content"]} for candidate_id, candidate in candidate_ids.items()},
    }  # every Noul question below reads from this same state via its candidate_id

    questions = {
        candidate_id: Noul(instructions=JEV_QUESTION.format(id=candidate_id), criteria=NoulCriteria(**JEV_CRITERIA)) for candidate_id in candidate_ids
    }  # one yes/no question per candidate, all sent in a single request and scored in parallel

    with mlflow.start_span(name="jev_model_call", span_type=SpanType.LLM) as span:
        span.set_inputs({"text": {"query": query, "documents": state["documents"]}, "model": model})
        response = client.system_one(state=state, questions=questions, model=model)
        relevance_probabilities = {candidate_id: float(response.answers[candidate_id].noul) for candidate_id in candidate_ids}
        span.set_outputs({"relevance_probabilities": relevance_probabilities})

    reranked = []
    for candidate_id, candidate in candidate_ids.items():
        jev_score = relevance_probabilities[candidate_id]  # P(relevant) in [0, 1] for this candidate

        if threshold is not None and jev_score < threshold:
            continue

        reranked.append({**candidate, "jev_score": jev_score})

    reranked.sort(key=lambda candidate: (-candidate["jev_score"], -candidate.get("rrf_score", 0.0), candidate["chunk_uid"]))

    for rank, candidate in enumerate(reranked, start=1):
        candidate["jev_rank"] = rank

    return reranked[:top_n] if top_n is not None else reranked
