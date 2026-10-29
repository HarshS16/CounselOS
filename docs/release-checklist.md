# CounselOS Release Checklist

## Pre-Release Gates

### Security (ALL must pass)
- [ ] Core workflows function with network interfaces disabled
- [ ] No unintended outbound network traffic observed
- [ ] Cross-matter isolation tests pass (zero failures)
- [ ] Local API rejects unauthenticated requests
- [ ] Backup encryption/restoration verified
- [ ] No secrets in source code or logs
- [ ] Dependencies pinned and scanned for vulnerabilities
- [ ] Model artifact hashes verified

### Quality (ALL must pass)
- [ ] Retrieval recall@10 ≥ 95% on benchmark
- [ ] Citation validity ≥ 98%
- [ ] Zero critical fabricated facts observed
- [ ] AI findings distinguish provisional from reviewed
- [ ] Extraction failures visible in UI

### Functionality
- [ ] Document import (PDF + DOCX) works
- [ ] OCR processes scanned documents
- [ ] Search returns relevant results with source links
- [ ] QA answers cite correct source passages
- [ ] Chronology preserves date precision
- [ ] Comparison shows both sides of discrepancies
- [ ] Human review decisions persist across restart
- [ ] Export generates valid DOCX report
- [ ] Application runs on 16GB RAM reference device

### Legal (Before commercial release)
- [ ] Model licenses reviewed for commercial use
- [ ] Dependency licenses audited
- [ ] Indian data protection obligations reviewed
- [ ] Professional confidentiality requirements assessed
- [ ] Known limitations documented for pilot users

### Usability
- [ ] Error messages are actionable
- [ ] Long-running tasks show progress
- [ ] Destructive actions require confirmation
- [ ] AI content visually distinct from reviewed content
