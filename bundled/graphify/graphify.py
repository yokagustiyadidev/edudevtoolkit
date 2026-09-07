#!/usr/bin/env python3
"""
graphify.py — Hermes-adapted knowledge graph builder (STDLIB ONLY, no pip/PyPI).

Adaptasi konsep Graphify-Labs/graphify untuk Hermes Agent: ubah folder berisi
kode/docs/notes menjadi knowledge graph dengan:
  - node: file + simbol (function/class/def) + heading dokumen
  - edge EXTRACTED: import/include/require/link nyata antar file
  - edge INFERRED (--mode deep): ko-okurensi kata kunci penting lintas file
  - community detection: union-find (connected components)
  - audit jujur: tiap edge ditag EXTRACTED / INFERRED / AMBIGUOUS
Output:
  graphify-out/graph.json      persistent graph (query weeks later)
  graphify-out/graph.html      interactive (SVG, search, filter by community)
  graphify-out/GRAPH_REPORT.md god nodes, communities, suggested questions

Usage:
  python graphify.py [path] [--mode deep] [--no-viz] [--json-only]
                     [--update] [--cluster-only] [--out DIR]

Dependency: Python stdlib only.
"""
import sys
import os
import re
import json
import hashlib
import datetime
import html
from pathlib import Path
from collections import defaultdict, Counter

# ---------------------------------------------------------------------------
# Config per extension
# ---------------------------------------------------------------------------
CODE_EXT = {
    ".py": {"sym": r"^\s*(?:def|class)\s+([A-Za-z_]\w*)", "imp": [
        r"^\s*import\s+([\w\.]+)",
        r"^\s*from\s+([\w\.]+)\s+import",
    ]},
    ".php": {"sym": r"(?:function\s+([A-Za-z_]\w*)|class\s+([A-Za-z_]\w*)|(?:public|private|protected)?\s*function\s+([A-Za-z_]\w*))", "imp": [
        r"^\s*require(?:_once)?\s*\(?['\"]([^'\"]+)['\"]",
        r"^\s*include(?:_once)?\s*\(?['\"]([^'\"]+)['\"]",
        r"^\s*use\s+([\\A-Za-z_]\w*)",
    ]},
    ".js": {"sym": r"(?:function\s+([A-Za-z_]\w*)|const\s+([A-Za-z_]\w*)\s*=|class\s+([A-Za-z_]\w*))", "imp": [
        r"import\s+.+\s+from\s+['\"]([^'\"]+)['\"]",
        r"require\(['\"]([^'\"]+)['\"]\)",
    ]},
    ".ts": {"sym": r"(?:function\s+([A-Za-z_]\w*)|class\s+([A-Za-z_]\w*)|const\s+([A-Za-z_]\w*)\s*[:=])", "imp": [
        r"import\s+.+\s+from\s+['\"]([^'\"]+)['\"]",
    ]},
    ".go": {"sym": r"(?:func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)|type\s+([A-Za-z_]\w*)\s+struct)", "imp": [
        r"^\s*import\s+\(\s*([\w\.\/]+)",
        r"^\s*import\s+[\"']([^\"']+)[\"']",
    ]},
    ".java": {"sym": r"(?:public|private|protected)?\s*(?:static\s+)?(?:void|int|String|class|boolean)\s+([A-Za-z_]\w*)\s*\(", "imp": [
        r"^\s*import\s+([\w\.]+);",
    ]},
    ".sql": {"sym": r"(?:CREATE\s+TABLE\s+([A-Za-z_]\w*)|CREATE\s+PROCEDURE\s+([A-Za-z_]\w*))", "imp": []},
    ".rb": {"sym": r"(?:def\s+([A-Za-z_]\w*)|class\s+([A-Za-z_]\w*))", "imp": [
        r"require\s+['\"]([^'\"]+)['\"]",
    ]},
    ".cs": {"sym": r"(?:public|private|protected)?\s*(?:static\s+)?(?:void|int|string|class|bool)\s+([A-Za-z_]\w*)\s*\(", "imp": [
        r"using\s+([A-Za-z_\.]+);",
    ]},
}
DOC_EXT = {".md", ".txt", ".rst"}
SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv",
             "graphify-out", ".idea", ".vscode", "tests_fixture"}
