#!/usr/bin/env python3
"""Turn a design diagram file into a component + connection list for grading.

Supports:
  .excalidraw / .json   Excalidraw scene JSON (shapes, bound text, arrows with bindings)
  .drawio / .xml        diagrams.net / draw.io (plain or compressed <diagram> payloads)
  .mmd / .md / .txt     Mermaid flowcharts (graph/flowchart; ```mermaid blocks inside markdown)

Images and PDFs are not handled here — view those directly.

Usage: parse_diagram.py <file> [--json]
"""
from __future__ import annotations

import base64
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


def clean(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " / ", s or "", flags=re.I)
    s = re.sub(r"\s*\n\s*", " / ", s.strip())
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- excalidraw
def parse_excalidraw(data: dict):
    els = [e for e in data.get("elements", []) if not e.get("isDeleted")]
    by_id = {e["id"]: e for e in els}
    label = {}
    for e in els:  # text bound to a container
        if e["type"] == "text" and e.get("containerId"):
            label[e["containerId"]] = (label.get(e["containerId"], "") + " " + (e.get("text") or "")).strip()
    shapes = {e["id"]: e for e in els if e["type"] in ("rectangle", "ellipse", "diamond", "frame", "image")}

    def name(eid):
        e = by_id.get(eid)
        if not e:
            return "?"
        return clean(label.get(eid) or e.get("name") or e.get("text") or "") or f"<unlabelled {e['type']}>"

    components = [{"id": i, "label": name(i), "shape": s["type"]} for i, s in shapes.items()]
    edges, dangling = [], []
    for e in els:
        if e["type"] not in ("arrow", "line"):
            continue
        a = (e.get("startBinding") or {}).get("elementId")
        b = (e.get("endBinding") or {}).get("elementId")
        # arrows bound to a text element -> use its container
        a = by_id.get(a, {}).get("containerId") or a
        b = by_id.get(b, {}).get("containerId") or b
        lab = clean(label.get(e["id"], ""))
        style = "dashed" if e.get("strokeStyle") in ("dashed", "dotted") else "solid"
        heads = (e.get("startArrowhead"), e.get("endArrowhead"))
        direction = "<->" if all(heads) else ("<-" if heads[0] and not heads[1] else "->")
        if e["type"] == "line" and not any(heads):
            direction = "--"
        if a and b:
            edges.append({"from": name(a), "to": name(b), "label": lab, "style": style, "dir": direction})
        else:
            dangling.append({"from": name(a) if a else None, "to": name(b) if b else None,
                             "label": lab, "style": style})
    free_text = [clean(e.get("text", "")) for e in els
                 if e["type"] == "text" and not e.get("containerId") and clean(e.get("text", ""))]
    return components, edges, dangling, free_text


# ---------------------------------------------------------------- draw.io
def _inflate(payload: str) -> str:
    raw = base64.b64decode(payload)
    xml = zlib.decompress(raw, -15).decode("utf-8")
    return urllib.parse.unquote(xml)


def parse_drawio(text: str):
    root = ET.fromstring(text)
    models = []
    for d in root.iter("diagram"):
        if list(d):
            models.extend(d.iter("mxGraphModel"))
        elif (d.text or "").strip():
            models.append(ET.fromstring(_inflate(d.text.strip())))
    if not models:
        models = list(root.iter("mxGraphModel"))
    components, edges, dangling, free_text = [], [], [], []
    for m in models:
        cells = {c.get("id"): c for c in m.iter("mxCell")}
        # draw.io wraps cells in <object>/<UserObject> when they have custom props
        for obj in list(m.iter("object")) + list(m.iter("UserObject")):
            c = obj.find("mxCell")
            if c is not None:
                c.set("id", obj.get("id"))
                c.set("value", obj.get("label", ""))
                cells[obj.get("id")] = c
        names = {}
        for cid, c in cells.items():
            if c.get("vertex") == "1":
                lab = clean(c.get("value", ""))
                style = c.get("style", "")
                if lab and style.startswith("text;"):
                    free_text.append(lab)
                    continue
                parent = cells.get(c.get("parent"))
                if parent is not None and parent.get("edge") == "1":
                    continue  # edge label
                names[cid] = lab or "<unlabelled shape>"
                shape = re.search(r"shape=([^;]+)", style)
                components.append({"id": cid, "label": names[cid],
                                   "shape": shape.group(1) if shape else style.split(";")[0] or "box"})
        edge_labels = {}
        for c in cells.values():
            p = cells.get(c.get("parent"))
            if c.get("vertex") == "1" and p is not None and p.get("edge") == "1":
                edge_labels[p.get("id")] = clean(c.get("value", ""))
        for cid, c in cells.items():
            if c.get("edge") != "1":
                continue
            style = c.get("style", "")
            lab = clean(c.get("value", "")) or edge_labels.get(cid, "")
            dashed = "dashed=1" in style
            s, t = c.get("source"), c.get("target")
            rec = {"from": names.get(s), "to": names.get(t), "label": lab,
                   "style": "dashed" if dashed else "solid",
                   "dir": "--" if "endArrow=none" in style else "->"}
            (edges if s and t else dangling).append(rec)
    return components, edges, dangling, free_text


