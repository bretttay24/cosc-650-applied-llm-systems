# Week 5 Research Note: RAG Retrieval Evaluation

## Scope

This note summarizes `week5_rag.ipynb`, which builds and evaluates a retrieval-augmented generation pipeline over eight Microsoft Learn documents. The pipeline creates chunks with three strategies, embeds them with both a local sentence-transformer and a Microsoft Foundry-hosted embedding model, and stores the chunks and vectors in PostgreSQL with pgvector.

The retrieval comparison holds chunking constant on the `md-header` strategy and compares `all-MiniLM-L6-v2` with `text-embedding-3-small` across ten test queries. Retrieval quality is measured at k=1 and k=5 using chunk-level precision, recall, and whether the designated primary chunk was retrieved. A final generation step supplies retrieved chunks to a Foundry-hosted language model and requires it to answer only from that context with citations.

## Exact Configuration

- Corpus: 8 Microsoft Learn documents
- Vector store: PostgreSQL with pgvector
- Distance metric: cosine distance
- Chunking strategies: fixed windows, Markdown headers, and Markdown headers followed by recursive character splitting
- Total chunks: 439
- Evaluated chunker: `md-header` with 73 chunks
- Local embedder: `all-MiniLM-L6-v2`, 384 dimensions
- Hosted embedder: `text-embedding-3-small`, 1,536 dimensions
- Test queries: 10
- Retrieval depths: k=1 and k=5
- Relevance rule: an expanded relevant set containing every `md-header` chunk from the expected document that includes the labeled fact string
- Primary relevance rule: one manually designated chunk that most directly answers each query

The expanded relevance rule is intentionally permissive. It includes chunks where the fact appears only in supporting context, such as an import, code sample, or resource link. Precision and recall therefore measure retrieval of fact-bearing chunks in the expected document, while `hit_primary` measures retrieval of the most direct answer.

## Retrieval Comparison

| Metric at k=5 | `all-MiniLM-L6-v2` | `text-embedding-3-small` |
|---|---:|---:|
| Mean precision | 0.26 | 0.34 |
| Mean recall | 0.86 | 0.98 |
| Queries with primary chunk retrieved | 10/10 | 10/10 |

At k=5, the models tied on all six queries with one relevant chunk. They differed on three of the four queries with multiple relevant chunks. `text-embedding-3-small` achieved higher recall for the vector-search-tool query (1.00 versus 0.67), the Cosmos DB memory-provider query (1.00 versus 0.50), and the local-evaluator query (0.80 versus 0.40). Both models achieved 1.00 recall for the Neo4j package query.

At k=1, MiniLM returned a chunk from the expanded relevance set for 9 of 10 queries, compared with 8 of 10 for `text-embedding-3-small`. Under the stricter primary-chunk measure, MiniLM succeeded on 7 of 10 queries and `text-embedding-3-small` succeeded on 6 of 10. This small top-1 difference establishes that MiniLM is stronger with this ten-query test set. The k=1 results also show why precision, recall, and `hit_primary` must remain separate: a retrieved chunk can belong to a multi-chunk relevance set without being the designated primary answer.

The grounded-generation example retrieved the Agent Hooks installation section and correctly answered that the required package is `agent-hooks-sdk`, citing the chunk that directly supported the answer.

## Failure Case

The selected failure query was: **"What should I pin so evaluation results stay comparable across runs?"** With `all-MiniLM-L6-v2`, `md-header` chunking, and k=1, retrieval returned the chunk from header `Evaluation.md > Conversation split strategies` instead of header `Microsoft-Foundry-evaluation.md > Quality gates`. Because the retrieved context did not contain the answer, the generation model correctly responded that it did not know based on the available context.

The incorrect and primary chunks both concern evaluation and share broad vocabulary such as `evaluator`, `results`, and `run`. However, the query's discriminating term, `pin`, appears in the primary chunk. At the same k, `text-embedding-3-small` ranked the `Quality gates` chunk first and the generated answer correctly identified datasets, model deployments, evaluator versions, and rubric versions.

This experiment demonstrates a dense-retrieval ranking difference, but it does not isolate its cause. Vector dimensionality, training data, and model objectives may all contribute. The answer was present intact in a well-formed `md-header` chunk, so the observed failure was not caused by the chunker splitting or omitting the fact.

Two potential mitigations follow from the failure. First, retrieving more than one chunk would expose the generator to the primary chunk because MiniLM retrieved it within the top five. Second, hybrid lexical and dense retrieval could reward the exact term `pin` and improve the ranking. BM25 was proposed but not implemented or tested in this notebook, so its effect remains unverified.

## Conclusion

Holding chunking constant showed that embedding-model performance depended on retrieval depth and the relevance definition. At k=5, `text-embedding-3-small` recovered more of the expanded relevant sets and increased mean recall from 0.86 to 0.98, while both models retrieved every designated primary chunk. At k=1, MiniLM held a small advantage on both expanded relevance and primary-chunk retrieval, but the ten-query sample is too small to support a general model ranking.

The failure case showed that a grounded generator cannot recover an answer that retrieval does not provide. Its refusal to answer from the wrong chunk was appropriate, and increasing retrieval depth made the correct evidence available. The main limitation is the permissive fact-string relevance rule: it makes labeling reproducible and recall measurable, but it treats supporting references as relevant alongside chunks that directly answer the question. A larger test set with stricter graded relevance judgments would provide stronger evidence about retrieval quality.