SKIP_FILES = {".env", ".env.example", "*.key", "*.pem", "*.png", "*.jpg", "*.jpeg",
              "*.gif", "*.pdf", "*.zip", "*.exe", "*.dll", "uv.lock"}
SENSITIVE_HINT = {".env", "credentials", "secret", "password", ".key", ".pem"}

# ---------------------------------------------------------------------------
# Detect
# ---------------------------------------------------------------------------
def detect(root):
    files = defaultdict(list)
    skipped_sensitive = 0
    total_words = 0
    for p in Path(root).rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        parts = set(rel.parts)
        if parts & SKIP_DIRS:
            continue
        ext = p.suffix.lower()
        if ext in CODE_EXT:
            files["code"].append(str(p))
            try:
                total_words += len(p.read_text(errors="ignore").split())
            except Exception:
                pass
        elif ext in DOC_EXT:
            files["docs"].append(str(p))
            try:
                total_words += len(p.read_text(errors="ignore").split())
            except Exception:
                pass
        if any(s in p.name.lower() for s in SENSITIVE_HINT):
            skipped_sensitive += 1
    return files, skipped_sensitive, total_words


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------
def _resolve_target(base, target):
    """Coba resolve import target ke file nyata di sekitar base."""
    # buang quote, normalisasi
    t = target.strip().strip("'\"")
    if not t or t.startswith(".") is False and "/" not in t and "\\" not in t and "." not in t:
        pass
    # heuristik: cari file dengan nama dasar == t (tanpa ext) di tree
    base_dir = Path(base).parent if Path(base).is_file() else Path(base)
    cand = []
    name = t.split("/")[-1].split("\\")[-1].split(".")[0]
    if not name:
        return None
    for ext in list(CODE_EXT) + list(DOC_EXT):
        p = base_dir / (name + ext)
        if p.exists():
            cand.append(str(p))
    if cand:
        return cand[0]
    return None  # unresolved -> tetap simpan sebagai node eksternal


