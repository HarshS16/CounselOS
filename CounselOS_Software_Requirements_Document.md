# CounselOS

## Software Requirements Document (SRD)

**Document version:** 1.0\
**Status:** Proposed baseline for discovery, implementation, and pilot
validation\
**Prepared:** 11 October 2026\
**Product category:** Offline-first legal evidence-analysis desktop
software\
**Initial market:** Indian litigation lawyers, advocates, and legal
assistants\
**Primary deployment:** Single-user desktop application on a standard
laptop\
**Primary workflow:** Case-file ingestion, evidence discovery,
chronology construction, and cross-document discrepancy analysis

------------------------------------------------------------------------

## Document Control

  -----------------------------------------------------------------------
  Field                               Value
  ----------------------------------- -----------------------------------
  Document owner                      Product / Engineering

  Intended audience                   Product, engineering, UX, QA,
                                      security, legal domain reviewers,
                                      pilot users

  Baseline platform                   Windows 10/11 64-bit initially;
                                      other platforms subject to
                                      validation

  Minimum target hardware             16 GB RAM, SSD, modern 64-bit CPU

  Core operating mode                 No internet required for normal
                                      operation

  Data processing boundary            Local device, under the user's
                                      control

  Release objective                   Supervised pilot after quality,
                                      security, and usability gates are
                                      met
  -----------------------------------------------------------------------

### Status and interpretation

This SRD defines the proposed requirements for CounselOS version 1.0.
Requirements and targets are intended to be testable, but some numerical
thresholds are provisional until validated against representative
documents and hardware. Legal, privacy, and security requirements must
be reviewed by qualified professionals before commercial release.

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and
**MAY** are used in their conventional requirements sense.

------------------------------------------------------------------------

# 1. Executive Summary

CounselOS is a local-first AI workspace designed to help Indian
litigation teams review confidential case materials without sending case
content to external AI services. It combines a desktop case workspace,
local document processing, hybrid retrieval, a quantized language model,
evidence-analysis workflows, source verification, and human review.

The product is not intended to act as a lawyer or make final legal
determinations. Its job is to reduce the time spent locating,
organizing, and comparing evidence while making uncertainty and source
provenance visible.

The first release will focus on four connected capabilities:

1.  **Private case vault:** create matters and import case documents
    into controlled local storage.
2.  **Evidence search and question answering:** retrieve relevant
    passages and answer factual questions with verifiable source
    references.
3.  **Chronology and claim extraction:** identify candidate events,
    dates, entities, and factual assertions while preserving source
    links.
4.  **Discrepancy analysis:** compare claims across selected documents
    and surface potential contradictions, omissions, or ambiguities for
    lawyer review.

The first release will not include autonomous court filing, unsupervised
legal advice, cloud-based processing, automatic external communications,
or unrestricted internet legal research.

The product's differentiator is not merely offline model execution. It
is a complete evidence workflow where every important AI-generated
finding is traceable to original material, reviewable by a human, and
generated inside a defined security boundary.

------------------------------------------------------------------------

# 2. Product Vision and Objectives

## 2.1 Vision

Provide a private, evidence-grounded legal workbench that helps lawyers
understand and work with their case files while keeping confidential
case content under their control.

## 2.2 Problem statement

Litigation teams may need to inspect large collections of pleadings,
affidavits, written statements, orders, correspondence, invoices,
exhibits, and scanned records. Locating a fact or comparing two accounts
can require repeated manual review.

General-purpose cloud AI may be unsuitable for some legal matters
because of confidentiality, client instructions, contractual
restrictions, and data-handling concerns. A locally hosted language
model helps reduce external exposure but is not sufficient on its own. A
useful product also needs accurate extraction, retrieval, provenance,
review workflows, predictable tool permissions, and verifiable offline
operation.

## 2.3 Product goals

-   Enable local import, indexing, search, and analysis of case
    documents.
-   Keep case documents, extracted text, prompts, embeddings, model
    inputs, outputs, and reports on the local device during normal
    operation.
-   Make source documents and precise source locations accessible from
    each material finding.
-   Help users build a chronology and compare claims across documents.
-   Represent uncertainty, conflicting evidence, and extraction
    limitations explicitly.
-   Preserve original files and maintain a record of analysis and human
    review.
-   Operate on a standard 16 GB RAM laptop with a quantized model and
    bounded context.
-   Establish measurable quality and security gates before pilot
    deployment.

## 2.4 Success criteria

The product will be considered ready for a supervised pilot when:

-   The core workflow operates with Wi-Fi and Ethernet disabled.
-   No unintended outbound network traffic is observed in defined
    offline tests.
-   Users can import supported documents, search them, inspect source
    passages, review findings, and export a report.
-   The held-out benchmark meets the approved retrieval, citation, and
    factual-support targets.
-   Cross-matter isolation tests pass.
-   Encrypted backup and restoration tests pass.
-   A small group of practicing lawyers can complete representative
    tasks and judge the findings useful enough to review.
-   Critical known limitations are documented and communicated to pilot
    users.

## 2.5 Product principles

1.  **Evidence before fluency:** a plausible answer is not acceptable if
    its factual basis cannot be shown.
2.  **Local by design:** the offline guarantee must be enforced and
    tested, not merely described in marketing.
3.  **Human judgment remains central:** AI findings are provisional
    until reviewed where the workflow requires review.
4.  **Fail visibly:** extraction failure, poor OCR, missing evidence,
    conflicting sources, and incomplete processing must be visible.
5.  **Least privilege:** each component receives only the data and
    capabilities required for its task.
6.  **Reproducibility:** important outputs should be associated with
    model, prompt, workflow, and retrieval versions.
7.  **Incremental complexity:** use a modular monolith and deterministic
    workflows before introducing multi-agent autonomy.

------------------------------------------------------------------------

# 3. Scope

## 3.1 In scope for version 1.0

-   Desktop application and local Python service.
-   Local matter creation and management.
-   Import of PDF and DOCX documents.
-   Local text extraction and OCR for scanned PDFs.
-   Original-file hashing and integrity checks.
-   Page- and paragraph-aware text representation.
-   Local full-text and semantic retrieval.
-   Local language-model inference.
-   Evidence-grounded question answering.
-   Structured extraction of claims, events, dates, people, and
    organizations.
-   Chronology generation.
-   Comparison of selected documents or claims.
-   Source citation validation.
-   Human review and correction of findings.
-   DOCX and PDF report export.
-   Local audit events.
-   Encrypted storage and backup design.
-   Offline operation tests and packaged desktop installation.
-   Benchmarking, quality evaluation, and supervised pilot workflow.

## 3.2 Out of scope for version 1.0

-   Autonomous legal representation or final legal advice.
-   Autonomous court filing or submission to government systems.
-   Automatic sending of emails or messages to opposing counsel,
    clients, or courts.
