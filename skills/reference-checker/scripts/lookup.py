#!/usr/bin/env python3
"""Look up references in Crossref and OpenAlex and print what the records say.

usage: python3 lookup.py refs.bib            # BibTeX file
       python3 lookup.py refs.txt            # one reference per line or paragraph
       python3 lookup.py --doi 10.1038/nature14539
       python3 lookup.py "LeCun, Bengio, Hinton (2015). Deep learning. Nature 521, 436-444."
       add --json for machine-readable output

For every reference it prints the given data and the records found:
  - with a DOI: the Crossref record for that DOI, how well its title matches the
    given title (a low match means the DOI belongs to a different work), print and
    online year, volume, issue, pages / article number, type
  - always: the best Crossref matches for the full reference, and OpenAlex matches
    for the title (OpenAlex also covers arXiv, conference papers and many books)
  - retractions, corrections and expressions of concern (Crossref "updated-by",
    Retraction Watch data; OpenAlex is_retracted)

It only collects evidence; the rating stays with you. A missing record is not proof
of a fabricated reference (books, reports, theses, patents are often not in
Crossref) - search the web for those. Python standard library only.
"""
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

UA = "reference-checker-skill/1.0 (https://github.com/LiaScript/skills)"
LATEX = {r'\"a': "ä", r'\"o': "ö", r'\"u': "ü", r'\"A': "Ä", r'\"O': "Ö", r'\"U': "Ü",
         r"\ss": "ß", r"\&": "&", "--": "–", r"\'e": "é", r"\`e": "è", r"\'a": "á"}


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1 + attempt)
        except OSError:
            time.sleep(1 + attempt)
    return None


def delatex(s):
    s = re.sub(r"\{\\(['\"`^~])\{?(\w)\}?\}", r"\\\1\2", s)
    for k, v in LATEX.items():
        s = s.replace(k, v)
    return re.sub(r"[{}]", "", s).strip()


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def similarity(a, b):
    a, b = " ".join(norm(a)), " ".join(norm(b))
    if not a or not b:
        return None
    b = re.sub(r"^retracted ", "", b)
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 2)


# ------------------------------------------------------------------ input

def parse_bibtex(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        i, depth = m.end(), 1
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body, fields = text[m.end():i - 1], {}
        for f in re.finditer(r"(\w+)\s*=\s*", body):
            j = f.end()
            if j < len(body) and body[j] == "{":
                d, k = 1, j + 1
                while k < len(body) and d:
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                value = body[j + 1:k - 1]
            elif j < len(body) and body[j] == '"':
                k = body.index('"', j + 1)
                value = body[j + 1:k]
            else:
                value = re.match(r"[^,\n]*", body[j:]).group(0)
            fields.setdefault(f.group(1).lower(), delatex(" ".join(value.split())))
        fields["_key"], fields["_type"] = m.group(2), m.group(1).lower()
        entries.append(fields)
    return entries


def parse_text(text):
    parts = re.split(r"\n\s*\n", text.strip())
    if len(parts) == 1:
        parts = text.strip().splitlines()
    refs = []
    for p in parts:
        p = re.sub(r"^\s*(\[\d+\]|\d+[.)])\s*", "", " ".join(p.split()))
        if len(p) > 15:
            refs.append({"_raw": p})
    return refs


def given(ref):
    if "_raw" in ref:
        raw = ref["_raw"]
        doi = re.search(r"10\.\d{4,9}/[^\s\"<>]+", raw)
        title = re.search(r"\(\d{4}[a-z]?\)\.?\s*(.+?)\.\s", raw)
        return {"text": raw, "doi": doi.group(0).rstrip(".") if doi else None,
                "title": title.group(1) if title else None}
    text = ", ".join(ref.get(k, "") for k in ("author", "year", "title", "journal", "booktitle",
                                               "volume", "pages") if ref.get(k))
    return {"text": text, "doi": (ref.get("doi") or "").replace("https://doi.org/", "") or None,
            "title": ref.get("title"), "key": ref.get("_key")}


# ------------------------------------------------------------------ records

def year_of(m, key):
    parts = (m.get(key) or {}).get("date-parts") or [[None]]
    return parts[0][0]


def crossref_summary(m, given_title):
    updates = [{"type": u.get("type"), "notice": u.get("DOI"),
                "date": "-".join(str(x) for x in (u.get("updated") or {}).get("date-parts", [[None]])[0] if x)}
               for u in m.get("updated-by") or []]
    return {
        "doi": m.get("DOI"),
        "title": (m.get("title") or [""])[0],
        "title_match": similarity(given_title, (m.get("title") or [""])[0]) if given_title else None,
        "authors": [" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name")
                    for a in m.get("author") or []],
        "container": (m.get("container-title") or [None])[0],
        "year_print": year_of(m, "published-print"),
        "year_online": year_of(m, "published-online"),
        "year_issued": year_of(m, "issued"),
        "volume": m.get("volume"), "issue": m.get("issue"),
        "pages": m.get("page"), "article_number": m.get("article-number"),
        "type": m.get("type"), "url": f"https://doi.org/{m.get('DOI')}",
        "updated_by": updates,
    }


