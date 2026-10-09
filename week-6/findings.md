# Week 6 Research Note: Query Transformation and Re-ranking

## Scope

This note summarizes `week6_advanced_rag.ipynb`, which extends the Week 5 retrieval pipeline with a query-side transformation and a ranking-side fusion step, then measures whether it actually improved retrieval. The assignment covers Part 1 (build the transformation and re-ranking components), Part 2 (measure the effect of query transformation + RRF against the Week 5 baseline), and Part 3 (find a query where the transformation hurt retrieval and explain why, or explain why none did). Part 4 is a self-directed exploration I added beyond the assignment scope, using a System One "Jev" reranker, and is reported separately at the end so it doesn't get conflated with the required findings.

Part 1 implemented four pieces and wired all of them into one extended `retrieve()` function: a BM25 lexical index, an LLM-based multi-query generator (`gpt-4o`, temperature 0.0, modeled on the rag-fusion reference implementation), a Reciprocal Rank Fusion (RRF) combiner, and a Jev reranker. The required comparison in Part 2, however, uses only two of these: the original single vector query versus that same query plus 3 LLM-generated paraphrases, fused with RRF. BM25 is not part of the Part 2/3 comparison — it's built, but it's only exercised later in the optional Part 4 hybrid-search experiment.

## Exact Configuration

- Corpus: same 8 Microsoft Learn documents from Week 5, same pgvector store
- Chunking strategy evaluated: `md-header`
- Embedder: `text-embedding-3-small` only (Week 5's MiniLM comparison was dropped for this week's experiment)
- Distance metric: cosine distance
- Test queries: 10, same set and relevance labels as Week 5 (expanded relevant set + one designated primary chunk per query)
- Query transformation model: `gpt-4o`, `temperature=0.0`, `max_output_tokens=800`, 3 additional paraphrases generated per query (4 total queries fused)
- Retrieval depth per query: `retrieval_k=10`
- Fusion pool size: `pool_k=20`
- RRF constant: `rank_constant=60`
- Final depth compared in Part 2: `final_k=3`
- Hybrid search (BM25): disabled for Part 2/3. Only pertains to part 4. 
- Jev reranking: disabled for Part 2/3 (see Part 4)

## Findings: Query Transformation + RRF vs. Single-Query Baseline

Two retrieval configurations were compared at `k=3`, both using `text-embedding-3-small` and the `md-header` chunker. The baseline issues the original query once and returns the top 3 chunks by cosine similarity. The transformed pipeline takes that same query, calls the LLM to generate 3 diverse paraphrases, vectorizes all 4 queries, and fuses the 4 resulting ranked lists with RRF before taking the top 3.

**Aggregate quality.** Multi-query + RRF improved mean per-query recall from 0.757 to 0.907 (+0.150), mean precision from 0.400 to 0.467 (+0.067), and primary-answer hit rate from 90% to 100%.

**Per-query deltas.** Two of the ten queries changed; the other eight were identical between baseline and transformed retrieval.
- *"How long does an Agent Hooks interceptor wait before it times out?"* (fact: "five seconds") went from 0 hits to 1 hit (precision 0 → 0.333, recall 0 → 1.000), and its primary chunk flipped from missed to found. The single baseline query apparently wasn't phrased closely enough to the surrounding sentence containing "five seconds" to pull that chunk into the top 3. One of the three LLM-generated paraphrases must have matched the wording around the fact more closely, and RRF was enough to surface it once it appeared in even one of the four ranked lists.
- *"Which Cosmos DB provider contains memories of facts or summaries between sessions?"* (fact: "CosmosMemoryContextProvider") also gained a hit (precision +0.333, recall +0.5), but its primary chunk was already being retrieved correctly at baseline, so the primary-hit flag didn't change — this is a pure recall gain, pulling in a second relevant chunk alongside the one the baseline already found.

The other eight queries — mostly ones asking for a specific package, function, class, or provider name (e.g., "agent-hooks-sdk", "create_vector_search_tool", "Harness Agent") — were already retrieved correctly by the single-query baseline, and multi-query + RRF didn't change them in either direction.

**Latency cost.** The transformed pipeline is substantially slower, because 4 queries now have to be embedded and searched instead of 1, and because the paraphrase generation itself is an LLM round trip to Microsoft Foundry. Single-query median latency was 160.85ms (mean 443.38ms); multi-query + RRF median latency was 3451.63ms (mean 3823.57ms) — roughly a 21x increase in median latency for a 0.15 gain in mean recall. Nearly all of the added time is the LLM call generating the 3 paraphrases.

One caveat worth stating plainly: `generate_multiple_queries` calls an LLM at temperature 0.0, but the paraphrases it produces are not guaranteed to be identical across runs, so the exact precision/recall/latency numbers above can shift somewhat if the notebook is rerun. The qualitative pattern — a small recall gain concentrated in one or two queries, at a large latency cost — has held across the runs I checked.