-   Internet browsing or remote legal-research APIs.
-   Cloud-hosted inference or external AI-provider fallback.
-   Training a foundation model on client documents.
-   Multi-user collaboration or a shared firm-wide server.
-   Native mobile applications.
-   Comprehensive legal drafting across all document types.
-   Automated legal deadline calculation as an authoritative source.
-   Automatic classification of privilege or confidentiality as a
    substitute for lawyer review.
-   Handwriting recognition guarantees.
-   Guaranteed interpretation of every Indian language or regional
    script.

## 3.3 Future scope candidates

-   On-premises multi-user deployment.
-   Additional Indian languages and improved OCR.
-   Controlled legal research over a licensed, versioned corpus.
-   Drafting studio with approved templates.
-   Matter-level task tracking.
-   Redaction tools.
-   Additional document formats.
-   Integration with firm document-management systems.
-   Administrator-managed policies and model packages.

Future capabilities require separate requirements, threat modelling,
licensing review, and acceptance criteria.

------------------------------------------------------------------------

# 4. Stakeholders and Users

## 4.1 Primary users

### Litigation lawyer / advocate

Needs to identify relevant evidence, compare factual accounts, examine
timelines, prepare case notes, and verify source material.

### Legal associate or assistant

Needs to organize document bundles, find facts, prepare summaries,
extract dates, and produce reviewable evidence reports for a supervising
lawyer.

## 4.2 Secondary stakeholders

-   Law-firm owner or managing partner.
-   IT or security administrator supporting the workstation.
-   Product support engineer, where support is explicitly authorized.
-   Legal-domain reviewer responsible for benchmark quality.
-   QA and security testers.
-   Client or data controller whose information may appear in case
    files.

## 4.3 User roles for version 1.0

The initial release is single-user, but internal permission concepts
should be designed so they can extend to multi-user deployments later.

  -----------------------------------------------------------------------
  Role                                Capabilities
  ----------------------------------- -----------------------------------
  Local application user              Create matters, import documents,
                                      search, run analysis, review
                                      findings, export reports

  Local device administrator          Install or update software and
                                      manage device-level controls; does
                                      not automatically gain a
                                      product-level right to inspect case
                                      content

  Support personnel                   No default access to case content;
                                      access only through an explicit,
                                      documented, user-authorized process
                                      if support access is ever
                                      implemented
  -----------------------------------------------------------------------

The product MUST NOT introduce hidden remote support access.

------------------------------------------------------------------------

# 5. Assumptions, Constraints, and Dependencies

## 5.1 Assumptions

-   Initial users work primarily on Windows 10/11 64-bit machines.
-   A standard target device has 16 GB RAM and an SSD.
-   Users can supply lawful copies of documents they are authorized to
    process.
-   The first release processes one matter at a time for AI-heavy
    workflows.
-   Model and OCR packages can be provisioned during installation or
    through a separate, verified offline package.
-   Users will review AI-generated findings before relying on them in
    legal work.
-   Lawyers or qualified reviewers can help create evaluation labels for
    a pilot benchmark.

## 5.2 Constraints

-   No external AI API is available or required.
-   Model context and memory are limited by standard hardware.
-   Scanned documents may have poor OCR quality.
-   The application cannot guarantee that all source documents are
    complete, authentic, or accurate.
-   Model-generated conclusions may still be wrong even when citations
    are valid.
-   The software cannot establish legal admissibility or the truth of a
    statement merely from its presence in a document.
-   Legal and privacy obligations depend on the actual deployment, data,
    contractual arrangements, and applicable law.

## 5.3 Dependencies

-   Desktop runtime and packaging toolchain.
-   Python runtime and pinned dependencies.
-   Local inference runtime and compatible model artifacts.
-   PDF/DOCX extraction libraries.
-   Local OCR engine and language data.
-   SQLite and search indexes.
-   Embedding model and optional reranker.
-   Encryption library and operating-system key protection facilities.
-   Test documents and lawyer-reviewed benchmark labels.
-   Legal review of licenses, privacy obligations, professional
    confidentiality, and product claims.

------------------------------------------------------------------------

# 6. Functional Requirements

Each requirement has a stable identifier and a proposed priority. **P0**
means required for the pilot baseline, **P1** means important but can
follow the first usable vertical slice, and **P2** means a later
enhancement.

## 6.1 Matter management

### FR-MAT-001: Create matter --- P0

The application MUST allow the user to create a matter with: - Unique
internal ID. - Matter title. - Optional internal reference. -
Jurisdiction or court field. - Matter category. - Optional party names
and metadata. - Creation and modification timestamps. - Matter status.

The user MUST be able to leave optional metadata blank.

**Acceptance criteria** - A new matter receives a unique stable ID. -
The matter appears in the matter list after restart. - Data from one
matter is not returned when another matter is selected. - Invalid input
is rejected with a clear explanation.

### FR-MAT-002: Edit matter metadata --- P1

The user SHOULD be able to update matter metadata without altering
original documents or historical analysis records.

### FR-MAT-003: Archive matter --- P1

The user SHOULD be able to archive a matter so it no longer appears in
the default active list. Archiving MUST NOT delete documents or indexes.

### FR-MAT-004: Delete matter --- P1

The application SHOULD support explicit deletion after confirmation.
Deletion must cover original files, extracted text, embeddings, indexes,
reports managed by the application, and associated metadata according to
the documented deletion policy.

The application MUST explain whether backups remain and how they are
removed or expire. Deletion must not be represented as complete while
recoverable copies remain in unmanaged backups.

## 6.2 Document import and processing

### FR-DOC-001: Supported file types --- P0

The initial release MUST support: - PDF files. - DOCX files.

Unsupported formats MUST be rejected with a clear message. A file
extension alone MUST NOT be treated as proof of file type.

### FR-DOC-002: Safe import --- P0

The application MUST: - Stage imported files before parsing. - Validate
file signatures and formats. - Enforce configurable file-size and
processing limits. - Generate a SHA-256 hash of the original file. -
Preserve original bytes. - Avoid executing embedded scripts or active
content. - Report import failures. - Prevent imported content from
escaping the authorized data directory.

### FR-DOC-003: Duplicate detection --- P1

The application SHOULD identify byte-identical documents using their
hashes. It MAY suggest possible duplicates based on content, but MUST
NOT merge documents automatically based only on similar text.

### FR-DOC-004: Text extraction --- P0

The application MUST extract text from digitally generated PDFs and DOCX
files while preserving document identity and, where available, page and
paragraph boundaries.

### FR-DOC-005: OCR --- P0

The application MUST detect scanned or text-deficient PDFs and offer
local OCR.

The application MUST store extraction status and available quality
indicators. Low-quality OCR MUST be disclosed to the user.

### FR-DOC-006: Processing status --- P0

Each document MUST have an explicit state, such as: - Imported. -
Queued. - Processing. - Indexed. - Partially processed. - Failed. -
Needs review.

A failed or partially processed document MUST NOT silently appear as
fully indexed.

### FR-DOC-007: Source integrity --- P0

Original files MUST remain unchanged by ingestion and analysis. The
application SHOULD verify stored content against its recorded hash when
integrity checking is requested and during relevant recovery workflows.

