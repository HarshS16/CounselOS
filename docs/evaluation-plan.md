# CounselOS Evaluation Plan

## CounselBench Benchmark

### Composition Target
- 30-50 case bundles for development
- Mix of digital PDFs, DOCX files, scanned PDFs
- English, Hindi, and mixed-language records
- Varying OCR quality levels
- Known contradictions and discrepancies for ground truth

### Quality Metrics (Proposed Gates)

| Metric | Target | Notes |
|--------|--------|-------|
| Retrieval Recall@10 | ≥95% | On answerable labelled queries |
| Citation validity | ≥98% | Valid source references |
| Substantive claim support | ≥95% | Against source evidence |
| Discrepancy precision (high-priority) | ≥90% | Must also measure recall |
| Critical fabricated facts | 0 observed | Does not prove zero risk |
| Cross-matter isolation failures | 0 | Release blocker |
| Unintended outbound traffic | 0 observed | Under defined offline tests |
| Backup/restore scenarios | 100% pass | All required scenarios |

### Test Layers

1. **Unit tests** — hashing, chunking, schema validation, date precision
2. **Integration tests** — import, OCR, indexing, retrieval, inference, export
3. **AI regression tests** — fact retrieval, comparison, abstention, citation fidelity
4. **Security tests** — network monitoring, cross-matter access, API misuse
5. **User acceptance tests** — lawyer task completion, finding quality assessment
