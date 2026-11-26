"""Wspólna obsługa dokumentów Word, w tym szablonów .dotx."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

TEMPLATE_TYPE = b"wordprocessingml.template.main+xml"
DOCUMENT_TYPE = b"wordprocessingml.document.main+xml"


def open_document(path: str | Path):
    """Otwiera .docx albo .dotx. Plik szablonu pozostaje bez zmian."""
    from docx import Document

    path = Path(path)
    if path.suffix.lower() != ".dotx":
        return Document(str(path))
    buffer = io.BytesIO()
    with zipfile.ZipFile(path) as source, zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(TEMPLATE_TYPE, DOCUMENT_TYPE)
            target.writestr(item, data)
    buffer.seek(0)
    return Document(buffer)