### FR-DOC-008: Reprocessing --- P1

The application SHOULD support reprocessing a document after parser or
OCR upgrades. Reprocessing MUST create a versioned processing result and
preserve enough metadata to understand which version was used in earlier
analyses.

## 6.3 Document viewing

### FR-VIEW-001: Open original source --- P0

The user MUST be able to open the original document associated with a
search result or finding.

### FR-VIEW-002: Navigate to source location --- P0

When a source reference includes a page number, the viewer SHOULD open
the correct page. Where coordinates are available, the viewer SHOULD
highlight the relevant passage.

### FR-VIEW-003: Show extraction limitations --- P0

The viewer MUST make relevant extraction warnings visible, including low
OCR quality, missing pages, and unsupported layouts.

### FR-VIEW-004: Preserve original and extracted text distinction --- P0

The application MUST distinguish original source content from OCR text,
normalized text, summaries, and model-generated interpretation.

## 6.4 Search and retrieval

### FR-SEARCH-001: Keyword search --- P0

The user MUST be able to search indexed document text using exact words
and phrases.

### FR-SEARCH-002: Semantic search --- P0

The application MUST support local semantic retrieval for
natural-language queries.

### FR-SEARCH-003: Hybrid retrieval --- P0

The application SHOULD combine keyword and semantic retrieval. Retrieval
MUST preserve source references and apply matter scope before content
reaches the model.

### FR-SEARCH-004: Filters --- P1

The user SHOULD be able to filter by document, document type where
known, date metadata, processing status, and selected matter.

### FR-SEARCH-005: Search result provenance --- P0

Each result MUST identify its document and source location. The result
text MUST be drawn from stored extracted content and MUST NOT be
fabricated by the search layer.

### FR-SEARCH-006: Retrieval benchmark --- P0

The system MUST be evaluated against manually labelled relevant
passages. Initial target: recall@10 of at least 95% on an agreed
answerable benchmark. The test set and query distribution MUST be
documented.

## 6.5 Evidence-grounded question answering

### FR-QA-001: Matter-scoped questions --- P0

The user MUST be able to ask factual questions about the selected
matter.

### FR-QA-002: Evidence-grounded answers --- P0

Answers about case facts MUST be generated from retrieved source
passages. The system MUST distinguish direct source statements from
model inference.

### FR-QA-003: Source citations --- P0

Each material factual claim SHOULD include one or more source
references. References MUST resolve to stored documents and valid
locations.

### FR-QA-004: Abstention --- P0

When relevant evidence is not found or is inadequate, the system MUST
communicate that limitation rather than inventing a fact.

### FR-QA-005: Conflicting evidence --- P0

When retrieved sources disagree, the system MUST present the conflict
rather than silently selecting one source as correct.

### FR-QA-006: Conversation scope --- P0

Conversation context MUST remain associated with the selected matter.
The system MUST NOT retrieve evidence from other matters to answer a
question unless a future, explicitly authorized cross-matter feature is
introduced.

### FR-QA-007: Answer provenance --- P0

Each analysis run MUST retain references to the relevant document
chunks, model version, prompt/workflow version, and validation outcome.

## 6.6 Claims and entity extraction

### FR-EXT-001: Structured claims --- P0

The system MUST be able to extract candidate factual claims from
selected passages into a defined schema.

Each claim SHOULD include: - Claim text. - Claim type. - Speaker,
author, or attributed source if known. - Source document and passage. -
Extraction status. - Uncertainty or ambiguity indicators.

### FR-EXT-002: Entity extraction --- P1

The system SHOULD identify candidate people, organizations, locations,
amounts, and dates.

### FR-EXT-003: Entity resolution --- P1

The system MAY propose that two names refer to the same entity, but
ambiguous matches MUST remain reviewable and MUST NOT be merged without
an auditable decision where the merge affects substantive findings.

### FR-EXT-004: Date precision --- P0

The system MUST distinguish exact dates from approximate dates, date
ranges, and inferred dates. An approximate reference MUST NOT be
converted into an exact date without explicit supporting evidence.

### FR-EXT-005: Source linkage --- P0

Every extracted claim MUST retain one or more source links. Unsupported
claims MUST be marked as unverified or discarded from evidence-backed
output.

## 6.7 Chronology

### FR-CHR-001: Generate chronology --- P0

The system MUST generate a candidate chronology from extracted events in
the selected matter.

### FR-CHR-002: Event provenance --- P0

Every event MUST link to one or more source passages.

### FR-CHR-003: Ambiguous dates --- P0

Events with approximate, conflicting, or missing dates MUST be marked
accordingly. The application MUST NOT create false precision by sorting
ambiguous dates as if they were exact.

### FR-CHR-004: Human editing --- P0

The user MUST be able to edit, accept, reject, or annotate a candidate
event.

### FR-CHR-005: Chronology export --- P1

The user SHOULD be able to export a chronology with source references
and review status.

## 6.8 Discrepancy and contradiction analysis

### FR-CMP-001: Select comparison scope --- P0

The user MUST be able to select two or more documents or a defined set
of claims for comparison.

### FR-CMP-002: Compare claims --- P0

The system MUST identify candidate: - Direct contradictions. -
Differences in dates or amounts. - Differences in attributed
statements. - Omissions that may warrant review. - Ambiguities or
potentially different interpretations. - Agreements or corroborating
statements.

### FR-CMP-003: Explain both sides --- P0

A discrepancy result MUST show the compared claims and their source
passages. It MUST NOT show only a model-written conclusion.

### FR-CMP-004: Avoid overclaiming --- P0

The system MUST distinguish a potential contradiction from a proven
falsehood. It MUST allow the explanation that two statements may refer
to different events, stages, or contexts.

### FR-CMP-005: Review classification --- P0

The user MUST be able to mark a result as: - Accepted for further
consideration. - Rejected. - Needs more evidence. - Ambiguous. -
Corrected. - Irrelevant to the current issue.

These labels are workflow statuses, not legal conclusions.

### FR-CMP-006: Preserve rejected results --- P0

Rejected or corrected findings MUST remain in the analysis history
unless the user explicitly deletes the matter under the documented
retention policy.

## 6.9 Findings review

### FR-REV-001: Review queue --- P0

The application MUST provide a view of findings awaiting review.

### FR-REV-002: Edit and annotate --- P0

The user MUST be able to add notes and correct AI-generated text without
altering the original source material.

### FR-REV-003: Review history --- P0

The system MUST record the finding ID, action, timestamp, and prior/new
value or a secure reference to the change. Audit data SHOULD avoid
copying large passages of confidential content.

### FR-REV-004: AI/human distinction --- P0

The UI MUST distinguish AI-generated suggestions from human-authored
corrections and accepted review outcomes.

## 6.10 Reports and export

### FR-EXP-001: Export evidence report --- P0

The application MUST export a local report in DOCX and/or PDF
containing: - Matter title and export date. - Analysis scope. - Findings
and their review status. - Source references. - Relevant caveats and
extraction warnings. - Model-generated versus human-reviewed content
labels.

