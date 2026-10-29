# CounselOS Threat Model

## Assets to Protect

1. **Case documents** — confidential client materials
2. **Extracted text and analysis** — derived from case documents
3. **AI-generated findings** — may reveal case strategy
4. **User review decisions** — attorney work product
5. **System integrity** — correct operation of analysis tools

## Threat Actors

| Actor | Capability | Motivation |
|-------|-----------|------------|
| Remote attacker | Network access | Data theft, disruption |
| Local malware | OS-level access | Exfiltration, ransomware |
| Malicious document | Parsed by application | Code execution, data leak |
| Unauthorized user | Physical device access | Unauthorized case access |
| Supply chain | Compromised dependency | Backdoor, data collection |

## Threats and Mitigations

### T1: Accidental Cloud Upload
- **Mitigation**: No cloud API integration, network denial policy
- **Test**: Offline operation verification with network monitoring

### T2: Telemetry Data Leak
- **Mitigation**: No analytics, no crash reporting, no update checks
- **Test**: Network traffic observation during all workflows

### T3: Malicious Document Content
- **Mitigation**: File signature validation, resource limits, no script execution
- **Test**: Adversarial document test suite

### T4: Prompt Injection via Documents
- **Mitigation**: Document text treated as data, typed tool arguments, bounded context
- **Test**: Embedded instruction detection tests

### T5: Cross-Matter Data Leak
- **Mitigation**: Matter-scoped queries, FK constraints, isolation tests
- **Test**: Cross-matter access attempt suite (release blocker)

### T6: Local API Abuse
- **Mitigation**: Loopback binding, session auth, origin validation
- **Test**: Unauthorized request rejection tests

### T7: Device Theft
- **Mitigation**: Encrypted backups, OS-level encryption recommended
- **Test**: Backup encryption/decryption verification

### T8: Dependency Tampering
- **Mitigation**: Pinned versions, hash verification, model manifests
- **Test**: Integrity verification on startup

### T9: Parser Vulnerability
- **Mitigation**: Resource limits, restricted worker, input validation
- **Test**: Large/malformed file processing tests

### T10: Sensitive Data in Logs
- **Mitigation**: Audit log filters sensitive keys, no document text in logs
- **Test**: Log content inspection for PII/case data
