# Evaluation

## Variant Comparison

| Variant | Recall@3 | Recall@5 | MRR | Citation Acc. | Rejection Acc. | Avg Latency |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline vector RAG | 0.3810 | 0.4762 | 0.3071 | 0.2143 | 0.6250 | 111.2100 |
| Vector RAG + normalization | 0.3810 | 0.4762 | 0.3071 | 0.2143 | 0.6250 | 137.0600 |
| Vector RAG + NER filtering | 0.4524 | 0.6667 | 0.4246 | 0.3095 | 0.6250 | 147.8800 |
| Vector RAG + reranker | 0.5952 | 0.6667 | 0.4889 | 0.3810 | 0.6250 | 1017.6000 |
| Full system | 0.7381 | 0.7857 | 0.5849 | 0.4524 | 0.6250 | 1050.6600 |

## Analysis

The strongest variant by Recall@3 is **Full system**. If the full system does not lead every metric, inspect the per-question CSV files; the usual causes are over-restrictive metadata filters, reranker model fallback, or unavailable generation service.

Per-question outputs are saved under each variant directory.