### FR-EXP-002: Export confirmation --- P0

The user MUST explicitly initiate an export. The application MUST
confirm the destination and scope before writing the report.

### FR-EXP-003: Export audit --- P0

The application MUST record the export event without unnecessarily
storing the complete report content in the audit log.

### FR-EXP-004: Citation preservation --- P0

Exported source references MUST remain legible and must identify the
underlying document and location.

## 6.11 Model and application configuration

### FR-MOD-001: Local inference --- P0

All model inference required for the core workflow MUST run locally.

### FR-MOD-002: Model manifest --- P0

The application MUST maintain a manifest containing model name, version
or revision, artifact hash, quantization, license information, and
runtime compatibility.

### FR-MOD-003: Resource controls --- P0

The application SHOULD expose safe defaults for context length,
concurrency, and memory usage. It MUST handle inference failures without
corrupting matter data.

### FR-MOD-004: No silent cloud fallback --- P0

If the local model cannot run, the application MUST report the problem.
It MUST NOT silently switch to an external AI service.

------------------------------------------------------------------------

# 7. User Experience Requirements

## 7.1 Primary navigation

The desktop UI SHOULD contain: - Matter list. - Matter overview. -
Documents and processing status. - Search and ask-your-case workspace. -
Chronology. - Evidence comparison. - Findings review queue. -
Export/report view. - Local settings, model status, and privacy
information.

## 7.2 Matter overview

The overview SHOULD show: - Matter title and metadata. - Document count
and processing state. - Documents needing OCR or review. - Recent
analysis runs. - Findings awaiting review. - Links to chronology and
comparison workspaces.

Dashboard counts MUST reflect actual persisted data, not hard-coded
values.

## 7.3 Evidence viewer

The evidence viewer SHOULD provide: - Original document view. - Page
navigation. - Search-result highlighting where feasible. - Source
passage metadata. - Extraction-quality warnings. - A way to copy a
source reference without changing the original file.

## 7.4 Discrepancy table

Each row SHOULD include: - Discrepancy category. - Claim A and source. -
Claim B and source. - Explanation of the difference. - Uncertainty or
limitations. - Review status. - Actions to open sources, annotate,
accept, or reject.

## 7.5 Privacy presentation

The application SHOULD clearly display the current local processing
status and explain what data is stored locally. A visual privacy
indicator MUST NOT imply security certification or substitute for
technical enforcement.

## 7.6 Accessibility and usability

-   Keyboard navigation SHOULD be supported for primary workflows.
-   Text and controls SHOULD remain readable at common desktop scaling
    settings.
-   Long-running tasks MUST show progress and allow safe cancellation.
-   Error messages MUST explain what happened and what the user can do
    next.
-   Destructive actions MUST require explicit confirmation.

------------------------------------------------------------------------

# 8. Technical Architecture

## 8.1 Architecture overview

The product will use a modular monolith with a desktop UI and a local
processing service.

### Desktop layer

-   Tauri shell.
-   React and TypeScript UI.
-   Local navigation and state management.
-   Secure communication with the local service.

### Application service

-   Python and FastAPI.
-   Matter and document APIs.
-   Authorization and scope validation.
-   Workflow orchestration.
-   Export operations.
-   Audit-event generation.

### Document-processing layer

-   PDF text extraction.
-   DOCX parsing.
-   Local OCR.
-   Normalization and chunking.
-   Content hashing and extraction-quality reporting.

### Retrieval layer

-   SQLite FTS5 for keyword search.
-   Local embedding model.
-   FAISS or an equivalent local vector index.
-   Optional local reranker.
-   Matter-scoped retrieval and source mapping.

### Inference layer

-   Local quantized language model.
-   Local embedding model.
-   Optional local reranker.
-   Bounded prompts and structured output validation.

### Persistence layer

-   SQLite metadata database.
-   Application-managed original-file storage.
-   Derived extracted text and indexes.
-   Analysis and review records.
-   Encrypted backups.

## 8.2 Proposed technology stack

  -----------------------------------------------------------------------
  Component               Initial choice          Notes
  ----------------------- ----------------------- -----------------------
  Desktop shell           Tauri                   Package web UI as
                                                  desktop application

  Frontend                React + TypeScript      Case workspace and
                                                  evidence UI

  Local service           Python + FastAPI        Local APIs and
                                                  orchestration

  Database                SQLite                  Single-user local
                                                  persistence

  ORM/migrations          SQLAlchemy + Alembic    Schema and migrations

  PDF processing          PyMuPDF                 Digital PDF extraction
                                                  and page references

  DOCX processing         python-docx             DOCX text and structure

  OCR                     Tesseract or another    Must be packaged with
                          vetted local OCR        required language data
                          pipeline                

  Keyword search          SQLite FTS5             Exact phrase and
                                                  lexical retrieval

  Vector index            FAISS or equivalent     Local semantic
                                                  retrieval

  Inference               llama.cpp or compatible Quantized local models
                          local runtime           

  Validation              Pydantic and            Typed outputs and
                          deterministic checks    reference validation

  Export                  python-docx and a       Local output generation
                          vetted PDF generation   
                          path                    

  Testing                 pytest and frontend     Unit, integration, and
                          test tooling            regression tests
  -----------------------------------------------------------------------

Technology choices MAY change after a proof of concept, but the offline
boundary, provenance requirements, and testable behavior MUST remain.

## 8.3 Process and privilege boundaries

-   The desktop UI MUST NOT have direct unrestricted access to the
    filesystem.
-   The local API MUST bind to loopback only in the single-user build.
-   Local API requests MUST use an authenticated session or equivalent
    protection and validate request origin.
-   Document parsing SHOULD run in a restricted worker process with
    resource limits.
-   The inference runtime SHOULD receive only the model files and input
    data needed for the current task.
-   The AI agent MUST NOT receive unrestricted shell, filesystem, or
    network tools.
-   Application components MUST run without administrator privileges
    unless a specific installation operation requires them.
-   Sensitive values MUST NOT be written to logs or included in
    telemetry.

## 8.4 Model selection

Initial candidates: - An 8B-class instruction model at 4-bit
quantization for the main analysis workflow. - A 4B-class alternative
for lower-memory or slower hardware. - A small multilingual embedding
model. - An optional lightweight reranker.

Exact model versions MUST be selected through evaluation of extraction
accuracy, schema adherence, citation support, English/Hindi performance,
memory, latency, and licensing.

The model MUST NOT be selected solely on generic benchmark scores. The
product SHOULD process documents in bounded batches instead of placing
an entire case into one context window.

## 8.5 Retrieval strategy

The retrieval pipeline SHOULD: 1. Validate the selected matter and
access scope. 2. Run keyword and semantic retrieval. 3. Merge and
deduplicate candidates. 4. Apply a local reranker where enabled. 5.
Assemble a bounded evidence context. 6. Preserve source IDs and
page/paragraph references. 7. Pass only the required evidence to the
model. 8. Validate citations and structured output after generation.

