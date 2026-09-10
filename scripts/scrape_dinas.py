#!/usr/bin/env python3
"""
scrape_dinas.py — Auto-scrape info dari situs web resmi Dinas Pendidikan /
Kemendikdasmen (halaman HTML biasa, tanpa RSS/API), lalu catat info baru ke
spreadsheet Excel via scripts/catat_info_dinas.py.

Cara pakai:
  python scripts/scrape_dinas.py                 # pakai config default dinas_sources.json
  python scripts/scrape_dinas.py --dry-run      # hanya tampilkan item yang ketemu, jangan tulis
  python scripts/scrape_dinas.py --config path.json
  python scripts/scrape_dinas.py --list         # list sumber terkonfigurasi
  python scripts/scrape_dinas.py --self-check   # uji internal dengan fixture

Konfigurasi (dinas_sources.json) — array sumber:
  [
    {
      "name": "Disdik Provinsi",
      "url": "https://disdik.example.go.id/pengumuman",
      "container": {"tag": "div", "class": "artikel"},   # opsional; wadah tiap item
      "title":     {"tag": "a",   "class": "", "attr": "href"},  # link + teks judul
      "date":      {"tag": "span","class": "tanggal"},    # teks tanggal (opsional)
      "summary":   {"tag": "p",   "class": "ringkas"},    # ringkasan (opsional)
      "kategori":  "Surat Edaran"                          # default isi kolom Kategori
    }
  ]

- `class` dicocokkan sebagai substring (case-insensitive) dari atribut class.
- Bila `url` berawalan `file://` atau merupakan path lokal yang ada, dibaca dari
  disk (berguna untuk uji offline / fixture).
- Relative URL (href="/pengumuman/123") di-join ke base URL sumber otomatis.
- Dedup: hash (name+title+url) disimpan di .scrape_state.json di folder script.
  Item sudah pernah tercatat tidak ditulis ulang.
- Tiap item baru dikirim ke catat_info_dinas.py (stdin JSON) -> append ke xlsx.

Dependency: requests (fetch) + html.parser (stdlib). Tidak perlu bs4/pip.
"""
import sys
import os
import json
import hashlib
import subprocess
import datetime
from urllib.parse import urljoin, urlparse

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "dinas_sources.json")
STATE_FILE = os.path.join(HERE, ".scrape_state.json")
CATAT_SCRIPT = os.path.join(HERE, "catat_info_dinas.py")


# ---------------------------------------------------------------------------#
# HTML parsing (minimal, stdlib only)
# ---------------------------------------------------------------------------#
class _El:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.classes = (self.attrs.get("class") or "").split()
        self.href = self.attrs.get("href")
        self.text_parts = []
        self.children = []
        self.parent = None

    @property
    def text(self):
        return "".join(self.text_parts).strip()

    def match(self, spec):
        if not spec:
            return True
        tag = spec.get("tag")
        cls = spec.get("class")
        if tag and self.tag != tag:
            return False
        if cls:
            need = cls.lower()
            if not any(need in c.lower() for c in self.classes):
                return False
        return True

    def descendants(self):
        """Iterate all descendants (not including self)."""
        for c in self.children:
            yield c
            yield from c.descendants()


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = _El("__root__", [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        el = _El(tag, attrs)
        el.parent = self.stack[-1]
        self.stack[-1].children.append(el)
        self.stack.append(el)

    def handle_endtag(self, tag):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_data(self, data):
        if data.strip():
            self.stack[-1].text_parts.append(data)

    def all(self):
        out = []

        def walk(node):
            out.append(node)
            for c in node.children:
                walk(c)

        for c in self.root.children:
            walk(c)
        return out


def _collect_text_href(node):
    """Recursive: gabung teks + cari href pertama dalam subtree."""
    texts = []
    href = None

    def walk(n):
        nonlocal href
        if n.text:
            texts.append(n.text)
        if n.href and not href:
            href = n.href
        for c in n.children:
            walk(c)

    walk(node)
    return " ".join(texts).strip(), href


def _resolve_url(href, base_url):
    """Join relative URL ke base. Return href as-is kalau bukan HTTP."""
    if not href:
        return ""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return href
    if base_url and base_url.startswith(("http://", "https://")):
        return urljoin(base_url, href)
    return href


def _extract_items(html, source):
    parser = _Collector()
    parser.feed(html)
    elements = parser.all()

    container_spec = source.get("container")
    title_spec = source.get("title", {"tag": "a"})
    date_spec = source.get("date")
    summary_spec = source.get("summary")
    base_url = source.get("url", "")

    if container_spec:
        containers = [e for e in elements if e.match(container_spec)]
        search_scope_fn = lambda cont: cont.descendants()  # noqa: E31
    else:
        containers = [parser.root]
        # Saat tidak ada container, cari di seluruh dokumen
        search_scope_fn = lambda cont: elements  # noqa: E31

    items = []
    for cont in containers:
        scope = list(search_scope_fn(cont))

        # judul
        title_el = None
        for e in scope:
            if e.match(title_spec):
                title_el = e
                break
        if not title_el:
            continue
        title_text, href = _collect_text_href(title_el)
        if not title_text:
            continue
        href = _resolve_url(href, base_url)

        # tanggal
        date_text = ""
        if date_spec:
            for e in scope:
                if e is title_el:
                    continue
                if e.match(date_spec):
                    date_text, _ = _collect_text_href(e)
                    break

        # ringkasan
        summary_text = ""
        if summary_spec:
            for e in scope:
                if e is title_el:
                    continue
                if e.match(summary_spec):
                    summary_text, _ = _collect_text_href(e)
                    break

        items.append({
            "title": title_text,
            "url": href or "",
            "date": date_text,
            "summary": summary_text,
            "kategori": source.get("kategori", "Lainnya"),
            "sumber": source.get("name", "Dinas"),
        })
    return items


# ---------------------------------------------------------------------------#
# Fetch
# ---------------------------------------------------------------------------#
def _fetch(url, timeout=20):
    if url.startswith("file://"):
        with open(url[7:], encoding="utf-8", errors="replace") as f:
            return f.read()
    if os.path.exists(url):
        with open(url, encoding="utf-8", errors="replace") as f:
            return f.read()
    if requests is None:
        raise RuntimeError("module requests tidak tersedia untuk fetch HTTP")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; EduDevToolkit/2.4)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------------------#
# State / dedup
# ---------------------------------------------------------------------------#
def _load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"seen": []}
    return {"seen": []}


