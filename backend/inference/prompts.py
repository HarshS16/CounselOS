SYSTEM_PREAMBLE = (
    "You are CounselOS, a legal evidence analysis assistant. "
    "You MUST follow these rules:\n"
    "1. Base every statement strictly on the provided source passages.\n"
    "2. Cite sources using [DOC-{document_id}, Page {page}] format.\n"
    "3. If the evidence is insufficient, say so explicitly — never fabricate facts.\n"
    "4. Distinguish direct quotes from your own inferences.\n"
    "5. When sources conflict, present BOTH sides with their citations.\n"
    "6. Express uncertainty when the evidence is ambiguous.\n"
)


def build_qa_prompt(question: str, context_passages: list[dict]) -> str:
    passages_text = _format_passages(context_passages)

    return (
        f"{SYSTEM_PREAMBLE}\n"
        "---\n"
        "EVIDENCE PASSAGES:\n\n"
        f"{passages_text}\n"
        "---\n\n"
        f"QUESTION: {question}\n\n"
        "INSTRUCTIONS:\n"
        "- Answer the question based ONLY on the evidence passages above.\n"
        "- Cite every factual claim with [DOC-<id>, Page <number>].\n"
        "- If the passages do not contain enough information, state: "
        "\"Insufficient evidence in the provided documents to answer this question.\"\n"
        "- If passages contradict each other, present both accounts with citations.\n"
        "- Do NOT add information from outside the provided passages.\n\n"
        "ANSWER:\n"
    )


def build_extraction_prompt(text: str, document_id: str = "", page_number: int = 0) -> str:
    return (
        f"{SYSTEM_PREAMBLE}\n"
        "---\n"
        f"SOURCE TEXT (Document: {document_id}, Page: {page_number}):\n\n"
        f"{text}\n\n"
        "---\n\n"
        "Extract all factual claims, dates, people, organizations, locations, "
        "and monetary amounts from the source text above.\n\n"
        "Return a JSON object with this structure:\n"
        "{\n"
        '  "claims": [\n'
        "    {\n"
        '      "claim_text": "the factual assertion",\n'
        '      "claim_type": "factual_assertion|temporal_claim|financial_claim|attribution|legal_assertion|other",\n'
        '      "speaker": "name of person making the claim, or null",\n'
        '      "date_value": "YYYY-MM-DD or descriptive date string, or null",\n'
        '      "date_precision": "exact|approximate|range|inferred|unknown",\n'
        '      "quote": "exact text from source supporting this claim",\n'
        '      "uncertainty": "note about ambiguity, or null"\n'
        "    }\n"
        "  ],\n"
        '  "entities": [\n'
        "    {\n"
        '      "name": "entity name as it appears",\n'
        '      "type": "person|organization|location|amount|date|other",\n'
        '      "context": "brief description of role or relevance"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Include ONLY claims present in the source text.\n"
        "- Preserve the original wording in quotes.\n"
        "- Mark approximate or unclear dates with the appropriate precision.\n"
        "- Do NOT invent claims or entities not in the text.\n\n"
        "JSON:\n"
    )


def build_chronology_prompt(claims: list[dict]) -> str:
    claims_text = ""
    for i, c in enumerate(claims, 1):
        claims_text += (
            f"Claim {i}:\n"
            f"  Text: {c.get('claim_text', '')}\n"
            f"  Date: {c.get('date_value', 'unknown')}\n"
            f"  Precision: {c.get('date_precision', 'unknown')}\n"
            f"  Source: DOC-{c.get('document_id', '?')}, Page {c.get('page_number', '?')}\n"
            f"  Chunk: {c.get('chunk_id', '?')}\n\n"
        )

    return (
        f"{SYSTEM_PREAMBLE}\n"
        "---\n"
        "EXTRACTED CLAIMS:\n\n"
        f"{claims_text}"
        "---\n\n"
        "Build a chronological timeline of events from these claims.\n\n"
        "Return a JSON array of events:\n"
        "[\n"
        "  {\n"
        '    "event_date": "YYYY-MM-DD or descriptive string",\n'
        '    "date_precision": "exact|approximate|range|inferred|unknown",\n'
        '    "description": "what happened",\n'
        '    "source_claims": [claim numbers that support this event],\n'
        '    "source_chunk_ids": ["chunk_id1", "chunk_id2"],\n'
        '    "uncertainty": "note if date or event is uncertain, or null"\n'
        "  }\n"
        "]\n\n"
        "Rules:\n"
        "- Only create events supported by the claims above.\n"
        "- Do NOT convert approximate dates into exact ones.\n"
        "- Flag conflicting dates from different sources.\n"
        "- Sort by date where possible; place undated events at the end.\n\n"
        "JSON:\n"
    )


