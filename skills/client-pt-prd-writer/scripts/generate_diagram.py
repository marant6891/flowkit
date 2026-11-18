"""Generuje diagram SVG i HTML z modelu pośredniego YAML.

Użycie:
  python generate_diagram.py model.yaml [model2.yaml ...] --out diagrams/
      [--mode working|final] [--brand-from szablon.docx]

Plik wynikowy powstaje tylko wtedy, gdy model i geometria przejdą walidację.
Kody wyjścia: 0 = sukces, 1 = błąd modelu lub geometrii.
"""
from __future__ import annotations

import argparse
import re
import shutil
import statistics
import sys
import zipfile
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagram_core import (  # noqa: E402
    LAYERED_TYPES, MATRIX_TYPES, SEQUENCE_TYPES, TIMELINE_TYPES, TYPE_LABELS, UNCERTAIN_RE,
    ModelError, block_width, build_theme, load_model, snap, text_width,
    validate_model, wrap,
)

MAX_WIDTH = 860          # powyżej tej szerokości tekst w Wordzie (A4) staje się nieczytelny
MARGIN = 24
FS_NODE, FS_SUB, FS_EDGE = 14, 12, 12
LINE_NODE, LINE_SUB, LINE_EDGE = 18, 15, 15
EDGE_LABEL_W = 104
LAYOUT_GAPS = (32, 48, 72)  # kolejne próby rozluźnienia układu


class Canvas:
    """Zbiera elementy SVG oraz ich geometrię do kontroli jakości."""

    def __init__(self, theme: dict):
        self.t = theme
        self.layers = {name: [] for name in ("back", "group", "edge", "node", "text")}
        self.nodes: list[dict] = []
        self.groups: list[dict] = []
        self.texts: list[dict] = []
        self.edges: list[dict] = []
        self.width = 0.0
        self.height = 0.0
        self.top = 0.0

    def text(self, lines, x, y, size, *, anchor="start", weight=400, fill=None, family=None,
             owner=None, box=None, kind="label", layer="text", line_h=None, spacing=None):
        lines = [lines] if isinstance(lines, str) else lines
        line_h = line_h or round(size * 1.3)
        widths = [text_width(l, size, weight >= 600) for l in lines]
        width = max(widths, default=0)
        left = x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x
        attrs = (f'x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" fill="{fill or self.t["ink"]}" '
                 f'font-family="{escape(family or self.t["font"], quote=True)}"')
        if spacing:
            attrs += f' letter-spacing="{spacing}"'
        if box:
            attrs += ' data-box="{:g} {:g} {:g} {:g}"'.format(*box)
        spans = "".join(f'<tspan x="{x:g}" dy="{0 if i == 0 else line_h}">{escape(l)}</tspan>'
                        for i, l in enumerate(lines))
        self.layers[layer].append(f"<text {attrs}>{spans}</text>")
        self.texts.append({"x": left, "y": y - size * 0.85, "w": width,
                           "h": size * 1.1 + line_h * (len(lines) - 1),
                           "owner": owner, "box": box, "kind": kind, "text": " ".join(lines)})

    def path(self, d, *, stroke=None, width=1, fill="none", dash=None, layer="edge", extra=""):
        attrs = f'd="{d}" fill="{fill}" stroke="{stroke or self.t["line"]}" stroke-width="{width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.layers[layer].append(f"<path {attrs} {extra}/>")

    def rect(self, x, y, w, h, *, rx=6, fill=None, stroke=None, width=1, dash=None, layer="node"):
        attrs = (f'x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" '
                 f'fill="{fill or self.t["node"]}" stroke="{stroke or self.t["rule"]}" stroke-width="{width}"')
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.layers[layer].append(f"<rect {attrs}/>")

    def edge(self, points, source, target, *, start_arrow=False, end_arrow=True, color=None, conn_id=""):
        extra = ""
        if end_arrow:
            extra += 'marker-end="url(#arrow-line)" '
        if start_arrow:
            extra += 'marker-start="url(#arrow-line-start)" '
        self.path(_rounded(points), stroke=color or self.t["line"], width=1.25, extra=extra)
        self.edges.append({"points": points, "source": source, "target": target, "id": conn_id})

    def to_svg(self, model: dict) -> str:
        t = self.t
        vb_w = self.width + 2 * MARGIN
        vb_h = self.height - self.top + 2 * MARGIN
        vb_y = self.top - MARGIN
        title, desc = escape(str(model["title"])), escape(str(model["alt"]))
        defs = []
        for name, color in (("line", t["line"]),):
            defs.append(f'<marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
                        f'markerHeight="8" orient="auto"><path d="M0 0.8 L9.5 5 L0 9.2 Z" fill="{color}"/></marker>')
            defs.append(f'<marker id="arrow-{name}-start" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" '
                        f'markerHeight="8" orient="auto"><path d="M10 0.8 L0.5 5 L10 9.2 Z" fill="{color}"/></marker>')
        body = "\n".join("\n".join(self.layers[k]) for k in ("back", "group", "edge", "node", "text"))
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="d-title d-desc" '
            f'width="{vb_w:g}" height="{vb_h:g}" viewBox="{-MARGIN} {vb_y:g} {vb_w:g} {vb_h:g}" '
            f'data-diagram="{escape(str(model["id"]))}">\n'
            f'<title id="d-title">{title}</title>\n<desc id="d-desc">{desc}</desc>\n'
            f'<defs>{"".join(defs)}</defs>\n'
            f'<rect x="{-MARGIN}" y="{vb_y:g}" width="{vb_w:g}" height="{vb_h:g}" fill="{t["paper"]}"/>\n'
            f'{body}\n</svg>\n'
        )