## 8.6 Workflow orchestration

Version 1.0 MUST use a controlled workflow or state machine for evidence
analysis.

The model MAY request an approved tool call. The application MUST
validate the requested action, arguments, scope, and resource budget
before executing it.

Retries MUST be bounded. Failed validation MUST lead to a controlled
retry, a request for more information, or abstention.

------------------------------------------------------------------------

# 9. Agent Tools and Contracts

The agent MUST use a registered set of typed tools. It MUST NOT invent
tools or execute arbitrary code.

## 9.1 Tool registry

  --------------------------------------------------------------------------
  Tool                       Purpose                 Permission
  -------------------------- ----------------------- -----------------------
  `list_case_documents`      List authorized         Read-only
                             documents               

  `search_case_documents`    Retrieve candidate      Read-only
                             passages                

  `get_source_passage`       Fetch exact stored text Read-only
                             and location            

  `extract_claims`           Create provisional      Derived-data write
                             structured claims       

  `normalize_entities`       Propose entity          Derived-data write
                             normalization           

  `build_chronology`         Build candidate events  Derived-data write

  `compare_claims`           Compare claims and flag Derived-data write
                             discrepancies           

  `validate_finding`         Check source references Validation
                             and structural support  

  `save_review_decision`     Save a user review      Human-authorized write
                             action                  

  `export_evidence_report`   Generate an approved    User-authorized output
                             report locally          
  --------------------------------------------------------------------------

## 9.2 Common tool requirements

Every tool MUST: - Validate input against a typed schema. - Validate
matter scope. - Enforce file and result-size limits. - Return structured
errors. - Avoid logging sensitive source content. - Use stable IDs. -
Respect cancellation and time limits. - Avoid external network calls. -
Record a meaningful audit event where appropriate.

## 9.3 Evidence comparison workflow

1.  User selects the matter and documents or claims.
2.  Application validates the selected scope.
3.  Retrieval identifies relevant passages.
4.  Extraction produces candidate claims with source links.
5.  Normalization identifies comparable dates, people, amounts, and
    events.
6.  Comparison identifies possible agreements, contradictions,
    omissions, and ambiguities.
7.  Citation validation checks all source references and quoted
    passages.
8.  The UI presents findings with both sides of the comparison.
9.  The lawyer reviews, corrects, rejects, or annotates the finding.
10. The application records the review decision and workflow version.

## 9.4 Prompt-injection handling

Document content MUST be treated as untrusted data. Text inside a
document MUST NOT be allowed to override system instructions, expand
tool permissions, change matter scope, or authorize data export.

Controls MUST include: - Separation of system instructions from document
content. - Typed tool arguments and application-side validation. - No
arbitrary code execution tools. - Matter-scoped retrieval. - Bounded
context and output size. - Adversarial document tests. - Human approval
for consequential actions.

Prompt instructions alone are not a sufficient security control.

------------------------------------------------------------------------

# 10. Data Model

The database design SHOULD use stable identifiers and explicit
provenance relationships.

## 10.1 Core entities

### `matters`

-   `id`: stable unique ID.
-   `title`.
-   `reference`.
-   `jurisdiction`.
-   `matter_type`.
-   `status`.
-   `created_at`.
-   `updated_at`.

### `documents`

-   `id`.
-   `matter_id`.
-   `original_name`.
-   `storage_key`.
-   `sha256`.
-   `mime_type`.
-   `size_bytes`.
-   `imported_at`.
-   `processing_status`.
-   `parser_version`.
-   `ocr_version`, when applicable.

### `document_pages`

-   `id`.
-   `document_id`.
-   `page_number`.
-   `extracted_text`.
-   `extraction_method`.
-   `quality_indicator`.
-   `processing_status`.

### `chunks`

-   `id`.
-   `document_id`.
-   `page_start`.
-   `page_end`.
-   `paragraph_start`, where available.
-   `paragraph_end`, where available.
-   `text`.
-   `content_hash`.
-   `chunk_index`.
-   `language`, where known.

### `entities`

-   `id`.
-   `matter_id`.
-   `entity_type`.
-   `canonical_label`, if reviewed.
-   `status`.

### `entity_aliases`

-   `id`.
-   `entity_id`.
-   `alias_text`.
-   `source_chunk_id`.
-   `review_status`.

### `claims`

-   `id`.
-   `matter_id`.
-   `claim_text`.
-   `claim_type`.
-   `speaker_entity_id`, where known.
-   `date_value`, where applicable.
-   `date_precision`.
-   `review_status`.
-   `analysis_run_id`.

### `claim_sources`

-   `claim_id`.
-   `chunk_id`.
-   `quote_start` or stored quote reference.
-   `quote_end` or stored quote reference.
-   `evidence_role`.

### `events`

-   `id`.
-   `matter_id`.
-   `event_date`.
-   `date_precision`.
-   `description`.
-   `review_status`.
-   `analysis_run_id`.

### `event_sources`

-   `event_id`.
-   `chunk_id`.
-   `support_type`.

### `findings`

-   `id`.
-   `matter_id`.
-   `analysis_run_id`.
-   `finding_type`.
-   `summary`.
-   `explanation`.
-   `review_status`.
-   `created_at`.

### `finding_sources`

-   `finding_id`.
-   `chunk_id`.
-   `relationship_type`.

### `analysis_runs`

-   `id`.
-   `matter_id`.
-   `workflow_version`.
-   `model_manifest_id`.
-   `prompt_version`.
-   `retrieval_configuration`.
-   `status`.
-   `started_at`.
-   `completed_at`.

### `review_events`

-   `id`.
-   `finding_id` or relevant entity reference.
-   `action`.
-   `previous_value` or secure change reference.
-   `new_value` or secure change reference.
-   `timestamp`.

### `audit_events`

-   `id`.
-   `event_type`.
-   `matter_id`, where relevant.
-   `actor_id`, where relevant.
-   `timestamp`.
-   `metadata`.

## 10.2 Data integrity rules

-   Every document MUST belong to one matter.
-   Every chunk MUST reference a document.
-   Every claim, event, and finding MUST retain source relationships
    when derived from case material.
-   Source IDs MUST be validated before display or export.
-   Foreign-key constraints SHOULD be enabled.
-   Database schema changes MUST use versioned migrations.
-   Derived indexes MUST be rebuildable from source data and metadata.
-   Reprocessing MUST NOT silently rewrite historical analysis results.
-   Dates MUST preserve precision and ambiguity.
-   Review decisions MUST be stored separately from the original AI
    result.

## 10.3 Data storage

Original files, derived text, indexes, and metadata MUST be kept in
controlled application storage. Sensitive databases, extracted text, and
backups MUST be protected using an approved encryption design.

Encryption keys MUST NOT be hardcoded in source code or stored
unprotected beside encrypted data. The product MUST document recovery
implications if a key is lost.

------------------------------------------------------------------------

# 11. Security and Privacy Requirements