def extract(root, files, deep):
    nodes = {}      # id -> {label, type, file, kind}
    edges = []      # {src, dst, kind, detail}
    file_index = {}  # path -> file_id

    def add_node(nid, label, ntype, fpath, kind="file"):
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": label, "type": ntype,
                          "file": fpath, "kind": kind}
        return nid

    # 1) file nodes
    for f in files["code"] + files["docs"]:
        fid = "F:" + f
        add_node(fid, Path(f).name, "file", f)
        file_index[f] = fid

    # 2) symbol / heading nodes + EXTRACTED edges (imports, links)
    keyword_index = defaultdict(list)  # kata kunci -> list file
    for f in files["code"]:
        text = Path(f).read_text(errors="ignore")
        ext = Path(f).suffix.lower()
        cfg = CODE_EXT.get(ext, {})
        fid = file_index[f]
        # symbols
        sym_re = cfg.get("sym")
        if sym_re:
            for m in re.finditer(sym_re, text, re.MULTILINE):
                name = next((g for g in m.groups() if g), None)
                if name:
                    sid = f + "::" + name
                    add_node(sid, name, "symbol", f, "symbol")
                    edges.append({"src": fid, "dst": sid, "kind": "EXTRACTED",
                                  "detail": "defines"})
        # imports
        for imp_re in cfg.get("imp", []):
            for m in re.finditer(imp_re, text, re.MULTILINE):
                tgt = m.group(1)
                if not tgt:
                    continue
                resolved = _resolve_target(f, tgt)
                if resolved and resolved in file_index:
                    edges.append({"src": fid, "dst": file_index[resolved],
                                  "kind": "EXTRACTED", "detail": "imports " + tgt})
                else:
                    # external / unresolved module
                    eid = "X:" + tgt
                    add_node(eid, tgt, "external", tgt, "external")
                    edges.append({"src": fid, "dst": eid, "kind": "EXTRACTED",
                                  "detail": "imports " + tgt})
        if deep:
            # keyword = CamelCase / TitleCase / UPPER_SNAKE
            for kw in re.findall(r"\b([A-Z][A-Za-z0-9]{3,}|[A-Z]{2,}_[A-Z_]+)\b", text):
                keyword_index[kw].append(fid)

    # docs: headings + links
    for f in files["docs"]:
        text = Path(f).read_text(errors="ignore")
        fid = file_index[f]
        for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE):
            heading = m.group(2).strip()
            hid = f + "#" + heading
            add_node(hid, heading, "heading", f, "heading")
            edges.append({"src": fid, "dst": hid, "kind": "EXTRACTED",
                          "detail": "contains"})
        for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            tgt = m.group(1)
            if tgt.startswith("http"):
                eid = "U:" + tgt
                add_node(eid, tgt, "url", tgt, "url")
                edges.append({"src": fid, "dst": eid, "kind": "EXTRACTED",
                              "detail": "links"})
            elif tgt.endswith((".md", ".txt")):
                resolved = _resolve_target(f, tgt)
                if resolved and resolved in file_index:
                    edges.append({"src": fid, "dst": file_index[resolved],
                                  "kind": "EXTRACTED", "detail": "links"})

    # 3) INFERRED edges (deep mode): keyword co-occurrence lintas file
    if deep:
        for kw, fids in keyword_index.items():
            fids = list(set(fids))
            if len(fids) >= 2:
                for i in range(len(fids)):
                    for j in range(i + 1, len(fids)):
                        edges.append({"src": fids[i], "dst": fids[j],
                                      "kind": "INFERRED",
                                      "detail": "shared keyword " + kw})

    # dedup edges
    seen = set()
    unique = []
    for e in edges:
        key = (e["src"], e["dst"], e["kind"], e["detail"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)
    return list(nodes.values()), unique


# ---------------------------------------------------------------------------
# Community detection (union-find)
# ---------------------------------------------------------------------------
def communities(nodes, edges):
    parent = {n["id"]: n["id"] for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in edges:
        if e["kind"] == "EXTRACTED":  # hanya edge pasti yg mengikat komunitas
            union(e["src"], e["dst"])
    comm = defaultdict(list)
    for nid in parent:
        comm[find(nid)].append(nid)
    # map node->comm id
    node_comm = {}
    comm_list = []
    for i, (root, members) in enumerate(comm.items(), 1):
        cid = "C" + str(i)
        for m in members:
            node_comm[m] = cid
        comm_list.append({"id": cid, "size": len(members), "members": members})
    return node_comm, comm_list


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write_json(out, nodes, edges, comm_list, meta):
    data = {"meta": meta, "nodes": nodes, "edges": edges,
            "communities": comm_list}
    (out / "graph.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                    encoding="utf-8")


def write_html(out, nodes, edges, node_comm, comm_list):
    node_json = json.dumps(nodes, ensure_ascii=False)
    edge_json = json.dumps(edges, ensure_ascii=False)
    comm_json = json.dumps(comm_list, ensure_ascii=False)
    nc_json = json.dumps(node_comm, ensure_ascii=False)
    n_comm = len(comm_list)

    html_doc = """<!DOCTYPE html>
<html lang="id"><head><meta charset="utf-8">
<title>graphify output</title>
<style>
 body{font-family:system-ui,sans-serif;margin:0;background:#0f172a;color:#e2e8f0}
 #bar{padding:8px;background:#1e293b;position:sticky;top:0;z-index:10}
 input{padding:6px;width:300px;border-radius:4px;border:1px solid #334155;background:#0f172a;color:#e2e8f0}
 svg{width:100vw;height:90vh;display:block}
 .node{cursor:pointer}
 .edge{stroke:#334155;stroke-width:1}
 .edge.hl{stroke:#38bdf8;stroke-width:2}
 text{font-size:10px;fill:#cbd5e1;pointer-events:none}
 #info{padding:10px;max-width:600px}
</style></head>
<body>
<div id="bar">
 <input id="q" placeholder="cari node / komunitas...">
 <span id="stat"></span>
</div>
<svg id="svg"></svg>
<div id="info">Klik node untuk detail. Scroll = zoom.</div>
<script>
const NODES=__NODE__; const EDGES=__EDGE__; const COMM=__COMM__; const NC=__NC__;
const svg=document.getElementById('svg');
const groups={};
NODES.forEach(n=>{const c=NC[n.id]||'C0';(groups[c]=groups[c]||[]).push(n);});
const commIds=Object.keys(groups);
const R=Math.min(svg.clientWidth,svg.clientHeight)/2 - 60;
const cx=svg.clientWidth/2, cy=svg.clientHeight/2;
const pos={};
commIds.forEach((cid,i)=>{
  const ang=(i/commIds.length)*2*Math.PI;
  const ccx=cx+Math.cos(ang)*R*0.7, ccy=cy+Math.sin(ang)*R*0.7;
  const members=groups[cid]; const r=Math.max(20,Math.min(120,members.length*7));
  members.forEach((n,j)=>{
    const a=(j/members.length)*2*Math.PI;
    pos[n.id]={x:ccx+Math.cos(a)*r, y:ccy+Math.sin(a)*r, comm:cid};
  });
});
// edges
const edgeEls=[];
EDGES.forEach(e=>{
  const a=pos[e.src], b=pos[e.dst]; if(!a||!b)return;
  const l=document.createElementNS('http://www.w3.org/2000/svg','line');
  l.setAttribute('x1',a.x);l.setAttribute('y1',a.y);l.setAttribute('x2',b.x);l.setAttribute('y2',b.y);
  l.setAttribute('class','edge'); l.dataset.s=e.src; l.dataset.d=e.dst;
  svg.appendChild(l); edgeEls.push(l);
});
// nodes
const nodeEls={};
NODES.forEach(n=>{
  const p=pos[n.id]; if(!p)return;
  const g=document.createElementNS('http://www.w3.org/2000/svg','g');
  g.setAttribute('class','node'); g.dataset.id=n.id;
  const rad=n.type==='file'?7:(n.type==='external'?5:4);
  const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('cx',p.x);c.setAttribute('cy',p.y);c.setAttribute('r',rad);
  c.setAttribute('fill', n.type==='file'?'#38bdf8':n.type==='symbol'?'#a78bfa':n.type==='heading'?'#34d399':'#64748b');
  g.appendChild(c);
  const t=document.createElementNS('http://www.w3.org/2000/svg','text');
  t.setAttribute('x',p.x+rad+2);t.setAttribute('y',p.y+3);t.textContent=n.label;
  g.appendChild(t);
  g.addEventListener('click',()=>showInfo(n));
  svg.appendChild(g); nodeEls[n.id]=g;
});
document.getElementById('stat').textContent=NODES.length+' nodes, '+EDGES.length+' edges, '+commIds.length+' communities';
function showInfo(n){
  const rel=EDGES.filter(e=>e.src===n.id||e.dst===n.id);
  let html='<b>'+n.label+'</b> ('+n.type+')<br>file: '+n.file+'<br>edges: '+rel.length+'<br>';
  rel.slice(0,10).forEach(e=>{html+=e.kind+' '+e.detail+' &rarr; '+(e.src===n.id?e.dst:e.src)+'<br>';});
  document.getElementById('info').innerHTML=html;
  edgeEls.forEach(l=>{l.classList.remove('hl');});
  rel.forEach(e=>{edgeEls.forEach(l=>{if((l.dataset.s===e.src&&l.dataset.d===e.dst)||(l.dataset.s===e.dst&&l.dataset.d===e.src))l.classList.add('hl');});});
}
document.getElementById('q').addEventListener('input',ev=>{
  const q=ev.target.value.toLowerCase();
  NODES.forEach(n=>{const g=nodeEls[n.id]; if(!g)return; g.style.display=(!q||n.label.toLowerCase().includes(q)||(NC[n.id]||'').toLowerCase().includes(q))?'':'none';});
});
</script>
</body></html>"""
    html_doc = (html_doc
                .replace("__NODE__", node_json)
                .replace("__EDGE__", edge_json)
                .replace("__COMM__", comm_json)
                .replace("__NC__", nc_json))
    (out / "graph.html").write_text(html_doc, encoding="utf-8")
def write_report(out, nodes, edges, comm_list, node_comm, meta):
    deg = Counter()
    for e in edges:
        deg[e["src"]] += 1
        deg[e["dst"]] += 1
    by_deg = sorted(deg.items(), key=lambda x: -x[1])[:10]
    god = [{"label": next((n["label"] for n in nodes if n["id"] == i), i),
            "degree": d} for i, d in by_deg]
    nid2node = {n["id"]: n for n in nodes}
    lines = ["# GRAPH_REPORT", "",
             f"Dibuat: {meta['generated']} | mode: {meta['mode']}",
             f"Total: {len(nodes)} node, {len(edges)} edge, {len(comm_list)} komunitas", ""]
    lines.append("## God Nodes (degree tertinggi)")
    for g in god:
        lines.append(f"- {g['label']} — {g['degree']} edge")
    lines.append("")
    lines.append("## Komunitas (terbesar dulu)")
    for c in sorted(comm_list, key=lambda x: -x["size"])[:10]:
        members = [nid2node[m]["label"] for m in c["members"][:8] if m in nid2node]
        lines.append(f"- {c['id']} ({c['size']}): " + ", ".join(members))
    lines.append("")
    lines.append("## Audit Edge")
    ek = Counter(e["kind"] for e in edges)
    for k, v in ek.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Pertanyaan yang bisa dijawab")
    if god:
        lines.append(f"- Apa peran '{god[0]['label']}' dalam sistem?")
        lines.append(f"- Bagaimana '{god[0]['label']}' terhubung ke modul lain?")
    lines.append("- Komunitas mana yang terisolasi (tidak ada edge EXTRACTED ke luar)?")
    (out / "GRAPH_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    path = "."
    mode = "normal"
    no_viz = False
    json_only = False
    out_dir = "graphify-out"
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--mode",) and i + 1 < len(args):
            mode = args[i + 1]; i += 2; continue
        if a == "--no-viz":
            no_viz = True; i += 1; continue
        if a == "--json-only":
            json_only = True; i += 1; continue
        if a == "--out" and i + 1 < len(args):
            out_dir = args[i + 1]; i += 2; continue
        if not a.startswith("-"):
            path = a
        i += 1

    root = Path(path).resolve()
    if not root.exists():
        print(f"Path tidak ada: {root}")
        sys.exit(1)

    print(f"Scan: {root}")
    files, skipped_sens, words = detect(root)
    n_code = len(files["code"]); n_doc = len(files["docs"])
    print(f"Corpus: {n_code + n_doc} file · ~{words} kata")
    if skipped_sens:
        print(f"(lewati {skipped_sens} file sensitif)")
    if n_code + n_doc == 0:
        print("No supported files found.")
        sys.exit(0)

    nodes, edges = extract(root, files, deep=(mode == "deep"))
    node_comm, comm_list = communities(nodes, edges)

    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    meta = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": str(root),
        "mode": mode,
        "files": n_code + n_doc,
    }
    write_json(out, nodes, edges, comm_list, meta)
    print(f"graph.json: {len(nodes)} node, {len(edges)} edge")
    if not json_only and not no_viz:
        write_html(out, nodes, edges, node_comm, comm_list)
        print("graph.html: interaktif (buka di browser)")
    write_report(out, nodes, edges, comm_list, node_comm, meta)
    print(f"GRAPH_REPORT.md: {len(comm_list)} komunitas")
    print(f"Selesai -> {out.resolve()}")


if __name__ == "__main__":
    main()
