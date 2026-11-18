# Obsługa plików .docx — wykrywanie środowiska i wybór biblioteki

Instrukcja obowiązuje zawsze, gdy skill lub agent musi **odczytać lub wygenerować plik `.docx`/`.dotx`**.  
Cel: deterministyczny wybór biblioteki w każdej sesji, niezależnie od środowiska.

---

## Krok 1 — Wykrywanie dostępnych bibliotek (wykonaj zawsze jako pierwszy krok)

Uruchom poniższy snippet za pomocą narzędzia `execute` (Python). Wynik zachowaj — decyzja z kroku 2 opiera się wyłącznie na nim.

```python
import sys, importlib

libs = {
    "python-docx": "docx",
    "docx2txt":    "docx2txt",
    "mammoth":     "mammoth",
    "pypandoc":    "pypandoc",
}

available = []
for name, module in libs.items():
    try:
        importlib.import_module(module)
        available.append(name)
    except ImportError:
        pass

print("DOCX_ENV:")
for lib in available:
    print(f"  AVAILABLE: {lib}")
if not available:
    print("  NONE")
print(f"  PYTHON: {sys.version.split()[0]}")
```

**Wynik przykładowy:**
```
DOCX_ENV:
  AVAILABLE: python-docx
  AVAILABLE: docx2txt
  PYTHON: 3.11.4
```