# ---------------------------------------------------------------- mermaid
NODE = r"([A-Za-z0-9_\-]+)\s*(\[\[.*?\]\]|\[\(.*?\)\]|\(\(.*?\)\)|\[\/.*?\/\]|\[.*?\]|\(.*?\)|\{\{.*?\}\}|\{.*?\}|>.*?\])?"
ARROW = r"\s*(-->|---|-\.->|-\.-|==>|===|--x|--o|<-->|-->>|->>|-\.->)\s*(?:\|([^|]*)\|)?\s*"


def parse_mermaid(text: str):
    blocks = re.findall(r"```mermaid\s*\n(.*?)```", text, flags=re.S)
    src = "\n".join(blocks) if blocks else text
    names, components, edges = {}, [], []

    def kind(shape):
        for prefix, k in (("[(", "database"), ("[[", "subroutine/queue"), ("((", "circle"),
                          ("{{", "hexagon"), ("{", "decision"), ("(", "rounded"), ("[/", "parallelogram")):
            if shape.startswith(prefix):
                return k
        return "box"

    def reg(nid, shape):
        if shape:
            lab = clean(shape.strip("[](){}/>\\").strip('"'))
            if nid not in names or names[nid] == nid:
                if nid not in names:
                    components.append({"id": nid, "label": lab, "shape": kind(shape)})
                else:
                    for c in components:
                        if c["id"] == nid:
                            c["label"] = lab
                names[nid] = lab
        elif nid not in names:
            names[nid] = nid
            components.append({"id": nid, "label": nid, "shape": "box"})
        return names[nid]

    for line in src.splitlines():
        line = line.strip()
        if not line or line.startswith(("%%", "graph", "flowchart", "classDef", "class ", "style ",
                                         "linkStyle", "subgraph", "end", "direction")):
            continue
        # inline label form: A -- text --> B
        line = re.sub(r"--\s+([^-][^>]*?)\s+-->", r"-->|\1|", line)
        parts = re.split(ARROW, line)
        if len(parts) < 4:
            m = re.match(NODE, line)
            if m and m.group(1):
                reg(m.group(1), m.group(2))
            continue
        prev = None
        i = 0
        while i < len(parts):
            seg = parts[i].strip()
            nodes = [n.strip() for n in seg.split("&")] if seg else []
            ids = []
            for n in nodes:
                m = re.match(NODE, n)
                if m and m.group(1):
                    reg(m.group(1), m.group(2))
                    ids.append(m.group(1))
            if prev is not None and i >= 3:
                arrow, lab = parts[i - 2], parts[i - 1]
                for a in prev:
                    for b in ids:
                        edges.append({"from": names[a], "to": names[b], "label": clean(lab or ""),
                                      "style": "dashed" if "." in arrow else "solid",
                                      "dir": "--" if arrow in ("---", "-.-", "===") else "->"})
            prev = ids or prev
            i += 3
    return components, edges, [], []


# ---------------------------------------------------------------- main
def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    as_json = "--json" in sys.argv
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if suffix in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".heic"):
        sys.exit("This is an image/PDF — view it directly instead of parsing.")
    try:
        if suffix in (".excalidraw",) or (suffix == ".json" and '"excalidraw"' in text[:500]):
            kind, result = "excalidraw", parse_excalidraw(json.loads(text))
        elif suffix in (".drawio", ".xml") or text.lstrip().startswith(("<mxfile", "<mxGraphModel")):
            kind, result = "drawio", parse_drawio(text)
        else:
            kind, result = "mermaid", parse_mermaid(text)
    except Exception as exc:  # malformed input: report, don't crash the review
        sys.exit(f"Could not parse {path.name}: {exc}. Ask for a PNG export instead.")
    components, edges, dangling, free_text = result
    if as_json:
        print(json.dumps({"format": kind, "components": components, "edges": edges,
                          "unconnected_arrows": dangling, "notes": free_text}, indent=2))
        return
    print(f"Format: {kind}")
    print(f"\nComponents ({len(components)}):")
    for c in components:
        print(f"  - {c['label']}  [{c['shape']}]")
    print(f"\nConnections ({len(edges)}):")
    for e in edges:
        lab = f"  \"{e['label']}\"" if e["label"] else ""
        print(f"  - {e['from']} {e.get('dir', '->')} {e['to']}{lab}{'  (dashed)' if e['style'] == 'dashed' else ''}")
    if dangling:
        print(f"\nArrows not attached to a shape at one or both ends ({len(dangling)}) — check the image:")
        for e in dangling:
            print(f"  - from {e['from'] or '(loose)'} to {e['to'] or '(loose)'} {e['label']}")
    if free_text:
        print("\nFree text / annotations:")
        for t in free_text:
            print(f"  - {t}")
    unlabelled = sum(1 for c in components if c["label"].startswith("<unlabelled"))
    if unlabelled:
        print(f"\nNote: {unlabelled} shape(s) have no label.")


if __name__ == "__main__":
    main()