## 11.1 Threat model

The design MUST consider: - Accidental upload to cloud services. -
Unexpected telemetry or update checks. - Malware or compromise of the
host operating system. - Malicious or adversarial document content. -
Parser vulnerabilities. - Local API abuse. - Unauthorized access across
matters. - Stolen or copied device storage. - Model or dependency
tampering. - Accidental export to an incorrect destination. - Corruption
or loss of local data. - Sensitive content in logs, crash reports, or
temporary files.

## 11.2 Security requirements

### SEC-001: Offline operation --- P0

All core workflows MUST function with network interfaces disabled.

### SEC-002: No external inference --- P0

The application MUST NOT send case content, prompts, extracted text,
embeddings, model outputs, filenames, or sensitive metadata to external
AI providers.

### SEC-003: Network denial --- P0

The offline release SHOULD be distributed with a documented host
firewall or equivalent policy that denies unnecessary outbound
connections. Offline verification MUST include observation of actual
network activity.

### SEC-004: No telemetry --- P0

The initial offline release MUST NOT use analytics, remote crash
reporting, or usage telemetry that transmits data. Any future opt-in
diagnostic export must be explicit, reviewable, and free of sensitive
content by default.

### SEC-005: Local API protection --- P0

The local API MUST bind to loopback only, use authenticated session
protection, validate request origin, and reject unauthorized requests.
It MUST NOT expose an unauthenticated service to the local network.

### SEC-006: Encryption at rest --- P0

Sensitive databases, files, and backups MUST be encrypted using a vetted
implementation of authenticated encryption. Key management MUST be
reviewed by a security professional.

### SEC-007: Least privilege --- P0

The application MUST NOT require administrator privileges for routine
document analysis. Parsing and inference components SHOULD run with
restricted filesystem permissions.

### SEC-008: Matter isolation --- P0

All data-access operations MUST validate matter scope. Cross-matter
leakage tests MUST pass before pilot release.

### SEC-009: Secure import --- P0

Imported documents MUST be treated as untrusted input. The parser MUST
have resource limits and MUST NOT execute embedded scripts or active
content.

### SEC-010: Secret management --- P0

Keys, credentials, and other secrets MUST NOT be embedded in source
code, model prompts, or logs.

### SEC-011: Dependency security --- P0

Dependencies MUST be pinned and scanned. The release process MUST
include vulnerability review and a documented process for security
updates.

### SEC-012: Auditability --- P0

Important events such as imports, analysis runs, exports, and review
decisions MUST be recorded with timestamps and stable references. Audit
logs MUST avoid unnecessary duplication of confidential material.

### SEC-013: Backup and recovery --- P0

The product MUST support a documented backup and restoration process.
Backup artifacts MUST be encrypted and restoration MUST be tested.

### SEC-014: Deletion --- P1

Deletion workflows MUST address originals, extracted content, indexes,
reports, and application-managed backups. The UI MUST explain any
remaining copies outside the application's control.

### SEC-015: Supply-chain integrity --- P0

Model and installer artifacts MUST have recorded hashes. Signed releases
SHOULD be used. Updates MUST be verified before installation.

## 11.3 Offline update process

Model and application updates MAY be acquired using an authorized
connected machine and transferred to the target device through an
approved process.

The installer or update mechanism MUST verify signatures or hashes
against a trusted manifest. The offline application MUST NOT silently
connect to the internet to check for updates.

## 11.4 India-specific legal review

Before commercial release, qualified Indian counsel MUST review
applicable data-protection obligations, professional confidentiality,
client instructions, contractual duties, software licensing, and
relevant retention or incident-handling requirements.

The applicability and commencement dates of legal provisions MUST be
checked against authoritative current sources. Offline processing
reduces certain risks but does not automatically establish legal
compliance.

------------------------------------------------------------------------

# 12. Non-Functional Requirements

## 12.1 Performance

Initial targets on the agreed 16 GB RAM reference device:

  -----------------------------------------------------------------------
  Operation                           Proposed target
  ----------------------------------- -----------------------------------
  Open matter with local metadata     Under 2 seconds for typical matters

  Search indexed content              Under 3 seconds for typical queries

  First answer to a focused question  15--30 seconds target,
                                      benchmark-dependent

  Import status feedback              Immediate acknowledgement, then
                                      progress updates

  Large-document processing           Asynchronous with progress and
                                      cancellation

  Recovery from a failed analysis     No corruption of original files or
                                      previously saved findings
  -----------------------------------------------------------------------

Targets MUST be validated with a documented reference workload. The
product MUST not conceal slow operations by blocking the entire UI.

## 12.2 Memory and CPU

-   The product MUST support a low-memory inference configuration.
-   The application SHOULD process OCR and inference jobs sequentially
    where needed.
-   Model context length MUST be bounded.
-   The application MUST handle out-of-memory errors gracefully.
-   Indexing MUST NOT require loading every document into RAM
    simultaneously.
-   Resource limits SHOULD be configurable through tested presets rather
    than unrestricted user tuning.

## 12.3 Reliability

-   Interrupted analysis MUST leave source documents intact.
-   Database writes SHOULD be transactional.
-   Failed indexing jobs MUST be recoverable.
-   Application restart MUST restore matter metadata and saved review
    decisions.
-   Repeated execution of the same workflow with the same inputs SHOULD
    be traceable, even where model output is not perfectly
    deterministic.

## 12.4 Maintainability

-   Backend modules MUST have defined responsibilities.
-   API and data schemas MUST be versioned.
-   Database changes MUST use migrations.
-   Model artifacts MUST be versioned and checksummed.
-   Automated tests MUST cover the primary evidence workflow.
-   Architecture and security decisions MUST be documented.

## 12.5 Usability

-   Errors MUST be actionable and understandable.
-   AI-generated content MUST be visually distinguishable from reviewed
    content.
-   Source references MUST be easy to open.
-   Users MUST be able to inspect both sides of a discrepancy.
-   Long-running jobs MUST show progress and support safe cancellation.
-   Destructive actions MUST require confirmation.

## 12.6 Accessibility

The UI SHOULD support keyboard navigation, readable contrast, scalable
text, and understandable focus states. Accessibility testing SHOULD be
included before wider deployment.

------------------------------------------------------------------------

# 13. Evaluation and Quality Assurance

## 13.1 CounselBench benchmark

Create a private evaluation suite of representative, authorized or
appropriately anonymized case bundles. Begin with approximately 30--50
bundles during development and expand as the product matures.

The benchmark SHOULD include: - Digital PDFs and DOCX files. - Scanned
PDFs with varying quality. - English, Hindi, and mixed-language
records. - Similar names and ambiguous entities. - Conflicting and
approximate dates. - Multiple versions of a statement. - Missing
evidence and unanswerable questions. - Irrelevant material and malicious
embedded instructions. - Tables, annexures, rotated pages, and poor
layouts.

Each benchmark case SHOULD include reviewed relevant passages, expected
claims, event/date labels, and discrepancy labels.