Jeśli `execute` jest niedostępny lub blokowany — przejdź bezpośrednio do [Trybu bezpiecznego](#tryb-bezpieczny--markdown).

---

## Krok 2 — Hierarchia wyboru biblioteki

Wybierz pierwszą bibliotekę z listy, która jest `AVAILABLE`. Kolejność jest stała — nie zmieniaj jej między wywołaniami w tej samej sesji.

| Priorytet | Biblioteka | Możliwości | Użyj gdy |
|---|---|---|---|
| **1** | `python-docx` | Pełny odczyt i zapis `.docx` — style, tabele, nagłówki/stopki, pola | zawsze preferowana |
| **2** | `mammoth` | Konwersja `.docx` → HTML/Markdown — utrata stylów, dobra do odczytu treści | brak python-docx, tylko odczyt |
| **3** | `docx2txt` | Ekstrakcja tekstu z `.docx` — brak struktury, tylko tekst | brak obu powyższych, tylko odczyt |
| **4** | `pypandoc` | Konwersja przez Pandoc (wymaga zainstalowanego Pandoc w PATH) | zapis do `.docx` gdy brak python-docx |
| **fallback** | Markdown | Zapis do `.md` zamiast `.docx` | żadna biblioteka niedostępna |

> [!IMPORTANT]
> Wybrany priorytet obowiązuje **przez całą sesję**. Jeśli w kroku 3 pojawi się błąd biblioteki — przejdź do kolejnej w hierarchii i poinformuj użytkownika.

---

## Krok 3 — Instrukcje dla każdej biblioteki

### python-docx (priorytet 1 — domyślna)

**Odczyt szablonu:**
```python
from docx import Document

doc = Document("szablon.docx")

# Nagłówki (style)
for para in doc.paragraphs:
    if para.style.name.startswith("Heading"):
        print(f"[{para.style.name}] {para.text}")

# Tabele
for i, table in enumerate(doc.tables):
    print(f"Tabela {i}: {len(table.rows)} wierszy x {len(table.columns)} kolumn")

# Nagłówki/stopki sekcji
for section in doc.sections:
    print("Header:", section.header.paragraphs[0].text if section.header.paragraphs else "brak")
```

**Szablon `.dotx`:** `Document()` odrzuca ten typ pliku. Otwórz kopię w pamięci, a wynik zapisz jako `.docx`:
```python
import io, zipfile
from docx import Document

def open_template(path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(path) as source, zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(b"wordprocessingml.template.main+xml", b"wordprocessingml.document.main+xml")
            target.writestr(item, data)
    buffer.seek(0)
    return Document(buffer)
```

**Zapis dokumentu:** nie przypisuj `para.text`, bo usuwa to formatowanie fragmentów tekstu.
```python
from docx import Document

def fill_placeholders(doc, values):
    """Zastępuje placeholdery w treści, tabelach, nagłówkach i stopkach, zachowując formatowanie."""
    def paragraphs(container):
        yield from container.paragraphs
        for table in container.tables:
            for row in table.rows:
                for cell in row.cells:
                    yield from paragraphs(cell)

    def replace(paragraph, key, value):
        offset = 0
        while True:
            runs = paragraph.runs
            start = "".join(run.text for run in runs).find(key, offset)
            if start < 0:
                return
            end, position, first = start + len(key), 0, True
            for run in runs:
                run_start, run_end = position, position + len(run.text)
                position = run_end
                if run_end <= start or run_start >= end:
                    continue
                before = run.text[:max(start - run_start, 0)]
                after = run.text[end - run_start:] if run_end > end else ""
                run.text = before + (value if first else "") + after
                first = False
            offset = start + len(value)

    containers = [doc]
    for section in doc.sections:
        containers += [section.header, section.footer, section.first_page_header,
                       section.first_page_footer, section.even_page_header, section.even_page_footer]
    for container in containers:
        for paragraph in paragraphs(container):
            for key, value in values.items():
                replace(paragraph, key, value)

# Otwórz szablon użytkownika jako bazę (zachowuje style, logo, stopki)
doc = Document("szablon-uzytkownika.docx")
fill_placeholders(doc, {"[WPISZ TUTAJ]": "Nowa treść"})
doc.save("wynik.docx")
```

---

### mammoth (priorytet 2 — odczyt/analiza)

```python
import mammoth

with open("szablon.docx", "rb") as f:
    result = mammoth.convert_to_markdown(f)
    print(result.value)       # treść w Markdown
    print(result.messages)    # ostrzeżenia o utraconych elementach
```

> [!NOTE]
> mammoth traci style, nagłówki/stopki i formatowanie tabel. Użyj tylko do odczytu treści gdy python-docx jest niedostępny. Wynik zapisz jako `.md`.

---

### docx2txt (priorytet 3 — tylko tekst)

```python
import docx2txt

text = docx2txt.process("szablon.docx")
print(text)
```

> [!NOTE]
> docx2txt zwraca surowy tekst bez struktury. Użyj tylko gdy potrzebny jest sam tekst (np. do analizy treści, nie do regeneracji dokumentu).

---

### pypandoc (priorytet 4 — konwersja przez Pandoc)

```python
import pypandoc

# Markdown → docx (wymaga Pandoc w PATH)
pypandoc.convert_text(
    markdown_content,
    "docx",
    format="md",
    outputfile="wynik.docx",
    extra_args=["--reference-doc=szablon.docx"]  # zachowaj style szablonu
)
```

Sprawdź dostępność Pandoc przed wywołaniem:
```python
import shutil
pandoc_ok = shutil.which("pandoc") is not None
print("Pandoc:", "OK" if pandoc_ok else "BRAK")
```

---

## Tryb bezpieczny — Markdown

Gdy żadna biblioteka nie jest dostępna lub `execute` jest zablokowany:

1. Generuj dokument jako **Markdown** (`.md`) z pełną strukturą (nagłówki `#`, tabele, listy).
2. Poinformuj użytkownika jednym zdaniem: *„Biblioteki .docx niedostępne — generuję dokument w formacie Markdown. Aby uzyskać .docx zainstaluj `python-docx` (`pip install python-docx`)."*
3. Nie próbuj emulować `.docx` przez tekst — Markdown jest pełnowartościowym formatem.

---

## Zasady sesji (ważne dla spójności)

- **Wykrywaj raz na początku sesji** — nie powtarzaj wykrywania przy każdym pliku.
- **Nie zgaduj** które biblioteki są dostępne — wynik z kroku 1 jest jedynym źródłem prawdy.
- **Informuj o wyborze** jedną linią w odpowiedzi: *„Używam: python-docx (dostępna w środowisku)."* lub *„Używam: tryb Markdown (brak bibliotek docx)."*
- **Nie mieszaj bibliotek** w jednej sesji — jeśli otworzyłeś plik z `python-docx`, zapisz nim też wynik.
- Jeśli użytkownik poprosi o konkretną bibliotekę, użyj jej o ile jest `AVAILABLE`; w przeciwnym razie poinformuj i użyj kolejnej w hierarchii.

---

## Szybka instalacja (dla użytkownika)

```bash
# Minimalna (pełny odczyt i zapis .docx)
pip install python-docx

# Pełen zestaw
pip install python-docx mammoth docx2txt

# Z Pandoc (opcjonalnie)
# Windows: winget install JohnMacFarlane.Pandoc
# macOS:   brew install pandoc
# Linux:   sudo apt install pandoc
pip install pypandoc
```
