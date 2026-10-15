# Imports
from .rag_components.bm25_search import search_bm25
from .rag_components.embedders import EMBEDDERS, Embedder
from .rag_components.query_tranformations import generate_multiple_queries
from .rag_components.rerankers import reciprocal_rank_fusion, rerank_with_jev
from .rag_components.vector_search import search_vectors


# ============================================================================================================
#                                           Retrieve Function
# ============================================================================================================


def retrieve(
    connection,
    query,
    embedders=None,
    chunkers=None,
    retrieval_k=10,
    pool_k=20,
    final_k=5,
    hybrid_search=False,
    multiple_query=False,
    additional_query_count=0,
    jev_rerank=False,
):
    """
    Retrieve the top-k chunks for a query from one or more embedders' vector tables.

    For multiple queries, it will generate additional diverse queries and retrieve top-k chunks for each query.
    If there are 4 queries and retrieval_k=10 there is 40 chunks retrieved in total.
    pool_k = 20 specifies the number of top candidates to consider for fusion, from the hypothetical 40 retrieved chunks.
    final_k = 5 specifies the number of final results to return after fusion / reranking.


    Args:
        connection (psycopg.Connection): An open connection to the pgvector database.
        query (str): The natural-language query.
        embedders (str | Embedder | list | None): Registered name(s) such as
            "all-MiniLM-L6-v2" or "text-embedding-3-small", Embedder objects, or None for all.
        chunkers (str | list[str] | None): Restrict to one or more chunking strategies, or None for all.
        retrieval_k (int, optional): The number of chunks to retrieve per query. Defaults to 10.
        pool_k (int, optional): The number of top candidates to consider for fusion. Defaults to 20.
        final_k (int, optional): The number of final results to return after fusion. Defaults to 5.
        hybrid_search (bool, optional): Whether to combine BM25 and vector search results. Defaults to False.
        multiple_query (bool, optional): Whether to generate multiple diverse queries. Defaults to False.
        additional_query_count (int, optional): The number of **additional** queries to generate. Defaults to 0.
        jev_rerank (bool, optional): Whether to apply JEV reranking. Defaults to False.

    Returns:
        dict[str, list[dict]]: Embedder name -> rows of chunk_uid, source, chunker,
            header_path, content, and distance, ordered by ascending cosine distance.

    Examples:
        ```
        q = "What package do I install to use Agent Hooks?"
        ```
    """
    by_name = {embedder.name: embedder for embedder in EMBEDDERS}

    if embedders is None:
        selected = list(EMBEDDERS)
    else:
        if isinstance(embedders, (str, Embedder)):
            embedders = [embedders]
        selected = []
        for item in embedders:
            if isinstance(item, Embedder):
                selected.append(item)
            elif item in by_name:
                selected.append(by_name[item])
            else:
                raise KeyError(
                    f"unknown embedder {item!r}; registered: {sorted(by_name)}"
                )

    if isinstance(chunkers, str):
        chunkers = [chunkers]
    elif chunkers is not None:
        chunkers = list(chunkers)

    # =================== ADD the Multiple Query Transformation ==================
    search_queries = [query]

    if multiple_query:
        if additional_query_count < 1:
            raise ValueError("additional_query_count must be at least 1")

        search_queries.extend(generate_multiple_queries(query, additional_query_count))

    # === Display multiple queries ===
    # print(f"Original query:\n   - {query}")
    # print("Additional diverse queries:")
    # for number, search_query in enumerate(search_queries[1:], start=1):
    #     print(f"  {number}. {search_query}")

    # ================= ADD BM25 if hybrid_search is enabled =================
    # BM25 does not depend on the embedding model, so run it once.
    bm25_by_query = {}

    if hybrid_search:
        bm25_by_query = {
            search_query: search_bm25(
                connection,
                search_query,
                k=retrieval_k,
                chunkers=chunkers,
            )
            for search_query in search_queries
        }

    # ================= Collect results for each embedder =================
    results = {}

    for embedder in selected:
        # ==== Collect each query's ranked candidates for this embedder ====
        candidates = []

        for search_query in search_queries:
            candidates.extend(
                search_vectors(
                    connection,
                    search_query,
                    embedder,
                    k=retrieval_k,
                    chunkers=chunkers,
                )
            )

            if hybrid_search:
                candidates.extend(
                    bm25_by_query[search_query]
                )  # Add BM25 results to the candidate list

        # ==== ADD:Fuse per-query rankings when multi-query is enabled ====
        if hybrid_search or multiple_query:
            # Fuse the rankings of candidates from multiple queries or hybrid search
            candidates = reciprocal_rank_fusion(
                candidates,
                rank_constant=60,
                top_k=pool_k,
            )
        else:
            # If not using hybrid search or multiple query, just take the top pool_k candidates
            candidates = candidates[:pool_k]

        # ==== Apply JEV reranking if enabled ====
        if jev_rerank:
            candidates = rerank_with_jev(
                query,
                candidates,
                top_n=final_k,
            )
        else:
            # return the top final_k candidates if JEV reranking is not applied
            candidates = candidates[:final_k]

        result_name = embedder.name

        results[result_name] = candidates

    return results