def _rounded(points, radius=5) -> str:
    pts = [points[0]]
    for point in points[1:]:
        if point != pts[-1]:
            pts.append(point)
    d = [f"M{pts[0][0]:g} {pts[0][1]:g}"]
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        r1 = min(radius, (abs(x1 - x0) + abs(y1 - y0)) / 2)
        r2 = min(radius, (abs(x2 - x1) + abs(y2 - y1)) / 2)
        r = min(r1, r2)
        ax = x1 - (r if x1 > x0 else -r if x1 < x0 else 0)
        ay = y1 - (r if y1 > y0 else -r if y1 < y0 else 0)
        bx = x1 + (r if x2 > x1 else -r if x2 < x1 else 0)
        by = y1 + (r if y2 > y1 else -r if y2 < y1 else 0)
        d.append(f"L{ax:g} {ay:g} Q{x1:g} {y1:g} {bx:g} {by:g}")
    d.append(f"L{pts[-1][0]:g} {pts[-1][1]:g}")
    return " ".join(d)


# --- Węzły -------------------------------------------------------------------

def measure_node(node: dict, down_slots: float = 0) -> dict:
    ntype = node.get("type", "service")
    if ntype == "entity":
        attrs = [str(a) for a in node.get("attributes") or []]
        width = max([176.0, text_width(node["label"], FS_NODE, True) + 28]
                    + [text_width(a, FS_SUB) + 28 for a in attrs])
        return {"w": snap(max(width, down_slots) + 2), "h": snap(34 + 20 * len(attrs) + 8),
                "lines": [node["label"]], "sub": [], "attrs": attrs}
    text_w = 116 if ntype != "decision" else 124
    lines = wrap(node["label"], FS_NODE, text_w, True)
    while len(lines) > 3 and text_w < 240:
        text_w += 24
        lines = wrap(node["label"], FS_NODE, text_w, True)
    sub = wrap(node["sublabel"], FS_SUB, text_w) if node.get("sublabel") else []
    inner = max(block_width(lines, FS_NODE, True), block_width(sub, FS_SUB))
    height = len(lines) * LINE_NODE + len(sub) * LINE_SUB + 24
    width = max(132.0, inner + 32, down_slots)
    if ntype == "decision":
        width = max(216.0, inner * 1.9, down_slots * 1.3)
        height = max(96.0, height * 1.9)
    if ntype == "database":
        height += 14
    if ntype == "queue":
        width += 16
    return {"w": snap(width + 2), "h": snap(height + 2), "lines": lines, "sub": sub, "attrs": []}


def draw_node(c: Canvas, node: dict, m: dict, x: float, y: float) -> None:
    t = c.t
    w, h = m["w"], m["h"]
    ntype = node.get("type", "service")
    fill, stroke, width, dash = t["node"], t["rule"], 1, None
    ink = t["ink"]
    if ntype == "external":
        fill, stroke = t["external"], t["muted"]
    if node.get("focus"):
        fill, stroke, width = t["accent_tint"], t["accent"], 1.5
    if ntype in ("start", "end"):
        fill, stroke, ink = t["ink"], t["ink"], t["paper"]
    box = (x, y, w, h)
    c.nodes.append({"id": node["id"], "x": x, "y": y, "w": w, "h": h, "group": node.get("group")})

    if ntype == "decision":
        points = f"{x + w / 2:g},{y:g} {x + w:g},{y + h / 2:g} {x + w / 2:g},{y + h:g} {x:g},{y + h / 2:g}"
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        c.layers["node"].append(f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" '
                                f'stroke-width="{width}"{extra}/>')
    elif ntype == "database":
        rim = 7
        c.path(f"M{x:g} {y + rim:g} A{w / 2:g} {rim} 0 0 1 {x + w:g} {y + rim:g} L{x + w:g} {y + h - rim:g} "
               f"A{w / 2:g} {rim} 0 0 1 {x:g} {y + h - rim:g} Z", stroke=stroke, width=width, fill=fill,
               dash=dash, layer="node")
        c.path(f"M{x:g} {y + rim:g} A{w / 2:g} {rim} 0 0 0 {x + w:g} {y + rim:g}", stroke=stroke, width=width,
               layer="node")
    elif ntype == "entity":
        c.rect(x, y, w, h, fill=fill, stroke=stroke, width=width, dash=dash)
        c.path(f"M{x:g} {y + 32:g} H{x + w:g}", stroke=stroke, layer="node")
        c.text(m["lines"], x + 14, y + 22, FS_NODE, weight=600, fill=ink, owner=node["id"], box=box, kind="node")
        for i, attr in enumerate(m["attrs"]):
            c.text(attr, x + 14, y + 52 + i * 20, FS_SUB, fill=t["muted"], owner=node["id"], box=box, kind="node")
        return
    else:
        rx = h / 2 if ntype in ("actor", "start", "end") else 14 if ntype == "state" else 6
        c.rect(x, y, w, h, rx=rx, fill=fill, stroke=stroke, width=width, dash=dash)
        if ntype == "queue":
            for off in (10, 18):
                c.path(f"M{x + w - off:g} {y:g} V{y + h:g}", stroke=stroke, layer="node")

    shift = -8 if ntype == "queue" else 3 if ntype == "database" else 0
    total = len(m["lines"]) * LINE_NODE + len(m["sub"]) * LINE_SUB
    base = y + (h - total) / 2 + 14 + shift * (ntype == "database")
    cx = x + w / 2 + (shift if ntype == "queue" else 0)
    c.text(m["lines"], cx, base, FS_NODE, anchor="middle", weight=600, fill=ink, owner=node["id"], box=box,
           kind="node", line_h=LINE_NODE)
    if m["sub"]:
        c.text(m["sub"], cx, base + len(m["lines"]) * LINE_NODE - 1, FS_SUB, anchor="middle",
               fill=ink if ntype in ("start", "end") else t["muted"], owner=node["id"], box=box, kind="node",
               line_h=LINE_SUB)