## No Failure Case

No query regressed. Every one of the 10 queries' recall, precision, and primary-hit status either improved or stayed exactly the same going from single-query to multi-query + RRF; none went down.

I think this is structural, not luck. The original query is still one of the four lists RRF fuses. So a chunk the baseline already ranked in the top 3 gets RRF credit from that alone. On top of that, it picks up whatever the three paraphrases add. That makes it hard for a weak or off-target paraphrase to push a correct chunk out of the fused top 3 — at worst, a bad paraphrase just adds noisy candidates without removing a strong one. I was specifically worried that the diversity encouraged in the paraphrase-generation prompt could backfire and boost a semantically related but wrong chunk, but that did not happen in this sample.

I'd also point out two likely reasons this specific result might not generalize. First, this comparison is pure dense vector search with no BM25 layered in. Most of my test queries also target a named term, like a package name, class name, or provider name. Named terms tend to survive paraphrasing and keep the embedding anchored to the same chunk. A corpus with vaguer or more ambiguous queries might show more RRF-induced drift. Second, ten queries is a small sample. A single regression is plausible, but I didn't observe one here. So "none regressed" describes this run, but is not guaranteed.

## Part 4: Supplementary Exploration — Jev Reranking (not required by the assignment)

Outside the assignment scope, I added a "Jev" System One reranker (inspired by the rag-fusion repository's Jev experiment) that scores each candidate chunk's P(relevant) against the query directly, instead of ranking by cosine similarity or RRF score. I ran two follow-on experiments with it, reported here separately since they go beyond what Parts 1–3 ask for.

**Experiment 1 — cosine similarity vs. Jev reranking, pure vector search, top 1.** Reranking the same top-10 pool with Jev instead of taking the top 1 by cosine similarity improved mean recall from 0.553 to 0.753 (+0.2), mean precision from 0.800 to 1.000 (+0.2), and primary-answer hit rate from 60% to 90%. Three queries improved (the interceptor-timeout question, the Neo4j package question on primary-hit only, and the planning/todo-agent question); the other seven were unchanged. The cost was a roughly 1.7x increase in median latency (192.8ms → 329.7ms) from the added System One call per query — much cheaper than the multi-query LLM call in Part 2.

**Experiment 2 — single-query + Jev vs. full hybrid (BM25 + multi-query + RRF) + Jev, top 1.** Layering hybrid search and multi-query fusion on top of Jev reranking left mean precision (1.000) and mean recall (0.753) unchanged, and only lifted primary-answer hit rate from 90% to 100% — on the strength of a single query ("What function lets an agent search a vector store?") whose primary chunk flipped from missed to found. The other nine queries were unchanged. The latency cost here is large: median latency rose from 329.7ms to 3321.2ms (about 10.1x), and the tail is considerably worse than the median suggests — the full pipeline's max observed latency was roughly 24.2 seconds with a p95 around 15.4 seconds, against a max of about 0.6 seconds for the single-query + Jev baseline. That gap points to at least one component (most likely the query-generation or Jev call) occasionally stalling or retrying, which the median alone hides.

## Conclusion

For the required comparison, multi-query + RRF produced a small, concentrated improvement: two of ten queries benefited, one by finding its primary chunk for the first time and one by gaining an extra relevant chunk without changing its primary-hit status, while the rest were unaffected. That gain came at roughly a 21x median latency cost, driven almost entirely by the added LLM call. No query regressed in this sample, which I attribute to RRF preserving the original query's contribution to the fused ranking even when the paraphrases added noise — though with only ten queries, mostly built around named terms, I would not generalize "no failures" beyond this specific test set.

The optional Jev exploration suggested that re-ranking the existing pool by a System One model's direct relevance judgment can be a cheaper way to capture some of the same quality gain, though the comparisons underneath that claim come with caveats. Jev's roughly 1.7x latency cost bought a 0.2 recall improvement at final_k=1, while multi-query's roughly 21x cost bought a 0.15 improvement at final_k=3; recall at k=1 starts from a lower baseline and has more room to move on a single hit, so these two deltas aren't measuring quite the same thing, even though the latency-to-quality ratio still favors Jev enough to be worth testing at final_k=3 before drawing a firmer conclusion. Stacking the full hybrid and multi-query pipeline on top of the Jev reranker added mostly latency, including a heavy tail, for one additional primary-hit flip, lifting primary-answer hit rate from 90% to 100% while leaving mean precision (1.000) and mean recall (0.753) unchanged. That comparison isn't fully isolated either, since the pool Jev reranks from also grew from 10 candidates to 20 between these two runs, so the hit-rate gain could come from the added retrieval methods, from the larger pool alone, or from some mix of the two. This was an experiment error.  A cleaner test would hold pool_k fixed and vary only hybrid_search/multiple_query, or test a single-query, vector-only, pool_k=20 + Jev configuration as a control.