def openalex_summary(w, given_title):
    src = ((w.get("primary_location") or {}).get("source") or {})
    b = w.get("biblio") or {}
    pages = "-".join(x for x in (b.get("first_page"), b.get("last_page")) if x) or None
    return {
        "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
        "title": w.get("title"),
        "title_match": similarity(given_title, w.get("title")) if given_title else None,
        "authors": [a["author"]["display_name"] for a in w.get("authorships") or []],
        "container": src.get("display_name"), "year": w.get("publication_year"),
        "volume": b.get("volume"), "issue": b.get("issue"), "pages": pages,
        "type": w.get("type"), "is_retracted": w.get("is_retracted"),
        "url": (w.get("primary_location") or {}).get("landing_page_url") or w.get("id"),
    }


def look_up(ref):
    g = given(ref)
    out = {"given": g, "doi_record": None, "crossref_matches": [], "openalex_matches": []}
    if g["doi"]:
        r = get("https://api.crossref.org/works/" + urllib.parse.quote(g["doi"], safe="/()"))
        if r:
            out["doi_record"] = crossref_summary(r["message"], g["title"])
            w = get("https://api.openalex.org/works/doi:" + g["doi"])
            if w:
                out["doi_record"]["openalex_is_retracted"] = w.get("is_retracted")
        else:
            out["doi_record"] = {"error": "DOI not found in Crossref"}
    r = get("https://api.crossref.org/works", {"query.bibliographic": g["text"][:500], "rows": 3})
    for m in (r or {}).get("message", {}).get("items", []):
        s = crossref_summary(m, g["title"])
        s["score"] = round(m.get("score", 0), 1)
        out["crossref_matches"].append(s)
    if g["title"]:
        r = get("https://api.openalex.org/works", {"search": g["title"][:300], "per-page": 2})
        out["openalex_matches"] = [openalex_summary(w, g["title"]) for w in (r or {}).get("results", [])]
    return out


# ------------------------------------------------------------------ output

def flags(rec):
    f = []
    if rec.get("updated_by"):
        f += [f"{u['type'].upper()} {u['date']} (notice {u['notice']})" for u in rec["updated_by"]]
    if rec.get("is_retracted") or rec.get("openalex_is_retracted"):
        f.append("RETRACTED (OpenAlex)")
    return f


def line(rec):
    pages = rec.get("pages") or (f"art. {rec['article_number']}" if rec.get("article_number") else None)
    year = rec.get("year") or rec.get("year_print") or rec.get("year_issued")
    if rec.get("year_online") and rec.get("year_online") != year:
        year = f"{year} (online {rec['year_online']})"
    authors = rec.get("authors") or []
    a = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
    vol = f"{rec.get('volume') or ''}{'(' + rec['issue'] + ')' if rec.get('issue') else ''}"
    return f"{a} | {year} | {rec.get('title')} | {rec.get('container')} | {vol} | {pages} | {rec.get('type')}"


def show(n, res):
    g = res["given"]
    print(f"\n[{n}] {g.get('key') or ''} {g['text'][:160]}")
    d = res["doi_record"]
    if d:
        if "error" in d:
            print(f"  DOI {g['doi']}: {d['error']}")
        else:
            print(f"  DOI {d['doi']}: title match {d['title_match']}")
            print(f"    {line(d)}")
            for f in flags(d):
                print(f"    !! {f}")
    print("  Crossref best matches:")
    for m in res["crossref_matches"]:
        print(f"    score {m['score']}, title match {m['title_match']}: {line(m)} | {m['url']}")
        for f in flags(m):
            print(f"      !! {f}")
    if res["openalex_matches"]:
        print("  OpenAlex title matches:")
        for m in res["openalex_matches"]:
            print(f"    title match {m['title_match']}: {line(m)} | {m['doi'] or m['url']}")
            for f in flags(m):
                print(f"      !! {f}")


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if argv[0] == "--doi":
        refs = [{"_raw": d} for d in argv[1:]]
    elif len(argv) == 1 and re.search(r"\.(bib|txt|md)$", argv[0]):
        text = open(argv[0], encoding="utf-8").read()
        refs = parse_bibtex(text) if "@" in text and re.search(r"@\w+\s*\{", text) else parse_text(text)
    else:
        refs = [{"_raw": a} for a in argv]
    results = []
    for n, ref in enumerate(refs, 1):
        res = look_up(ref)
        results.append(res)
        if not as_json:
            show(n, res)
        time.sleep(0.2)
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
