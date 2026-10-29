from backend.ingestion.chunker import chunk_pages, PageResult


def test_basic_chunking():
    pages = [
        PageResult(
            page_number=1,
            text="This is a test sentence. Another sentence here. " * 20,
            extraction_method="digital",
            quality_indicator=100.0,
        )
    ]

    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.text
        assert chunk.page_start == 1
        assert chunk.page_end == 1
        assert len(chunk.content_hash) == 64


def test_multi_page_chunking():
    pages = [
        PageResult(
            page_number=i,
            text=f"Page {i} content. " * 30,
            extraction_method="digital",
            quality_indicator=100.0,
        )
        for i in range(1, 4)
    ]

    chunks = chunk_pages(pages, chunk_size=300, chunk_overlap=50)
    assert len(chunks) > 0

    page_starts = {c.page_start for c in chunks}
    assert 1 in page_starts


def test_empty_pages():
    pages = []
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=50)
    assert len(chunks) == 0


def test_chunk_index_sequential():
    pages = [
        PageResult(
            page_number=1,
            text="Word " * 500,
            extraction_method="digital",
            quality_indicator=100.0,
        )
    ]

    chunks = chunk_pages(pages, chunk_size=100, chunk_overlap=20)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(indices)))