def _save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _key(item):
    base = item["sumber"] + "|" + item["title"] + "|" + item["url"]
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------#
# Write via catat_info_dinas.py
# ---------------------------------------------------------------------------#
def _write_item(item, xlsx_override=None):
    payload = {
        "isi": item["title"] + ((" — " + item["summary"]) if item["summary"] else ""),
        "tanggal_info": item["date"] or "-",
        "sumber": item["sumber"],
        "kategori": item["kategori"],
    }
    if xlsx_override:
        payload["xlsx"] = xlsx_override
    p = subprocess.run(
        [sys.executable, CATAT_SCRIPT],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True, text=True,
    )
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"ok": False, "raw": p.stdout, "err": p.stderr}


# ---------------------------------------------------------------------------#
# Main
# ---------------------------------------------------------------------------#
def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    do_list = "--list" in args
    config = DEFAULT_CONFIG
    if "--config" in args:
        i = args.index("--config")
        if i + 1 < len(args):
            config = args[i + 1]

    if not os.path.exists(config):
        print(json.dumps({"ok": False, "error": f"config tidak ada: {config}"}))
        sys.exit(1)

    with open(config, encoding="utf-8") as f:
        sources = json.load(f)

    if do_list:
        print(json.dumps([s.get("name", "?") for s in sources], ensure_ascii=False))
        return

    state = _load_state()
    seen = set(state["seen"])
    new_count = 0
    results = []

    for src in sources:
        url = src.get("url")
        if not url:
            continue
        try:
            html = _fetch(url)
        except Exception as e:
            results.append({"source": src.get("name"), "ok": False, "error": str(e)})
            continue
        items = _extract_items(html, src)
        for it in items:
            k = _key(it)
            if k in seen:
                continue
            if dry_run:
                results.append({"source": it["sumber"], "dry": True, "item": it})
                continue
            res = _write_item(it)
            seen.add(k)
            new_count += 1
            results.append({"source": it["sumber"], "written": res, "item": it})

    if not dry_run:
        state["seen"] = list(seen)
        _save_state(state)

    print(json.dumps({
        "ok": True,
        "dry_run": dry_run,
        "new_written": new_count,
        "details": results,
    }, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------#
# Self-test: jalankan dengan --self-check
# ---------------------------------------------------------------------------#
def _self_check():
    """Uji ekstraksi dengan fixture offline + relative URL join."""
    fixture_html = os.path.join(HERE, "..", "tests_fixture", "dinas_sample.html")
    fixture_config = os.path.join(HERE, "..", "tests_fixture", "dinas_sources_fixture.json")

    fixture_html = os.path.normpath(fixture_html)
    fixture_config = os.path.normpath(fixture_config)

    assert os.path.exists(fixture_html), f"fixture HTML tidak ada: {fixture_html}"
    assert os.path.exists(fixture_config), f"fixture config tidak ada: {fixture_config}"

    with open(fixture_config, encoding="utf-8") as f:
        sources = json.load(f)

    # Override URL ke path lokal
    sources[0]["url"] = fixture_html

    html = _fetch(fixture_html)
    items = _extract_items(html, sources[0])

    assert len(items) >= 1, f"harusnya ketemu >=1 item, dapat {len(items)}"

    # Cek relative URL join
    item = items[0]
    assert item["title"], "judul kosong"
    assert item["url"], "URL kosong"

    # Cek dedup
    k1 = _key(item)
    k2 = _key(item)
    assert k1 == k2, "key dedup tidak deterministik"

    # Cek resolve relative URL
    resolved = _resolve_url("/pengumuman/123", "https://disdik.example.go.id/news")
    assert resolved == "https://disdik.example.go.id/pengumuman/123", \
        f"relative URL join gagal: {resolved}"

    absolute = _resolve_url("https://other.com/page", "https://disdik.example.go.id")
    assert absolute == "https://other.com/page", f"absolute URL harus tetap: {absolute}"

    print(f"SELF-CHECK PASSED: {len(items)} item ekstrak, relative URL join benar, dedup deterministik.")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        _self_check()
    else:
        main()