The final held-out test set MUST NOT be used for prompt tuning or model
selection.

## 13.2 Quality metrics

  ------------------------------------------------------------------------
  Metric                     Initial proposed target Notes
  --------------------- ---------------------------- ---------------------
  Retrieval recall@10                   At least 95% On answerable,
                                                     labelled queries

  Citation                              At least 98% Valid references do
  source/location                                    not prove
  validity                                           interpretation is
                                                     correct

  Substantive claim                     At least 95% Evaluated against
  support                                            source evidence

  High-priority                         At least 90% Must also measure
  discrepancy precision                              recall

  Critical fabricated                  Zero observed Does not prove zero
  facts                                              risk

  Cross-matter                                  Zero Release blocker
  isolation failures                                 

  Unintended outbound                  Zero observed Under defined offline
  traffic                                            tests

  Defined                                  100% pass All required recovery
  backup/restore                                     scenarios
  scenarios                                          
  ------------------------------------------------------------------------

These are proposed gates. They MUST be reviewed against the risk of the
intended use and the size and composition of the benchmark.

## 13.3 Required test layers

### Unit tests

-   Hashing and integrity.
-   Chunk-to-source mapping.
-   Schema validation.
-   Date precision handling.
-   Citation validation.
-   Matter scope checks.
-   Database constraints.

### Integration tests

-   Import PDF/DOCX.
-   OCR and indexing.
-   Hybrid retrieval.
-   Local inference.
-   Evidence comparison.
-   Review decisions.
-   Report export.
-   Restart and recovery.

### AI regression tests

-   Exact fact retrieval.
-   Cross-document comparison.
-   Ambiguous evidence.
-   Unsupported question abstention.
-   Source quote fidelity.
-   English/Hindi retrieval.
-   Poor OCR.
-   Schema adherence.

### Security tests

-   Network monitoring.
-   Cross-matter access attempts.
-   Local API misuse.
-   Malicious documents.
-   Parser resource exhaustion.
-   Tampered model artifacts.
-   Backup and restore.
-   Log inspection for sensitive data.

### User acceptance tests

Lawyers and legal assistants SHOULD complete defined tasks using
representative files. Evaluation SHOULD measure completion time, missed
findings, false positives, source-verification effort, and user
confidence calibrated against actual correctness.

------------------------------------------------------------------------

# 14. Acceptance Criteria and Definition of Done

A feature is not complete merely because the UI appears to work.

## 14.1 Feature definition of done

A feature is complete when: - Functional requirements are implemented. -
Input validation and error states exist. - Matter scope is enforced. -
Unit and integration tests pass. - Sensitive content is excluded from
logs by default. - Source provenance is retained where applicable. -
Relevant security cases are tested. - Documentation is updated. - The
feature is tested on the target hardware.

## 14.2 Pilot release gate

The pilot release MUST be blocked if any of the following occurs: -
Unintended outbound transmission of case data. - Cross-matter data
leakage. - Unverified citations represented as verified. - Corruption or
loss of original source documents. - Critical security vulnerabilities
remain unresolved. - Core workflows fail with network interfaces
disabled. - Backup restoration fails for required scenarios. - Model or
dependency licensing has not been reviewed. - Legal-domain reviewers
have not assessed the quality and limitations of the benchmark results.

## 14.3 Known limitations

The pilot documentation MUST state that: - AI findings can be wrong. -
OCR may misread scanned or handwritten documents. - Source citations
establish where text was found, not whether the source statement is
true. - Absence of a retrieved result does not prove that evidence is
absent from the case. - Legal relevance and admissibility require
professional judgment. - The application does not independently verify
the authenticity of imported documents. - The first release does not
provide comprehensive legal research or authoritative legal advice.

------------------------------------------------------------------------

# 15. Implementation Plan and Milestones

The following plan assumes a small engineering team or a technically
capable solo developer. It is a planning baseline, not a guarantee of
completion or production readiness.

## Milestone 0: Discovery and validation --- Weeks 1--2

**Deliverables** - Interviews with 5--10 litigation lawyers or legal
assistants. - Defined initial document types and workflows. - Authorized
sample document set. - Initial threat model. - Benchmark annotation
guide. - Model and OCR proof-of-concept comparison. - Product acceptance
criteria reviewed with legal-domain users.

**Exit criteria** - One primary workflow selected. - Test materials and
permissions are documented. - Major privacy and deployment assumptions
are reviewed.

## Milestone 1: Local document foundation --- Weeks 3--4

**Deliverables** - Desktop shell and local backend. - Matter creation. -
PDF/DOCX import. - Hashing and original-file preservation. - Text
extraction and OCR. - Page-level source mapping. - SQLite schema and
migrations. - Processing-status UI.

**Exit criteria** - Representative documents import successfully. -
Original files remain unchanged. - Extraction failures are visible. -
Core processing works offline.

## Milestone 2: Search and evidence Q&A --- Weeks 5--6

**Deliverables** - Chunking pipeline. - FTS5 index. - Local
embeddings. - Hybrid retrieval. - Local model integration. - Typed tool
registry. - Evidence-grounded answer generation. - Citation
validation. - Abstention behavior.

**Exit criteria** - Search results link to the correct source
locations. - Benchmark metrics are measured. - No external inference is
used. - Failure paths are tested.

## Milestone 3: Chronology and discrepancy analysis --- Weeks 7--8

**Deliverables** - Claim extraction. - Entity and date normalization. -
Chronology workflow. - Claim comparison workflow. - Discrepancy table. -
Finding review and annotations. - Versioned analysis records.

**Exit criteria** - Findings include both sides of the comparison. -
Approximate and conflicting dates are represented correctly. - Human
review decisions persist across restart.

## Milestone 4: Security hardening and packaging --- Weeks 9--10

**Deliverables** - Encrypted storage and backup. - Restricted local
API. - Process and filesystem permission controls. - Network-denial
policy and verification. - Dependency and artifact manifests. - Signed
or verified release packages. - Recovery and deletion procedures.

**Exit criteria** - Defined security tests pass. - Network behavior is
observed and documented. - Backup restoration works. - Known security
issues are triaged.

## Milestone 5: Supervised pilot --- Weeks 11--12 and beyond

**Deliverables** - Held-out benchmark report. - Lawyer-reviewed quality
results. - Usability findings. - Performance and memory report. -
Release checklist. - Known-limitations document. - Pilot feedback and
prioritization plan.

**Exit criteria** - Pilot gates are met. - Critical issues are
resolved. - Legal-domain reviewers approve the use of the product in the
defined supervised pilot. - Users receive clear instructions and
limitations.

A production release may require additional time for security review,
reliability improvements, accessibility, support procedures, legal
review, and deployment testing.

------------------------------------------------------------------------

# 16. Repository and Engineering Standards

## 16.1 Proposed repository structure