def build_comparison_prompt(claims_a: list[dict], claims_b: list[dict]) -> str:
    side_a = _format_claims_for_comparison(claims_a, "A")
    side_b = _format_claims_for_comparison(claims_b, "B")

    return (
        f"{SYSTEM_PREAMBLE}\n"
        "---\n"
        "DOCUMENT A CLAIMS:\n\n"
        f"{side_a}\n"
        "DOCUMENT B CLAIMS:\n\n"
        f"{side_b}\n"
        "---\n\n"
        "Compare the claims from Document A and Document B. Identify:\n"
        "1. Direct contradictions\n"
        "2. Differences in dates or amounts\n"
        "3. Differences in attributed statements\n"
        "4. Omissions (claims in one document not addressed in the other)\n"
        "5. Ambiguities or different interpretations\n"
        "6. Agreements or corroborating statements\n\n"
        "Return a JSON array of findings:\n"
        "[\n"
        "  {\n"
        '    "finding_type": "contradiction|date_discrepancy|amount_discrepancy|'
        'attribution_difference|omission|ambiguity|corroboration",\n'
        '    "summary": "one-line description of the discrepancy or agreement",\n'
        '    "explanation": "detailed explanation showing both sides",\n'
        '    "claim_a": "text of claim from Document A, or null if omission",\n'
        '    "claim_a_index": claim_number_or_null,\n'
        '    "claim_b": "text of claim from Document B, or null if omission",\n'
        '    "claim_b_index": claim_number_or_null,\n'
        '    "uncertainty": "note about why this might not be a true discrepancy, or null"\n'
        "  }\n"
        "]\n\n"
        "Rules:\n"
        "- A potential contradiction is NOT a proven falsehood.\n"
        "- Two statements may refer to different events or contexts.\n"
        "- Show BOTH sides of every comparison.\n"
        "- Do NOT fabricate claims not present in the source material.\n\n"
        "JSON:\n"
    )


def build_summary_prompt(text: str) -> str:
    return (
        f"{SYSTEM_PREAMBLE}\n"
        "---\n"
        f"SOURCE TEXT:\n\n{text}\n\n"
        "---\n\n"
        "Provide a concise summary of the key facts in this text.\n"
        "- State only what is explicitly in the text.\n"
        "- Note any dates, amounts, or named parties.\n"
        "- Flag anything that is ambiguous or unclear.\n"
        "- Do NOT add information not present in the source.\n\n"
        "SUMMARY:\n"
    )


def _format_passages(passages: list[dict]) -> str:
    parts: list[str] = []
    for p in passages:
        doc_id = p.get("document_id", "unknown")
        doc_name = p.get("document_name", "unknown")
        page = p.get("page_number", "?")
        text = p.get("text", "")
        chunk_id = p.get("chunk_id", "")
        quality = p.get("quality_indicator")

        header = f"[DOC-{doc_id}, Page {page}] (File: {doc_name}, Chunk: {chunk_id})"
        if quality is not None and quality < 60:
            header += " ⚠ LOW OCR QUALITY"

        parts.append(f"{header}\n{text}\n")
    return "\n".join(parts)


def _format_claims_for_comparison(claims: list[dict], label: str) -> str:
    parts: list[str] = []
    for i, c in enumerate(claims, 1):
        parts.append(
            f"{label}-{i}: {c.get('claim_text', '')}\n"
            f"  Source: DOC-{c.get('document_id', '?')}, Page {c.get('page_number', '?')}\n"
            f"  Date: {c.get('date_value', 'N/A')} ({c.get('date_precision', 'unknown')})\n"
        )
    return "\n".join(parts)