# --- Układ warstwowy (architektura, procesy, stany, ER, swimlane...) ---------

def _ranks(nodes, conns):
    ids = [n["id"] for n in nodes]
    out = {i: [] for i in ids}
    for conn in conns:
        out[conn["from"]].append(conn)
    state, reversed_conns = {}, set()

    def visit(nid):
        state[nid] = 1
        for conn in out[nid]:
            if state.get(conn["to"]) == 1:
                reversed_conns.add(id(conn))
            elif conn["to"] not in state:
                visit(conn["to"])
        state[nid] = 2

    incoming = {c["to"] for c in conns}
    for nid in [i for i in ids if i not in incoming] + ids:
        if nid not in state:
            visit(nid)
    pairs = [((c["to"], c["from"]) if id(c) in reversed_conns else (c["from"], c["to"]), c) for c in conns]
    rank = {i: 0 for i in ids}
    for _ in ids:
        changed = False
        for (a, b), _conn in pairs:
            if rank[b] < rank[a] + 1:
                rank[b] = rank[a] + 1
                changed = True
        if not changed:
            break
    return rank, pairs, reversed_conns


def layout_layered(c: Canvas, model: dict, node_gap: int) -> None:
    nodes = model["nodes"]
    conns = model.get("connections") or []
    by_id = {n["id"]: n for n in nodes}
    rank, pairs, reversed_conns = _ranks(nodes, conns)
    swimlane = model["type"] == "swimlane"
    band_key = "lane" if swimlane else "group"
    declared = [g["id"] for g in model.get("lanes" if swimlane else "groups") or []]
    bands = ([None] if any(not n.get(band_key) for n in nodes) else []) + declared
    column_of = {b: b for b in bands}
    if not swimlane:
        # Grupy z rozłącznych warstw (np. warstwy aplikacji) układamy jedna pod drugą.
        columns: list[list[tuple[int, int]]] = []
        for band in bands:
            ranks = [rank[n["id"]] for n in nodes if n.get(band_key) == band]
            if not ranks:
                column_of[band] = 0
                continue
            span = (min(ranks), max(ranks))
            for index, used in enumerate(columns):
                if all(span[1] < lo or span[0] > hi for lo, hi in used):
                    used.append(span)
                    column_of[band] = index
                    break
            else:
                columns.append([span])
                column_of[band] = len(columns) - 1
        bands = list(range(max(len(columns), 1)))

    # Wierzchołki: rzeczywiste węzły + punkty pośrednie dla długich krawędzi.
    verts = {n["id"]: {"id": n["id"], "rank": rank[n["id"]], "band": column_of[n.get(band_key)], "dummy": False}
             for n in nodes}
    chains = []
    for (a, b), conn in pairs:
        chain = [a]
        for r in range(rank[a] + 1, rank[b]):
            vid = f"~{len(verts)}"
            verts[vid] = {"id": vid, "rank": r, "band": column_of[by_id[a].get(band_key)], "dummy": True}
            chain.append(vid)
        chain.append(b)
        chains.append({"chain": chain, "conn": conn, "rev": id(conn) in reversed_conns})

    label_lines = {}
    for ch in chains:
        if ch["conn"].get("label"):
            label_lines[id(ch)] = wrap(ch["conn"]["label"], FS_EDGE, EDGE_LABEL_W)

    down, up = {v: [] for v in verts}, {v: [] for v in verts}
    for ch in chains:
        for a, b in zip(ch["chain"], ch["chain"][1:]):
            down[a].append((ch, b))
            up[b].append((ch, a))

    def slot_width(vid):
        widths = [block_width(label_lines[id(ch)], FS_EDGE) for ch, _ in down[vid]
                  if id(ch) in label_lines and ch["chain"][0] == vid]
        return max(widths, default=0) + 22 if widths else 0

    for vid, v in verts.items():
        if v["dummy"]:
            v.update(w=16, h=0, m=None)
        else:
            n_down = len(down[vid])
            need = slot_width(vid) * n_down if n_down > 1 else 0
            need = max(need, 28 * max(n_down, len(up[vid])))
            m = measure_node(by_id[vid], need)
            v.update(w=m["w"], h=m["h"], m=m)

    # Kolejność w warstwach: minimalizacja przecięć metodą barycentryczną.
    max_rank = max(v["rank"] for v in verts.values())
    layers = [[] for _ in range(max_rank + 1)]
    for vid, v in verts.items():
        layers[v["rank"]].append(vid)
    band_index = {b: i for i, b in enumerate(bands)}

    def crossings(order):
        pos = {v: i for layer in order for i, v in enumerate(layer)}
        total = 0
        for layer in order[:-1]:
            edges = [(pos[a], pos[b]) for a in layer for _, b in down[a]]
            total += sum(1 for i, e in enumerate(edges) for f in edges[i + 1:]
                         if (e[0] - f[0]) * (e[1] - f[1]) < 0)
        return total

    best, best_cross = [list(l) for l in layers], crossings(layers)
    for sweep in range(12):
        rng = range(1, len(layers)) if sweep % 2 == 0 else range(len(layers) - 2, -1, -1)
        neighbours = up if sweep % 2 == 0 else down
        for r in rng:
            ref = {v: i for i, v in enumerate(layers[r - 1 if sweep % 2 == 0 else r + 1])}
            current = {v: i for i, v in enumerate(layers[r])}

            def key(v):
                near = [ref[o] for _, o in neighbours[v] if o in ref]
                return band_index[verts[v]["band"]], statistics.mean(near) if near else current[v]
            layers[r].sort(key=key)
        score = crossings(layers)
        if score < best_cross:
            best, best_cross = [list(l) for l in layers], score
    layers = best

    # Współrzędne poziome: pasy (grupy/role), a w pasie wyrównanie do sąsiadów.
    pad = 20 if len(bands) > 1 or declared else 0
    band_gap = 28 if declared else 0
    x_cursor, intervals = 0.0, {}
    for band in bands:
        width = 0.0
        for layer in layers:
            members = [verts[v] for v in layer if verts[v]["band"] == band]
            width = max(width, sum(m["w"] for m in members) + node_gap * max(len(members) - 1, 0))
        if swimlane:
            lane = next(l for l in model["lanes"] if l["id"] == band)
            width = max(width, text_width(lane["label"], FS_SUB, True) + 8)
        intervals[band] = (x_cursor + pad, x_cursor + pad + width)
        x_cursor += width + 2 * pad + band_gap
    total_w = x_cursor - band_gap

    for band, (lo, hi) in intervals.items():
        for layer in layers:
            members = [v for v in layer if verts[v]["band"] == band]
            used = sum(verts[v]["w"] for v in members) + node_gap * max(len(members) - 1, 0)
            cursor = lo + ((hi - lo) - used) / 2
            for v in members:
                verts[v]["cx"] = cursor + verts[v]["w"] / 2
                cursor += verts[v]["w"] + node_gap

    def settle(layer, band):
        lo, hi = intervals[band]
        members = [v for v in layer if verts[v]["band"] == band]
        edge = lo
        for v in members:
            half = verts[v]["w"] / 2
            verts[v]["cx"] = max(verts[v]["cx"], edge + half)
            edge = verts[v]["cx"] + half + node_gap
        edge = hi
        for v in reversed(members):
            half = verts[v]["w"] / 2
            verts[v]["cx"] = min(verts[v]["cx"], edge - half)
            edge = verts[v]["cx"] - half - node_gap

    for sweep in range(10):
        order = layers if sweep % 2 == 0 else list(reversed(layers))
        neighbours = up if sweep % 2 == 0 else down
        for layer in order:
            for v in layer:
                near = [verts[o]["cx"] for _, o in neighbours[v]]
                if near:
                    verts[v]["cx"] = statistics.median(near)
            for band in bands:
                settle(layer, band)
    for v in verts.values():
        v["cx"] = snap(v["cx"])
        v["x"] = v["cx"] - v["w"] / 2
    for layer in layers:
        for band in bands:
            settle(layer, band)
    for v in verts.values():
        v["x"] = v["cx"] - v["w"] / 2

    # Porty krawędzi.
    ports_down, ports_up = {}, {}
    for vid, v in verts.items():
        out = sorted(down[vid], key=lambda item: verts[item[1]]["cx"])
        slot = slot_width(vid)
        for i, (ch, other) in enumerate(out):
            if len(out) == 1:
                x = v["cx"]
            elif slot:
                start = v["cx"] - slot * len(out) / 2
                x = start + slot * i + 8
            else:
                x = v["x"] + v["w"] * (i + 1) / (len(out) + 1)
            ports_down[(id(ch), vid)] = snap(x)
        inc = sorted(up[vid], key=lambda item: verts[item[1]]["cx"])
        for i, (ch, other) in enumerate(inc):
            if len(inc) == 1:
                x = v["cx"]
                source_x = ports_down[(id(ch), other)] if (id(ch), other) in ports_down else None
                if source_x is None:
                    source_x = verts[other]["cx"]
                if not v["dummy"] and v["x"] + 16 <= source_x <= v["x"] + v["w"] - 16:
                    x = source_x
            else:
                x = v["x"] + v["w"] * (i + 1) / (len(inc) + 1)
            ports_up[(id(ch), vid)] = snap(x)
    # Porty górne zależą od dolnych z poprzedniej warstwy: drugi przebieg po ustaleniu wszystkich.
    for vid, v in verts.items():
        if len(up[vid]) == 1 and not v["dummy"]:
            ch, other = up[vid][0]
            source_x = ports_down[(id(ch), other)]
            if v["x"] + 16 <= source_x <= v["x"] + v["w"] - 16:
                ports_up[(id(ch), vid)] = source_x

    # Tory poziome w przerwach między warstwami.
    gaps = []
    for r in range(max_rank):
        spans = []
        label_h = 0
        for a in layers[r]:
            for ch, b in down[a]:
                x1, x2 = ports_down[(id(ch), a)], ports_up[(id(ch), b)]
                if abs(x1 - x2) >= 2:
                    spans.append((min(x1, x2), max(x1, x2), id(ch), a))
                if id(ch) in label_lines and ch["chain"][0] == a:
                    label_h = max(label_h, len(label_lines[id(ch)]) * LINE_EDGE + 6)
        tracks, assigned = [], {}
        for lo, hi, cid, a in sorted(spans):
            for i, end in enumerate(tracks):
                if end + 14 < lo:
                    tracks[i] = hi
                    assigned[(cid, a)] = i
                    break
            else:
                tracks.append(hi)
                assigned[(cid, a)] = len(tracks) - 1
        gaps.append({"label_h": label_h, "tracks": len(tracks), "assigned": assigned})

    # Współrzędne pionowe.
    has_groups = bool(model.get("groups"))
    header = 44 if swimlane else 32 if has_groups else 0
    y = header
    rank_y, rank_h = {}, {}
    for r, layer in enumerate(layers):
        height = max(verts[v]["h"] for v in layer)
        rank_y[r], rank_h[r] = y, height
        for v in layer:
            verts[v]["y"] = y + (height - verts[v]["h"]) / 2
        if r < max_rank:
            gap = gaps[r]
            gap["top"] = y + height + (18 if has_groups else 8)
            gap["track_y"] = gap["top"] + gap["label_h"] + 8
            y = gap["track_y"] + gap["tracks"] * 12 + (44 if has_groups else 22)
        else:
            y += height
    content_h = y + (20 if has_groups or swimlane else 0)

    # Tła: role (swimlane) i grupy.
    if swimlane:
        for i, band in enumerate(bands):
            lo, hi = intervals[band]
            lane = next(l for l in model["lanes"] if l["id"] == band)
            c.rect(lo - pad, 0, hi - lo + 2 * pad, content_h, rx=4, fill=c.t["paper2"] if i % 2 == 0 else c.t["paper"],
                   stroke=c.t["rule"], layer="back")
            c.text(lane["label"], (lo + hi) / 2, 26, FS_SUB, anchor="middle", weight=700, fill=c.t["muted"],
                   kind="group", layer="back")
    for group in model.get("groups") or []:
        members = [verts[n["id"]] for n in nodes if n.get("group") == group["id"]]
        if not members:
            continue
        x0 = min(m["x"] for m in members) - 16
        x1 = max(m["x"] + m["w"] for m in members) + 16
        y0 = min(m["y"] for m in members) - 30
        y1 = max(m["y"] + m["h"] for m in members) + 14
        c.rect(x0, y0, x1 - x0, y1 - y0, rx=8, fill=c.t["paper2"], stroke=c.t["rule"], layer="group")
        c.text(group["label"], x0 + 12, y0 + 19, FS_SUB, weight=700, fill=c.t["muted"], kind="group", layer="group")
        c.groups.append({"id": group["id"], "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0})

    # Krawędzie.
    def boundary(v, x, bottom):
        if v["dummy"]:
            return v["y"]
        node = by_id[v["id"]]
        if node.get("type") == "decision":
            ratio = abs(x - v["cx"]) / (v["w"] / 2)
            half = v["h"] / 2 * (1 - ratio)
            mid = v["y"] + v["h"] / 2
            return mid + half if bottom else mid - half
        return v["y"] + v["h"] if bottom else v["y"]

    for ch in chains:
        conn = ch["conn"]
        points = []
        chain = ch["chain"]
        for a, b in zip(chain, chain[1:]):
            r = verts[a]["rank"]
            x1, x2 = ports_down[(id(ch), a)], ports_up[(id(ch), b)]
            if not points:
                points.append((x1, boundary(verts[a], x1, True)))
            if abs(x1 - x2) >= 2:
                track = gaps[r]["track_y"] + gaps[r]["assigned"][(id(ch), a)] * 12
                points += [(x1, track), (x2, track)]
            points.append((x2, boundary(verts[b], x2, False)))
        first, last = chain[0], chain[-1]
        if id(ch) in label_lines:
            lines = label_lines[id(ch)]
            x = ports_down[(id(ch), first)] + 7
            c.text(lines, x, gaps[verts[first]["rank"]]["top"] + 11, FS_EDGE, fill=c.t["muted"],
                   kind="edge", owner=conn.get("label"), line_h=LINE_EDGE)
        direction = conn.get("direction", "forward")
        end_arrow = direction in ("forward", "both")
        start_arrow = direction == "both"
        if ch["rev"]:
            points = list(reversed(points))
            first, last = last, first
        c.edge(points, first, last, start_arrow=start_arrow, end_arrow=end_arrow,
               conn_id=f'{conn["from"]}>{conn["to"]}')

    for vid, v in verts.items():
        if not v["dummy"]:
            draw_node(c, by_id[vid], v["m"], v["x"], v["y"])

    c.width = max(total_w, max(v["x"] + v["w"] for v in verts.values()))
    c.height = content_h


# --- Sekwencja ---------------------------------------------------------------

def layout_sequence(c: Canvas, model: dict, _gap: int) -> None:
    t = c.t
    nodes = model["nodes"]
    measures = {n["id"]: measure_node({**n, "type": "service"}) for n in nodes}
    step = max(max(m["w"] for m in measures.values()) + 24, 176)
    if step * len(nodes) > MAX_WIDTH:
        step = max(MAX_WIDTH / len(nodes), 148)
    xs = {n["id"]: step * i + step / 2 for i, n in enumerate(nodes)}
    head_h = max(m["h"] for m in measures.values())
    y = head_h + 28
    rows = []
    for i, conn in enumerate(model.get("connections") or [], 1):
        a, b = xs[conn["from"]], xs[conn["to"]]
        span = abs(a - b) - 20 if conn["from"] != conn["to"] else step - 56
        lines = wrap(f'{i}. {conn.get("label", "")}'.strip(), FS_EDGE, max(span, 96))
        rows.append((conn, lines, y + len(lines) * LINE_EDGE))
        y += len(lines) * LINE_EDGE + (46 if conn["from"] == conn["to"] else 26)
    bottom = y + 8
    for node in nodes:
        m = {**measures[node["id"]], "w": min(measures[node["id"]]["w"], step - 16)}
        x = xs[node["id"]]
        c.path(f"M{x:g} {head_h:g} V{bottom:g}", stroke=t["rule"], layer="back")
        draw_node(c, node, m, x - m["w"] / 2, 0)
    for conn, lines, arrow_y in rows:
        a, b = xs[conn["from"]], xs[conn["to"]]
        direction = conn.get("direction", "forward")
        color = t["muted"] if conn.get("kind") == "reply" else t["line"]
        if conn["from"] == conn["to"]:
            pts = [(a, arrow_y), (a + 36, arrow_y), (a + 36, arrow_y + 22), (a + 4, arrow_y + 22)]
            tx, anchor = a + 8, "start"
            c.edge(pts, conn["from"], conn["to"], color=color)
        else:
            sign = 1 if b > a else -1
            pts = [(a + 3 * sign, arrow_y), (b - 3 * sign, arrow_y)]
            tx, anchor = (a + b) / 2, "middle"
            c.edge(pts, conn["from"], conn["to"], color=color, end_arrow=direction in ("forward", "both"),
                   start_arrow=direction == "both")
        width = block_width(lines, FS_EDGE)
        top = arrow_y - len(lines) * LINE_EDGE - 3
        left = tx - width / 2 if anchor == "middle" else tx
        c.rect(left - 4, top, width + 8, len(lines) * LINE_EDGE, rx=2, fill=t["paper"], stroke=t["paper"], layer="edge")
        c.text(lines, tx, top + 12, FS_EDGE, anchor=anchor, kind="edge", line_h=LINE_EDGE)
    c.width = step * len(nodes)
    c.height = bottom


# --- Oś czasu i ścieżka użytkownika -------------------------------------------

def layout_timeline(c: Canvas, model: dict, _gap: int) -> None:
    t = c.t
    nodes = model["nodes"]
    per_row, card_w, gap = 4, 184, 16
    y = 0
    numbered = model["type"] == "user-journey"
    for start in range(0, len(nodes), per_row):
        row = nodes[start:start + per_row]
        cards = []
        for node in row:
            lines = wrap(node["label"], FS_NODE, card_w - 24, True)
            sub = wrap(node["sublabel"], FS_SUB, card_w - 24) if node.get("sublabel") else []
            cards.append((lines, sub, len(lines) * LINE_NODE + len(sub) * LINE_SUB + 24))
        card_h = snap(max(h for *_, h in cards) + 2)
        axis = y + 34
        end = (len(row) - 1) * (card_w + gap) + card_w
        arrow = start + per_row >= len(nodes)
        c.path(f"M0 {axis:g} H{end:g}", stroke=t["line"], width=1.25,
               extra='marker-end="url(#arrow-line)"' if arrow else "", layer="back")
        for i, (node, (lines, sub, _)) in enumerate(zip(row, cards)):
            x = i * (card_w + gap)
            marker = str(node.get("date") or (f"Krok {start + i + 1}" if numbered else ""))
            color = t["accent"] if node.get("focus") else t["ink"]
            if marker:
                c.text(wrap(marker, FS_SUB, card_w), x, axis - 14, FS_SUB, weight=700, fill=color, kind="node")
            c.layers["node"].append(f'<circle cx="{x + 6:g}" cy="{axis:g}" r="5" fill="{color}"/>')
            m = {"w": card_w, "h": card_h, "lines": lines, "sub": sub, "attrs": []}
            draw_node(c, {**node, "type": "step"}, m, x, axis + 16)
        y = axis + 16 + card_h + 24
    c.width = min(len(nodes), per_row) * (card_w + gap) - gap
    c.height = y - 24


# --- Macierze: śledzenie wymagań i uprawnienia ---------------------------------

def layout_matrix(c: Canvas, model: dict, _gap: int) -> None:
    t = c.t
    rows = [n for n in model["nodes"] if n.get("axis") == "row"]
    cols = [n for n in model["nodes"] if n.get("axis") == "column"]
    cells = {(x["from"], x["to"]): x for x in model.get("connections") or []}
    head_w = min(max([text_width(r["label"], FS_SUB, True) for r in rows] + [120]) + 24, 240)
    col_w = max(min((MAX_WIDTH - 40 - head_w) / max(len(cols), 1), 132), 72)
    col_lines = [wrap(n["label"], FS_SUB, col_w - 12, True) for n in cols]
    head_h = max(len(l) for l in col_lines) * LINE_SUB + 20
    for i, (col, lines) in enumerate(zip(cols, col_lines)):
        x = head_w + i * col_w
        c.rect(x, 0, col_w, head_h, rx=0, fill=t["paper2"], stroke=t["rule"])
        box = (x, 0, col_w, head_h)
        c.text(lines, x + col_w / 2, 22, FS_SUB, anchor="middle", weight=700, owner=col["id"], box=box, kind="node", line_h=LINE_SUB)
    y = head_h
    for row in rows:
        lines = wrap(row["label"], FS_SUB, head_w - 20, True)
        row_h = max(36, len(lines) * LINE_SUB + 16)
        for col in cols:
            cell = cells.get((row["id"], col["id"])) or cells.get((col["id"], row["id"]))
            row_h = max(row_h, len(wrap(str((cell or {}).get("label", "")), FS_SUB, col_w - 12)) * LINE_SUB + 16)
        box = (0, y, head_w, row_h)
        c.rect(0, y, head_w, row_h, rx=0, fill=t["paper2"], stroke=t["rule"])
        c.text(lines, 10, y + 21, FS_SUB, weight=700, owner=row["id"], box=box, kind="node", line_h=LINE_SUB)
        for i, col in enumerate(cols):
            x = head_w + i * col_w
            cell = cells.get((row["id"], col["id"])) or cells.get((col["id"], row["id"]))
            c.rect(x, y, col_w, row_h, rx=0, fill=t["node"], stroke=t["rule"])
            if cell:  # Pusta komórka nie stwierdza braku relacji ani uprawnienia.
                cell_lines = wrap(str(cell.get("label") or "●"), FS_SUB, col_w - 12)
                box = (x, y, col_w, row_h)
                c.text(cell_lines, x + col_w / 2, y + 21, FS_SUB, anchor="middle", fill=t["ink"],
                       owner=f'{row["id"]}:{col["id"]}', box=box, kind="node", line_h=LINE_SUB)
        y += row_h
    c.width = head_w + col_w * len(cols)
    c.height = y


# --- Elementy wspólne ----------------------------------------------------------

def add_header_and_notes(c: Canvas, model: dict) -> None:
    t = c.t
    if t["name"] == "full-editorial":
        title = wrap(model["title"], 24, max(c.width, 420))
        height = 34 + len(title) * 30 + 12
        c.top = -height
        c.text(TYPE_LABELS[model["type"]].upper(), 0, -height + 14, 11, weight=700, fill=t["accent"], kind="group", spacing="1.4")
        c.text(title, 0, -height + 46, 24, family=t["heading"], kind="group", line_h=30)
        c.width = max(c.width, block_width(title, 24))
        c.path(f"M0 -10 H{c.width:g}", stroke=t["rule"], layer="back")
    y = c.height + 22
    for i, note in enumerate(model.get("annotations") or [], 1):
        lines = wrap(f'{i}) {note["text"]}', FS_SUB, max(c.width, 420))
        c.width = max(c.width, block_width(lines, FS_SUB))
        c.text(lines, 0, y, FS_SUB, fill=t["muted"], kind="note", line_h=LINE_SUB)
        y += len(lines) * LINE_SUB + 6
    c.height = y - 14 if y > c.height + 22 else c.height


def _segments(points):
    return list(zip(points, points[1:]))


def _hits(seg, box, inset=1.0) -> bool:
    (x1, y1), (x2, y2) = seg
    left, right = min(x1, x2), max(x1, x2)
    top, bottom = min(y1, y2), max(y1, y2)
    return (right > box["x"] + inset and left < box["x"] + box["w"] - inset
            and bottom > box["y"] + inset and top < box["y"] + box["h"] - inset)


def check_scene(c: Canvas, model: dict) -> list[str]:
    """Kontrola geometrii: nachodzenie, kadrowanie, kolizje linii i czytelność."""
    issues = []
    for text in c.texts:
        if UNCERTAIN_RE.search(text["text"]):
            issues.append(f"niepewna treść na obrazie: '{text['text']}'")
    width = c.width + 2 * MARGIN
    if width > MAX_WIDTH + 2 * MARGIN:
        issues.append(f"diagram ma {width:.0f}px szerokości (limit {MAX_WIDTH + 2 * MARGIN}px): podziel go na przegląd i szczegóły")
    for i, a in enumerate(c.nodes):
        for b in c.nodes[i + 1:]:
            if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
                issues.append(f"węzły nachodzą na siebie: {a['id']} i {b['id']}")
    for group in c.groups:
        for node in c.nodes:
            inside = node["x"] < group["x"] + group["w"] and group["x"] < node["x"] + node["w"] and node["y"] < group["y"] + group["h"] and group["y"] < node["y"] + node["h"]
            if inside and node.get("group") != group["id"]:
                issues.append(f"węzeł {node['id']} wchodzi w obszar grupy {group['id']}")
    for text in c.texts:
        if text["x"] < -MARGIN or text["x"] + text["w"] > c.width + MARGIN or text["y"] < c.top - MARGIN or text["y"] + text["h"] > c.height + MARGIN:
            issues.append(f"tekst poza kadrem: '{text['text']}'")
        if text["box"]:
            x, y, w, h = text["box"]
            if text["x"] < x - 0.5 or text["x"] + text["w"] > x + w + 0.5 or text["y"] < y - 0.5 or text["y"] + text["h"] > y + h + 0.5:
                issues.append(f"tekst wychodzi poza element: '{text['text']}'")
    labels = [t for t in c.texts if t["kind"] in ("edge", "group", "note")]
    for i, a in enumerate(labels):
        for b in c.texts:
            if a is b or (b in labels and c.texts.index(b) <= c.texts.index(a)):
                continue
            if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
                issues.append(f"teksty nachodzą na siebie: '{a['text']}' i '{b['text']}'")
    if model["type"] not in SEQUENCE_TYPES:
        for edge in c.edges:
            for seg in _segments(edge["points"]):
                for node in c.nodes:
                    if node["id"] not in (edge["source"], edge["target"]) and _hits(seg, node):
                        issues.append(f"linia {edge['id']} przechodzi przez węzeł {node['id']}")
                for text in c.texts:
                    if text["kind"] == "edge" and _hits(seg, text, 0.5):
                        issues.append(f"linia {edge['id']} przecina etykietę '{text['text']}'")
    return sorted(set(issues))


LAYOUTS = (
    (LAYERED_TYPES, layout_layered), (SEQUENCE_TYPES, layout_sequence),
    (TIMELINE_TYPES, layout_timeline), (MATRIX_TYPES, layout_matrix),
)


def render(model: dict, brand: dict | None = None) -> tuple[Canvas, list[str]]:
    """Renderuje diagram; przy kolizjach automatycznie rozluźnia układ."""
    layout = next(fn for types, fn in LAYOUTS if model["type"] in types)
    best = None
    for gap in LAYOUT_GAPS:
        canvas = Canvas(build_theme(model, brand))
        layout(canvas, model, gap)
        add_header_and_notes(canvas, model)
        issues = check_scene(canvas, model)
        if best is None or len(issues) < len(best[1]):
            best = (canvas, issues)
        if not issues:
            break
    return best


def html_page(model: dict, svg: str, theme: dict) -> str:
    return (
        '<!doctype html>\n<html lang="pl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{escape(str(model["id"]))} {escape(str(model["title"]))}</title>'
        f'<style>body{{margin:0;padding:24px;background:{theme["paper"]};color:{theme["ink"]};'
        f'font-family:{theme["font"]}}}figure{{margin:0 auto;max-width:960px}}'
        'svg{max-width:100%;height:auto;display:block}figcaption{margin-top:12px;font-size:14px;font-style:italic}'
        f'</style></head><body><figure>{svg}<figcaption>{escape(str(model["caption"]))}</figcaption></figure></body></html>\n'
    )


def brand_from_template(path: str | Path) -> dict:
    """Odczytuje kolor akcentu i czcionkę z motywu szablonu .docx (bez jego modyfikacji)."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        themes = [n for n in names if re.match(r"word/theme/theme\d*\.xml$", n)]
        xml = archive.read(themes[0]).decode("utf-8", "ignore") if themes else ""
        styles = archive.read("word/styles.xml").decode("utf-8", "ignore") if "word/styles.xml" in names else ""
    brand = {}
    accent = re.search(r"<a:accent1>\s*<a:srgbClr val=\"([0-9A-Fa-f]{6})\"", xml)
    if accent:
        brand["accent"] = f"#{accent.group(1)}"
    # Czcionka akapitu podstawowego ma pierwszeństwo przed czcionką motywu.
    normal = re.search(r"<w:style\b[^>]*w:styleId=\"Normal\"[^>]*>.*?</w:style>", styles, re.DOTALL)
    defaults = re.search(r"<w:docDefaults>.*?</w:docDefaults>", styles, re.DOTALL)
    theme_font = re.search(r"<a:minorFont>\s*<a:latin typeface=\"([^\"]+)\"", xml)
    for block in (normal, defaults):
        font = re.search(r"<w:rFonts\b[^>]*w:ascii=\"([^\"]+)\"", block.group(0)) if block else None
        if font:
            brand["font"] = font.group(1)
            break
    else:
        if theme_font:
            brand["font"] = theme_font.group(1)
    return brand


def base_name(model: dict) -> str:
    return f'{model["id"]}-{model["type"]}'


def generate(path: Path, out: Path, mode: str, brand: dict | None) -> list[str]:
    try:
        model = load_model(path)
    except ModelError as error:
        return error.errors
    errors = validate_model(model, mode)
    if errors:
        return errors
    canvas, issues = render(model, brand)
    if issues:
        return issues
    out.mkdir(parents=True, exist_ok=True)
    svg = canvas.to_svg(model)
    name = base_name(model)
    (out / f"{name}.svg").write_text(svg, encoding="utf-8")
    (out / f"{name}.html").write_text(html_page(model, svg, canvas.t), encoding="utf-8")
    target = out / f"{name}.yaml"
    if path.resolve() != target.resolve():
        shutil.copyfile(path, target)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("models", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("working", "final"), default="working")
    parser.add_argument("--brand-from", type=Path, help="szablon .docx, z którego pobrać kolor i czcionkę")
    args = parser.parse_args()
    brand = brand_from_template(args.brand_from) if args.brand_from else None
    failed = 0
    for path in args.models:
        errors = generate(path, args.out, args.mode, brand)
        if errors:
            failed += 1
            print(f"BŁĄD {path.name}:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {path.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
