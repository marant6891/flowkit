"""Eksportuje diagram SVG do PNG w wysokiej rozdzielczości.

Użycie: python export_diagram.py diagrams/D-01-architecture.svg [...]

Kolejność rendererów: Playwright (Chromium, Edge, Chrome), a potem CairoSVG.
Kody wyjścia: 0 = sukces, 3 = brak dostępnego renderera, 1 = błąd eksportu.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PNG_SCALE = 3


def open_browser():
    """Zwraca (playwright, browser) albo (None, None), gdy brak przeglądarki."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, None
    playwright = sync_playwright().start()
    for options in ({}, {"channel": "msedge"}, {"channel": "chrome"}):
        try:
            return playwright, playwright.chromium.launch(**options)
        except Exception:  # brak danej przeglądarki: próbujemy kolejnej
            continue
    playwright.stop()
    return None, None


def export_with_browser(browser, svg_path: Path, png_path: Path) -> None:
    page = browser.new_page(device_scale_factor=PNG_SCALE)
    try:
        page.set_content(f"<!doctype html><html><body style='margin:0'>{svg_path.read_text(encoding='utf-8')}</body></html>")
        page.locator("svg").first.screenshot(path=str(png_path))
    finally:
        page.close()


def export_all(paths: list[Path]) -> tuple[str | None, list[Path]]:
    """Zwraca nazwę użytego renderera i listę utworzonych plików PNG."""
    playwright, browser = open_browser()
    created = []
    if browser:
        try:
            for path in paths:
                target = path.with_suffix(".png")
                export_with_browser(browser, path, target)
                created.append(target)
        finally:
            browser.close()
            playwright.stop()
        return "playwright", created
    try:
        import cairosvg
    except (ImportError, OSError):
        return None, []
    for path in paths:
        target = path.with_suffix(".png")
        cairosvg.svg2png(url=str(path), write_to=str(target), scale=PNG_SCALE)
        created.append(target)
    return "cairosvg", created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("svg", nargs="+", type=Path)
    args = parser.parse_args()
    missing = [str(p) for p in args.svg if not p.exists()]
    if missing:
        print(f"BŁĄD: brak plików: {', '.join(missing)}")
        return 1
    renderer, created = export_all(args.svg)
    if renderer is None:
        print("BRAK RENDERERA: zainstaluj Playwright albo CairoSVG. Pliki SVG i HTML pozostają gotowe; "
              "do osadzenia w DOCX potrzebny jest PNG.")
        return 3
    for path in created:
        print(f"OK {path.name} ({renderer})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
