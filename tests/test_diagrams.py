"""Testy Documentation Diagrams Engine i słownika statusów skilla client-pt-prd-writer.
Uruchom: python -m unittest tests/test_diagrams.py
"""
import importlib.util
import re
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "client-pt-prd-writer"
FIXTURES = ROOT / "tests" / "fixtures" / "diagrams"
sys.path.insert(0, str(SKILL / "scripts"))

import check_status_labels as labels  # noqa: E402
import diagram_core as core  # noqa: E402
import generate_diagram as gen  # noqa: E402
import insert_diagrams as ins  # noqa: E402
import validate_diagram as val  # noqa: E402

HAS_DOCX = importlib.util.find_spec("docx") is not None


def fixture(name):
    return core.load_model(next(FIXTURES.glob(f"{name}-*.yaml")))


def tiny_png(path, width=2400, height=1200):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    raw = zlib.compress(b"".join(b"\x00" + b"\xff" * 3 for _ in range(1)))
    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")
    # Deklarowany rozmiar jest podmieniany, bo testy sprawdzają tylko skalowanie w dokumencie.
    png = png[:16] + struct.pack(">II", width, height) + png[24:]
    path.write_bytes(png)


class TestModel(unittest.TestCase):

    def test_all_fixture_models_render_without_issues(self):
        for path in sorted(FIXTURES.glob("D-*.yaml")):
            model = core.load_model(path)
            self.assertEqual(core.validate_model(model), [], path.name)
            canvas, issues = gen.render(model)
            self.assertEqual(issues, [], path.name)
            svg = canvas.to_svg(model)
            self.assertIn('role="img"', svg)
            self.assertIn("<title", svg)
            self.assertIn("<desc", svg)

    def test_skill_template_model_is_valid(self):
        model = core.load_model(SKILL / "templates" / "diagram-model.yaml")
        self.assertEqual(core.validate_model(model), [])
        self.assertEqual(gen.render(model)[1], [])

    def test_every_declared_type_has_a_layout(self):
        declared = {t for types, _ in gen.LAYOUTS for t in types}
        self.assertEqual(declared, core.DIAGRAM_TYPES)

    def test_element_without_source_is_rejected(self):
        model = fixture("D-01")
        del model["nodes"][0]["source"]
        self.assertTrue(any("source" in e for e in core.validate_model(model)))

    def test_unknown_direction_is_not_drawn(self):
        model = fixture("D-01")
        model["connections"][0]["direction"] = "unknown"
        self.assertTrue(any("remarks" in e for e in core.validate_model(model)))

    def test_only_confirmed_elements_can_be_drawn(self):
        for ref in ("OPEN-001", "ASSUMPTION-001"):
            model = fixture("D-01")
            model["nodes"][0]["source"] = ref
            self.assertTrue(any("remarks" in e for e in core.validate_model(model)), ref)

    def test_uncertain_wording_is_rejected_on_image(self):
        for text in ("DO POTWIERDZENIA", "Do ustalenia", "termin do uzgodnienia", "Nieokreślony system", "TBD"):
            model = fixture("D-01")
            model["nodes"][0]["label"] = text
            self.assertTrue(core.validate_model(model), text)

    def test_image_has_no_uncertainty_styling_or_remarks(self):
        for name in ("D-06", "D-07"):
            model = fixture(name)
            self.assertEqual(core.validate_model(model), [], name)
            canvas, issues = gen.render(model)
            self.assertEqual(issues, [], name)
            svg = canvas.to_svg(model).casefold()
            self.assertNotIn("stroke-dasharray", svg)
            self.assertNotIn("do potwierdzenia", svg)
            self.assertNotIn("materiały nie", svg)

    def test_missing_direction_cannot_hide_as_none(self):
        model = fixture("D-01")
        model["connections"][0]["direction"] = "none"
        self.assertTrue(any("remarks" in e for e in core.validate_model(model)))

    def test_tbd_label_is_rejected(self):
        model = fixture("D-01")
        model["nodes"][0]["label"] = "TBD"
        self.assertTrue(core.validate_model(model))

    def test_final_mode_rejects_working_markers_in_remarks(self):
        model = fixture("D-07")
        self.assertEqual(core.validate_model(model, "final"), [])
        model["remarks"][0]["text"] = "Termin DO POTWIERDZENIA"
        self.assertTrue(core.validate_model(model, "final"))

    def test_confirmed_model_is_clean_in_final_mode(self):
        model = fixture("D-01")
        self.assertEqual(core.validate_model(model, "final"), [])
        self.assertNotRegex(gen.render(model)[0].to_svg(model), r"(SRC|OPEN|ASSUMPTION)-\d{3}")

    def test_node_missing_from_document_is_reported(self):
        model = fixture("D-01")
        model["nodes"].append({"id": "x", "label": "Serwer OAuth2", "type": "service", "source": "SRC-001"})
        text = (FIXTURES / "document.md").read_text(encoding="utf-8")
        self.assertTrue(any("Serwer OAuth2" in e for e in val.check_against_document(model, text, "working")))

    def test_oversized_diagram_is_refused_not_degraded(self):
        model = fixture("D-01")
        model["groups"] = []
        model["nodes"] = [{"id": f"n{i}", "label": f"Komponent numer {i}", "type": "service", "source": "SRC-001"}
                          for i in range(12)]
        model["connections"] = []
        _canvas, issues = gen.render(model)
        self.assertTrue(any("podziel" in i for i in issues))

    def test_dense_diagram_with_cycle_and_long_edges_stays_valid(self):
        model = fixture("D-02")
        model["connections"] += [
            {"from": "o", "to": "v", "label": "Ponowna weryfikacja", "source": "SRC-001"},
            {"from": "s", "to": "k", "label": "Wycofanie", "source": "SRC-001"},
        ]
        self.assertEqual(gen.render(model)[1], [])

    def test_themes_and_brand_keep_contrast(self):
        for theme in sorted(core.THEMES):
            model = deepcopy(fixture("D-01"))
            model["output"] = {"theme": theme, "accent": "#FFD9D0"}
            self.assertEqual(val.check_theme(model), [], theme)
            self.assertEqual(gen.render(model)[1], [], theme)