``` text
counselos/
├── apps/
│   └── desktop/
│       ├── src/
│       │   ├── components/
│       │   ├── features/
│       │   │   ├── matters/
│       │   │   ├── documents/
│       │   │   ├── evidence/
│       │   │   ├── chronology/
│       │   │   └── review/
│       │   └── main.tsx
│       └── src-tauri/
├── backend/
│   ├── api/
│   ├── auth/
│   ├── db/
│   ├── ingestion/
│   ├── retrieval/
│   ├── inference/
│   ├── agents/
│   ├── workflows/
│   ├── security/
│   └── exports/
├── models/
│   └── manifest.json
├── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── counselbench/
├── scripts/
└── docs/
    ├── architecture.md
    ├── threat-model.md
    ├── evaluation-plan.md
    ├── data-retention.md
    └── release-checklist.md
```

## 16.2 Engineering practices

-   Use version control and protected release branches.
-   Pin application dependencies.
-   Keep secrets out of source control.
-   Use automated tests for database migrations.
-   Record model and prompt versions.
-   Maintain a reproducible local development setup.
-   Separate synthetic test fixtures from confidential pilot material.
-   Never put client documents in public issue trackers or build logs.
-   Require review of security-sensitive changes.
-   Maintain a release rollback procedure.

## 16.3 Observability without telemetry

The offline application MAY provide a local diagnostic view
containing: - Processing status. - Job duration. - Model and parser
versions. - Resource usage. - Error codes. - Indexing failures. -
Validation outcomes.

Diagnostic data MUST remain local unless the user explicitly exports a
reviewed diagnostic package. Confidential document text MUST NOT be
included by default.

------------------------------------------------------------------------

# 17. Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                    Impact                  Mitigation
  ----------------------- ----------------------- -----------------------
  Small model misses      High                    Hybrid retrieval,
  relevant evidence                               bounded workflows,
                                                  lawyer review,
                                                  benchmark testing

  Poor OCR creates false  High                    OCR quality indicators,
  facts                                           source viewer,
                                                  extraction warnings,
                                                  scanned-document
                                                  testing

  False-positive          High                    Show both sources,
  contradictions                                  distinguish categories,
                                                  measure precision and
                                                  recall

  Citation points to      High                    Stable source mapping
  wrong page                                      and automated
                                                  validation

  Prompt injection in     High                    Treat document text as
  documents                                       untrusted, restrict
                                                  tools, validate all
                                                  calls

  Data leakage through    Critical                Network denial, traffic
  local app behavior                              tests, no telemetry,
                                                  independent review

  Device theft or         High                    Encryption, OS
  compromise                                      security, least
                                                  privilege, backup and
                                                  recovery

  Model is too slow on    Medium/High             Quantized fallback
  standard hardware                               model, bounded context,
                                                  sequential processing

  Licensing prevents      High                    Review model and
  commercial distribution                         dependency licenses
                                                  before packaging

  Legal users over-trust  High                    Clear status labels,
  AI output                                       source-first UI,
                                                  abstention, training
                                                  and warnings

  Scope expands before    High                    Freeze MVP scope and
  core quality is proven                          require benchmark-based
                                                  prioritization

  Pilot documents contain High                    Authorized access, data
  sensitive personal data                         minimization, retention
                                                  policy, secure storage
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 18. Product Roadmap After Version 1.0

Potential enhancements, subject to separate discovery and security
review:

### Version 1.1

-   Improved DOCX and table handling.
-   Better source highlighting.
-   More robust OCR and mixed-language retrieval.
-   More flexible chronology filters.
-   Additional report templates.

### Version 1.2

-   Lawyer-reviewed drafting workflows.
-   Matter templates.
-   Better entity resolution.
-   Redaction and controlled report-sharing features.
-   Expanded benchmark coverage.

### Version 2.0

-   Managed on-premises deployment.
-   Multi-user authentication and matter permissions.
-   Administrator-managed policies.
-   Licensed, versioned legal research corpus.
-   Controlled integrations with firm systems.

A future on-premises or multi-user deployment requires new requirements
for authentication, authorization, concurrent access, backup,
administrator privileges, auditing, and network security. It MUST NOT be
treated as a simple packaging change.

------------------------------------------------------------------------

# 19. Open Decisions

These decisions should be resolved before the implementation baseline is
frozen.

  -----------------------------------------------------------------------
  Decision                Recommended default     Decision owner
  ----------------------- ----------------------- -----------------------
  Initial operating       Windows 10/11 64-bit    Product / Engineering
  system                                          

  Primary model           Selected through        AI Engineering
                          CounselBench            

  OCR engine              Local OCR chosen after  Engineering
                          scanned-document        
                          evaluation              

  Vector index            FAISS with stable chunk AI Engineering
                          mapping                 

  Encryption approach     Vetted library and      Security
                          OS-supported key        
                          protection              

  Local API               Authenticated local     Security / Engineering
  authentication          session plus origin     
                          validation              

  Backup destination      User-selected local or  Product / Security
                          approved encrypted      
                          external storage        

  Retention policy        Configurable and        Product / Legal
                          documented; no silent   
                          deletion                

  Pilot document set      Authorized or           Legal-domain reviewer
                          appropriately           
                          anonymized materials    

  Release thresholds      Proposed targets        Product / QA / Legal
                          validated against risk  
                          and benchmark size      

  Commercial model        Verified before         Legal / Product
  licenses                packaging               
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 20. Glossary

**Matter:** A legal case or other defined body of legal work managed in
CounselOS.

**Source passage:** A segment of extracted text mapped to a specific
original document location.

**Claim:** A candidate factual assertion attributed to a person,
document, or other source.

**Event:** A candidate occurrence with a description, date or date
range, and source evidence.

**Finding:** An AI-generated or subsequently reviewed observation, such
as a potential discrepancy.

**Provenance:** The relationship between a claim or finding and the
original evidence from which it was derived.

**Hybrid retrieval:** A search method combining lexical and semantic
retrieval.

**Abstention:** A deliberate response that evidence is insufficient to
support an answer.

**Local inference:** Model execution on the user's device rather than
through an external inference service.

**Air-gapped operation:** Operation on a device or environment isolated
from external networks.

**Prompt injection:** Untrusted content attempting to manipulate model
instructions or tool behavior.

**Recall@10:** The proportion of known relevant results found within the
top ten retrieved items.

**Citation validity:** Whether a reference resolves to the correct
source and location. This does not, by itself, establish that the
associated conclusion is correct.

------------------------------------------------------------------------

# 21. Final Product Definition

CounselOS version 1.0 is a single-user, offline-first desktop
application for Indian litigation professionals. It imports PDF and DOCX
case materials, extracts and indexes them locally, retrieves source
passages, answers factual questions with citations, constructs candidate
chronologies, compares claims across documents, and presents potential
discrepancies for human review.

The product's core promise is:

> **Your case files stay under your control. Every important finding can
> be traced back to its source. The lawyer remains in charge.**

The first release succeeds when it can demonstrate that promise on
representative legal documents, on standard hardware, with measurable
evidence quality and verified offline behavior.

That is the baseline against which features, implementation choices, and
future expansion should be judged.