class TestMarkdownIntegration(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.dir = self.tmp / "diagrams"
        for name in ("D-01", "D-02"):
            path = next(FIXTURES.glob(f"{name}-*.yaml"))
            self.assertEqual(gen.generate(path, self.dir, "working", None), [])
        self.doc = self.tmp / "doc.md"
        shutil.copyfile(FIXTURES / "document.md", self.doc)

    def run_insert(self):
        return ins.insert_markdown(self.doc, self.dir, self.doc, ins.load_models(self.dir))

    def test_diagram_follows_first_discussion_with_relative_path(self):
        self.run_insert()
        text = self.doc.read_text(encoding="utf-8")
        self.assertLess(text.index("Platforma ACME obejmuje"), text.index("Rysunek 1 przedstawia"))
        self.assertLess(text.index("*Rysunek 1."), text.index("### Odpowiedzialności"))
        self.assertIn("](diagrams/D-01-architecture.svg)", text)
        self.assertNotIn("<svg", text)

    def test_reinsertion_is_idempotent(self):
        self.run_insert()
        first = self.doc.read_bytes()
        self.run_insert()
        self.assertEqual(first, self.doc.read_bytes())

    def test_removing_a_diagram_renumbers_the_rest(self):
        self.run_insert()
        for path in self.dir.glob("D-01-*"):
            path.unlink()
        self.run_insert()
        text = self.doc.read_text(encoding="utf-8")
        self.assertNotIn("D-01-architecture", text)
        self.assertIn("*Rysunek 1. Przebieg obsługi reklamacji", text)

    def test_document_without_diagrams_is_unchanged(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        before = self.doc.read_bytes()
        ins.insert_markdown(self.doc, empty, self.doc, ins.load_models(empty))
        self.assertEqual(before, self.doc.read_bytes())

    def test_missing_section_is_an_error_not_an_append(self):
        model = fixture("D-01")
        model["placement"] = {"section": "Sekcja nieistniejąca"}
        with self.assertRaises(ValueError):
            ins.md_anchor(self.doc.read_text(encoding="utf-8").split("\n"), model)


@unittest.skipUnless(HAS_DOCX, "python-docx niedostępny")
class TestDocxIntegration(unittest.TestCase):

    def setUp(self):
        from docx import Document
        from docx.shared import Cm
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.dir = self.tmp / "diagrams"
        self.dir.mkdir()
        for name in ("D-01", "D-02"):
            path = next(FIXTURES.glob(f"{name}-*.yaml"))
            model = core.load_model(path)
            shutil.copyfile(path, self.dir / f"{gen.base_name(model)}.yaml")
            tiny_png(self.dir / f"{gen.base_name(model)}.png")
        doc = Document()
        section = doc.sections[0]
        section.left_margin = section.right_margin = Cm(4)
        section.header.paragraphs[0].text = "Nagłówek klienta"
        doc.add_heading("2. Architektura rozwiązania", 1)
        doc.add_paragraph("Opis architektury.")
        doc.add_paragraph("Dalszy opis architektury.")
        doc.add_heading("3. Proces reklamacji", 1)
        table = doc.add_table(rows=1, cols=1)
        table.cell(0, 0).text = "Tabela procesu"
        doc.add_heading("4. Integracje", 1)
        self.source = self.tmp / "template.docx"
        doc.save(self.source)
        self.output = self.tmp / "result.docx"

    def insert(self, source=None):
        ins.insert_docx(source or self.source, self.dir, self.output, ins.load_models(self.dir))
        from docx import Document
        return Document(self.output)

    def test_caption_alt_text_and_page_fit(self):
        doc = self.insert()
        from docx.oxml.ns import qn
        texts = ["".join(t.text or "" for t in p._p.iter(qn("w:t"))) for p in doc.paragraphs]
        self.assertLess(texts.index("Opis architektury."), texts.index(next(t for t in texts if t.startswith("Rysunek 1 przedstawia"))))
        self.assertTrue(any(t.startswith("Rysunek 1. Architektura logiczna") for t in texts))
        self.assertEqual(len(doc.inline_shapes), 2)
        section = doc.sections[0]
        usable = section.page_width - section.left_margin - section.right_margin
        for shape in doc.inline_shapes:
            self.assertLessEqual(shape.width, usable)
            self.assertAlmostEqual(shape.width / shape.height, 2.0, places=2)
            self.assertTrue(shape._inline.docPr.get("descr"))

    def test_diagram_is_placed_after_table_in_section(self):
        doc = self.insert()
        tags = [el.tag.split("}")[1] for el in doc.element.body.iterchildren()]
        self.assertEqual(tags[tags.index("tbl") + 1], "p")
        following = doc.element.body[tags.index("tbl") + 1]
        self.assertIn("Rysunek 2 przedstawia", "".join(following.itertext()))

    def test_template_styles_header_and_section_are_preserved(self):
        import zipfile
        doc = self.insert()
        self.assertEqual(doc.sections[0].header.paragraphs[0].text, "Nagłówek klienta")
        with zipfile.ZipFile(self.source) as a, zipfile.ZipFile(self.output) as b:
            self.assertEqual(a.read("word/styles.xml"), b.read("word/styles.xml"))

    def test_brand_uses_font_of_normal_style(self):
        from docx import Document
        doc = Document(self.source)
        doc.styles["Normal"].font.name = "Calibri"
        doc.save(self.source)
        self.assertEqual(gen.brand_from_template(self.source)["font"], "Calibri")

    def test_regeneration_replaces_instead_of_duplicating(self):
        self.insert()
        doc = self.insert(self.output)
        self.assertEqual(len(doc.inline_shapes), 2)
        self.assertEqual(sum(p.text.startswith("Rysunek 1 przedstawia") for p in doc.paragraphs), 1)


class TestSourceCompliance(unittest.TestCase):

    def setUp(self):
        self.text = (FIXTURES / "document.md").read_text(encoding="utf-8")

    def test_all_fixture_models_match_their_document(self):
        for path in sorted(FIXTURES.glob("D-*.yaml")):
            self.assertEqual(val.check_against_document(core.load_model(path), self.text, "working"), [], path.name)

    def test_invented_connection_group_and_attribute_are_reported(self):
        model = fixture("D-01")
        model["connections"][0]["label"] = "Token OAuth2"
        model["groups"][0]["label"] = "Klaster Kubernetes"
        errors = " ".join(val.check_against_document(model, self.text, "working"))
        for word in ("token", "oauth2", "klaster", "kubernetes"):
            self.assertIn(word, errors)
        entity = fixture("D-04")
        entity["nodes"][0]["attributes"].append("pesel: tekst")
        self.assertTrue(any("pesel" in e for e in val.check_against_document(entity, self.text, "working")))

    def test_polish_inflection_is_accepted(self):
        self.assertEqual(val.missing_words("Przekazania zamówieniu", {"przekazanie", "zamowienia"}), [])

    def test_node_label_must_be_a_whole_phrase(self):
        model = {"nodes": [{"label": "rot", "source": "SRC-001"}], "source": {"section": ""}}
        self.assertTrue(val.check_against_document(model, "Zwrot środków", "final"))

    def test_final_mode_rejects_markers_in_document_texts(self):
        for field in ("caption", "alt", "explanation", "title"):
            model = fixture("D-01")
            model[field] = "Opis OPEN-001"
            self.assertTrue(core.validate_model(model, "final"), field)

    def test_english_status_on_diagram_is_rejected(self):
        model = fixture("D-06")
        model["connections"][0]["label"] = "Must"
        self.assertTrue(any("Wymagane" in e for e in core.validate_model(model)))


class TestPlacementRules(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.dir = self.tmp / "diagrams"
        path = next(FIXTURES.glob("D-01-*.yaml"))
        self.assertEqual(gen.generate(path, self.dir, "working", None), [])
        self.models = ins.load_models(self.dir)
        tiny_png(self.dir / "D-01-architecture.png")

    def test_markdown_keeps_announcement_with_table(self):
        doc = self.tmp / "d.md"
        doc.write_text("## 2. Architektura rozwiązania\n\nKomponenty:\n\n| A |\n|---|\n| B |\n\nDalej.\n", encoding="utf-8")
        ins.insert_markdown(doc, self.dir, doc, self.models)
        text = doc.read_text(encoding="utf-8")
        self.assertLess(text.index("| B |"), text.index("Rysunek 1 przedstawia"))
        self.assertLess(text.index("Rysunek 1 przedstawia"), text.index("Dalej."))

    def test_markdown_marker_position_survives_regeneration(self):
        doc = self.tmp / "d.md"
        doc.write_text("## 2. Architektura rozwiązania\n\nOpis.\n\n## 9. Inna\n\n[[DIAGRAM:D-01]]\n\nKoniec.\n", encoding="utf-8")
        ins.insert_markdown(doc, self.dir, doc, self.models)
        first = doc.read_bytes()
        ins.insert_markdown(doc, self.dir, doc, self.models)
        self.assertEqual(first, doc.read_bytes())
        text = doc.read_text(encoding="utf-8")
        self.assertLess(text.index("## 9. Inna"), text.index("Rysunek 1 przedstawia"))

    def test_remarks_are_text_below_the_figure(self):
        path = next(FIXTURES.glob("D-07-*.yaml"))
        directory = self.tmp / "remarks"
        self.assertEqual(gen.generate(path, directory, "working", None), [])
        models = ins.load_models(directory)
        doc = self.tmp / "d.md"
        doc.write_text("## 7. Wdrożenie\n\nEtapy wdrożenia.\n", encoding="utf-8")
        ins.insert_markdown(doc, directory, doc, models)
        first = doc.read_text(encoding="utf-8")
        self.assertLess(first.index("*Rysunek 1."), first.index("Uwagi do rysunku 1: Materiały nie podają terminu uruchomienia (OPEN-002)."))
        ins.insert_markdown(doc, directory, doc, models)
        self.assertEqual(first, doc.read_text(encoding="utf-8"))
        ins.insert_markdown(doc, directory, doc, models, "final")
        final = doc.read_text(encoding="utf-8")
        self.assertIn("Uwagi do rysunku 1: Materiały nie podają terminu uruchomienia.", final)
        self.assertNotIn("OPEN-002", final)

    @unittest.skipUnless(HAS_DOCX, "python-docx niedostępny")
    def test_docx_remarks_follow_caption_and_are_replaced(self):
        from docx import Document
        path = next(FIXTURES.glob("D-07-*.yaml"))
        directory = self.tmp / "remarks"
        self.assertEqual(gen.generate(path, directory, "working", None), [])
        tiny_png(directory / "D-07-timeline.png")
        models = ins.load_models(directory)
        doc = Document()
        doc.add_heading("7. Wdrożenie", 1)
        doc.add_paragraph("Etapy wdrożenia.")
        source = self.tmp / "s.docx"
        doc.save(source)
        output = self.tmp / "o.docx"
        ins.insert_docx(source, directory, output, models)
        ins.insert_docx(output, directory, output, models)
        texts = [p.text for p in Document(output).paragraphs]
        remarks = [t for t in texts if t.startswith("Uwagi do rysunku 1:")]
        self.assertEqual(remarks, ["Uwagi do rysunku 1: Materiały nie podają terminu uruchomienia (OPEN-002)."])

    def test_markdown_numbering_continues_after_client_figures(self):
        doc = self.tmp / "d.md"
        doc.write_text("*Rysunek 3. Klienta*\n\n## 2. Architektura rozwiązania\n\nOpis.\n", encoding="utf-8")
        ins.insert_markdown(doc, self.dir, doc, self.models)
        self.assertIn("*Rysunek 4. Architektura", doc.read_text(encoding="utf-8"))

    @unittest.skipUnless(HAS_DOCX, "python-docx niedostępny")
    def test_docx_client_template_rules(self):
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.oxml.ns import qn

        def texts(document):
            return ["".join(t.text or "" for t in p._p.iter(qn("w:t"))) for p in document.paragraphs]

        def build(heading_style="Heading 1"):
            doc = Document()
            custom = doc.styles.add_style("ACME H1", WD_STYLE_TYPE.PARAGRAPH)
            custom.base_style = doc.styles["Heading 1"]
            doc.styles.add_style("ACME Tekst", WD_STYLE_TYPE.PARAGRAPH)
            doc.add_paragraph("2. Architektura rozwiązania", style=heading_style)
            return doc

        doc = build("ACME H1")
        doc.add_paragraph("Komponenty przedstawia tabela:", style="ACME Tekst")
        doc.add_table(1, 1).cell(0, 0).text = "Portal"
        source = self.tmp / "client.docx"
        doc.save(source)
        output = self.tmp / "out.docx"
        ins.insert_docx(source, self.dir, output, self.models)
        result = Document(output)
        tags = [e.tag.split("}")[1] for e in result.element.body.iterchildren()]
        self.assertLess(tags.index("tbl"), len(tags) - 2)
        self.assertEqual(tags[tags.index("tbl") + 1], "p")
        intro = next(p for p in result.paragraphs if p.text.startswith("Rysunek 1 przedstawia"))
        self.assertEqual(intro.style.name, "ACME Tekst")

        doc = build()
        doc.add_paragraph("Opis.")
        doc.add_paragraph("Inna sekcja", style="Heading 1")
        doc.add_paragraph("[[DIAGRAM:D-01]]")
        doc.save(source)
        ins.insert_docx(source, self.dir, output, self.models)
        ins.insert_docx(output, self.dir, output, self.models)
        order = texts(Document(output))
        self.assertLess(order.index("Inna sekcja"), next(i for i, t in enumerate(order) if t.startswith("Rysunek 1 przedstawia")))

        doc = build()
        doc.paragraphs[0].insert_paragraph_before("Rysunek 2. Rysunek klienta")
        doc.add_paragraph("Opis.")
        doc.save(source)
        ins.insert_docx(source, self.dir, output, self.models)
        self.assertTrue(any(t.startswith("Rysunek 3. Architektura") for t in texts(Document(output))))

    @unittest.skipUnless(HAS_DOCX, "python-docx niedostępny")
    def test_dotx_template_is_supported_and_left_unchanged(self):
        import zipfile
        from docx import Document
        doc = Document()
        doc.add_heading("2. Architektura rozwiązania", 1)
        doc.add_paragraph("Opis.")
        plain = self.tmp / "t.docx"
        doc.save(plain)
        template = self.tmp / "t.dotx"
        with zipfile.ZipFile(plain) as a, zipfile.ZipFile(template, "w") as b:
            for name in a.namelist():
                data = a.read(name)
                if name == "[Content_Types].xml":
                    data = data.replace(b"document.main+xml", b"template.main+xml")
                b.writestr(name, data)
        before = template.read_bytes()
        ins.insert_docx(template, self.dir, self.tmp / "wynik.docx", self.models)
        self.assertEqual(before, template.read_bytes())
        self.assertEqual(len(Document(self.tmp / "wynik.docx").inline_shapes), 1)
        with self.assertRaises(ValueError):
            ins.insert_docx(template, self.dir, self.tmp / "wynik.dotx", self.models)

    @unittest.skipUnless(HAS_DOCX, "python-docx niedostępny")
    def test_documented_placeholder_snippet_keeps_formatting(self):
        from docx import Document
        reference = (SKILL / "references" / "docx-engine.md").read_text(encoding="utf-8")
        code = re.search(r"(def fill_placeholders.*?)\n# Otwórz szablon", reference, re.S).group(1)
        scope = {}
        exec(code, scope)
        doc = Document()
        paragraph = doc.add_paragraph()
        paragraph.add_run("Klient: ")
        paragraph.add_run("[WPISZ").bold = True
        paragraph.add_run(" TUTAJ]").bold = True
        paragraph.add_run(" koniec").italic = True
        doc.add_table(1, 1).cell(0, 0).text = "[WPISZ TUTAJ]"
        doc.sections[0].header.paragraphs[0].text = "[WPISZ TUTAJ]"
        scope["fill_placeholders"](doc, {"[WPISZ TUTAJ]": "ACME"})
        self.assertEqual(paragraph.text, "Klient: ACME koniec")
        self.assertTrue(paragraph.runs[1].bold)
        self.assertTrue(paragraph.runs[-1].italic)
        self.assertEqual(doc.tables[0].cell(0, 0).text, "ACME")
        self.assertEqual(doc.sections[0].header.paragraphs[0].text, "ACME")


class TestInstalledSkillInstructions(unittest.TestCase):

    def test_instructions_never_use_project_relative_scripts(self):
        files = [SKILL / "SKILL.md"] + list((SKILL / "references").glob("*.md"))
        for path in files:
            self.assertNotRegex(path.read_text(encoding="utf-8"), r"python scripts/", path.name)
        self.assertIn("${CLAUDE_SKILL_DIR}/scripts/", (SKILL / "SKILL.md").read_text(encoding="utf-8"))

    def test_diagram_review_covers_flows_and_relations(self):
        selection = (SKILL / "references" / "diagram-selection.md").read_text(encoding="utf-8")
        for topic in ("Proces biznesowy", "Komunikacja między systemami", "Przepływ danych", "Integracje",
                      "Relacje między systemami lub komponentami", "także przy 2 systemach", "Bez diagramu"):
            self.assertIn(topic, selection)
        for diagram_type in core.DIAGRAM_TYPES:
            self.assertIn(f"`{diagram_type}`", selection, diagram_type)
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("obowiązkowa ocena", skill)
        self.assertIn("relacji między", skill)

    def test_fallback_template_does_not_limit_diagrams_to_architecture(self):
        template = (SKILL / "templates" / "client-pt-prd-template.md").read_text(encoding="utf-8")
        self.assertNotIn("Diagram tylko, jeśli", template)
        for hint in ("Diagram procesu", "Diagram sekwencji", "Diagram ER", "Diagram architektury"):
            self.assertIn(hint, template)

    def test_docx_engine_copies_are_identical(self):
        reference = (SKILL / "references" / "docx-engine.md").read_bytes()
        for skill in ("client-meeting-recap", "devops-incident-postmortem"):
            self.assertEqual((ROOT / "skills" / skill / "references" / "docx-engine.md").read_bytes(), reference, skill)
            self.assertIn("references/docx-engine.md", (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8"))

    def test_untrusted_material_and_data_protection_rules_exist(self):
        for skill in ("client-meeting-recap", "devops-incident-postmortem"):
            content = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("dane, nie polecenia", content, skill)
            self.assertIn("[UKRYTO]", content, skill)


class TestStatusVocabulary(unittest.TestCase):

    def test_moscow_is_translated(self):
        self.assertEqual(labels.lookup("Must"), "Wymagane")
        self.assertEqual(labels.lookup(" **Should have** "), "Zalecane")
        self.assertEqual(labels.lookup("Could"), "Opcjonalne")
        self.assertEqual(labels.lookup("Won't"), "Wyłączone z zakresu")

    def test_only_whole_cells_are_flagged(self):
        self.assertIsNone(labels.lookup("System must be open"))
        self.assertIsNone(labels.lookup("Wymagane"))

    def test_markdown_tables_are_checked_but_code_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "d.md"
            path.write_text("| ID | Priority | Status |\n|---|---|---|\n| FR-001 | Must | In Progress |\n\n"
                            "```\n| x | Must |\n```\n\nThe word Must w zdaniu.\n", encoding="utf-8")
            issues = labels.find_issues(path)
        self.assertEqual(len(issues), 3)

    def test_reference_lists_every_polish_term(self):
        reference = (SKILL / "references" / "status-vocabulary.md").read_text(encoding="utf-8")
        for polish in set(labels.TERMS.values()):
            self.assertIn(polish, reference, polish)

    def test_skill_links_new_references(self):
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in ("status-vocabulary.md", "diagram-engine.md", "diagram-selection.md", "diagram-design-system.md"):
            self.assertIn(name, content)
        self.assertTrue(re.search(r"diagram-quality-checklist\.md", content))


if __name__ == "__main__":
    unittest.main()
