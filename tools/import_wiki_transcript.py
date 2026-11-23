#!/usr/bin/env python3
"""Fill a book's transcript TSV from a Deadlock wiki transcription page.

    python tools/import_wiki_transcript.py geist extracted/text/geist_transcription.wiki

Save the wiki page's raw markup first (open <page>?action=raw and Ctrl+S).
Each voiced page in Valve's book plays one numbered voice clip, so the Nth spoken
line of a chapter goes on the Nth voiced page. Stage directions go on the
silent / sound-effect pages between them (or before the next line if there is
no such page). Re-run tools/convert.py afterwards.
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# wiki sections that Valve's layout plays inside another chapter (in-chapter choices)
MERGE = {"geist": {"5e": "5d", "5f": "5d", "5h": "5g"}}


def clean(s):
    s = re.sub(r"<small>.*?</small>", "", s)
    s = re.sub(r"<center>.*$", "", s)                     # trailing "Followed by" blocks
    s = re.sub(r"</?(center|small)>|<br\s*/?>", " ", s)
    s = re.sub(r"\{\{(?:PageRef|HeroIcon)\|name=[^}|]*\|alt_name=([^}|]+)[^}]*\}\}", r"\1", s)
    s = re.sub(r"\{\{(?:PageRef|HeroIcon)\|(?:name=)?([^}|]+)[^}]*\}\}", r"\1", s)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip()


SKIP_PHRASES = ("To be continued", "End of chapter", "End of route", "End of storyline",
                "Follows from", "Transcription of", "As there exist no voice lines",
                "Most of the chapters", "has no voice lines")


def parse(path, book):
    """{chapter id: [(kind, speaker, text)]}, kind = line | direction | gap"""
    merge = MERGE.get(book, {})
    chapters, cur, skip = {}, None, False
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        m = re.match(r"^(=+)\s*(.+?)\s*\1\s*$", line)
        if m:
            cm = re.match(r"(?:Chapter\s+)?(\d+[a-z]?)\b", clean(m.group(2)))
            if cm:
                cur = merge.get(cm.group(1), cm.group(1))
                chapters.setdefault(cur, [])
            skip = False
            continue
        st = line.strip()
        if cur is None or not st or st.startswith("{{"):
            continue
        if "Choice between" in st or "Featured heroes" in st or "Followed by" in st:
            head = st.split("<center>")[0] if ("Followed by" in st and "<center>" in st) else ""
            skip = "<center>" in st or st.startswith("<center>") or "'''Followed by" in st
            if "</center>" in st:
                skip = False
            if not head.strip():
                continue
            st = head
        elif skip:
            if "</center>" in st:
                skip = False
            continue
        if re.match(r"^'''If .* was chosen:'''", st) or st in ("<center>", "</center>"):
            continue
        text = clean(st)
        if not text or any(p in text for p in SKIP_PHRASES) or re.fullmatch(r"[.\s]*", text):
            continue
        if re.fullmatch(r"\(\.\.\.[)}]", text):
            chapters[cur].append(("gap", "", "")); continue
        is_direction = st.startswith("''") and not st.startswith("'''")
        sp = None if is_direction else re.match(r"^([^:!?\[\]]{1,40}):\s*(.*)$", text)
        if sp:
            who, said = sp.group(1).strip(), sp.group(2).strip()
            if re.fullmatch(r"\(\.\.\.[)}]?", said):
                chapters[cur].append(("gap", who, ""))
            elif said:
                chapters[cur].append(("line", who, said))
            continue
        chapters[cur].append(("direction", "", text))
    return chapters


def durations():
    """{audio file name: seconds} for every decompiled voice clip."""
    out = {}
    try:
        from mutagen import File as MFile
    except ImportError:
        MFile = None
        import wave
    for d, _, files in os.walk(os.path.join(ROOT, "game", "audio", "book")):
        for f in files:
            path = os.path.join(d, f)
            try:
                if MFile:
                    out[f] = MFile(path).info.length
                elif f.endswith(".wav"):
                    with wave.open(path) as w:
                        out[f] = w.getnframes() / float(w.getframerate())
            except Exception:
                pass
    return out


# speakers whose voice lines Valve removed: their lines sit on silent pages
UNVOICED = {"geist": {"infernus"}, "holliday": {"larry"}}
GAP = "\x00gap"


def align(lines, slots, unvoiced=()):
    """Best monotonic assignment of lines to consecutive page slots.
    lines: [(speaker, text)]; slots: [duration or None (silent page)].
    Returns spans[i] = (start, end) slot indices (end exclusive) or None."""
    L, P = len(lines), len(slots)
    total_c = sum(len(t) for w, t in lines if w.lower() not in unvoiced and t != GAP) or 1
    total_d = sum(d for d in slots if d) or 1
    rate = total_c / total_d                      # characters per second for this chapter
    INF = float("inf")
    best = [[INF] * (P + 1) for _ in range(L + 1)]
    back = [[None] * (P + 1) for _ in range(L + 1)]
    best[0][0] = 0.0

    def relax(i, j, ni, nj, cost, how):
        if cost < best[ni][nj]:
            best[ni][nj] = cost; back[ni][nj] = (i, j, how)

    for i in range(L + 1):
        for j in range(P + 1):
            c = best[i][j]
            if c == INF:
                continue
            if j < P:                                   # slot with no line
                relax(i, j, i, j + 1, c + (0.15 if slots[j] is None else 1.2), "skip")
            if i < L:
                relax(i, j, i + 1, j, c + 2.0, "skip")  # line with no slot
                who, text = lines[i]
                n = len(text)
                if text == GAP:                          # line with no audio and no transcript
                    if j < P:
                        relax(i, j, i + 1, j + 1, c + (0.0 if slots[j] is None else 1.5), 1)
                    continue
                silent_speaker = who.lower() in unvoiced
                if j < P and slots[j] is None:          # silent page: one line
                    relax(i, j, i + 1, j + 1, c + (0.0 if silent_speaker else 0.9), 1)
                if silent_speaker:
                    continue
                d = 0.0
                for k in range(1, 6):
                    if j + k > P or slots[j + k - 1] is None:
                        break
                    d += slots[j + k - 1]
                    err = (d * rate - n) / (n + 25.0)
                    relax(i, j, i + 1, j + k, c + err * err + 0.25 * (k - 1), k)
    spans = [None] * L
    i, j = L, P
    while i or j:
        pi, pj, how = back[i][j]
        if isinstance(how, int):
            spans[pi] = (pj, pj + how)
        i, j = pi, pj
    return spans


def split_text(text, parts):
    """Split text into len(parts) pieces, proportional to clip durations, preferring sentence ends."""
    k = len(parts)
    if k == 1:
        return [text]
    cuts = [m.end() for m in re.finditer(r"(\.\.\.|[.!?\u2026]|-)(?=\s)", text)]
    words = [m.start() for m in re.finditer(r"\s\S", text)]
    total = sum(parts) or 1
    pos, acc, pieces = 0, 0.0, []
    for x in parts[:-1]:
        acc += x
        target = len(text) * acc / total
        cand = [c for c in cuts if c > pos] or [w for w in words if w > pos]
        if not cand:
            break
        cut = min(cand, key=lambda c: abs(c - target))
        pieces.append(text[pos:cut].strip()); pos = cut
    pieces.append(text[pos:].strip())
    while len(pieces) < k:
        pieces.append("")
    return pieces


def even_spread(cps, items, cid):
    rows, P, N = [], len(cps), len(items)
    slots = {}
    for k, it in enumerate(items):
        slots.setdefault(min(P - 1, k * P // N), []).append(it)
    for n, p in enumerate(cps):
        its = [it for it in slots.get(n, []) if it[0] != "gap"]
        if not its:
            rows.append([p["page"], cid, p["audio"], "", ""])
        for kind, who, t in its:
            rows.append([p["page"], cid, p["audio"], who if kind == "line" else "narrator", t])
    return rows


def main():
    book, src = sys.argv[1], sys.argv[2]
    tsv = os.path.join(ROOT, "extracted", "text", book + ".tsv")
    rows = list(csv.DictReader(open(tsv, encoding="utf-8", newline=""), delimiter="\t"))
    pages = []
    for r in rows:
        if not pages or pages[-1]["page"] != r["page"]:
            pages.append({"page": r["page"], "chapter": r["chapter"], "audio": r["audio"]})
    wiki = parse(src, book)
    dur = durations()

    out, report = [], []
    for cid in dict.fromkeys(p["chapter"] for p in pages):
        cps = [p for p in pages if p["chapter"] == cid]
        items = list(wiki.get(cid, []))
        vo_idx = [n for n, p in enumerate(cps) if "_sfx_" not in p["audio"]]
        line_items = [n for n, it in enumerate(items) if it[0] in ("line", "gap")]
        slots = [dur.get(cps[n]["audio"]) for n in vo_idx]
        if items and not any(slots):
            # no audio at all in this chapter: spread everything evenly over the pages
            out_rows = even_spread(cps, items, cid)
            out += out_rows
            report.append("%-4s %3d pages, no audio: %d items spread evenly" % (cid, len(cps), len(items)))
            continue
        spans = align([(items[n][1], GAP if items[n][0] == "gap" else items[n][2]) for n in line_items],
                      slots, UNVOICED.get(book, ()))

        texts = {n: [] for n in range(len(cps))}     # page index -> [(speaker, text)]
        placed_lines = 0
        prev_end_page = -1
        pending_dirs = []
        li = 0
        for n, it in enumerate(items):
            if it[0] == "direction":
                pending_dirs.append(it[2]); continue
            span = spans[li]; li += 1
            if it[0] == "gap":
                if span is not None:
                    prev_end_page = vo_idx[span[1] - 1]
                continue
            if span is None:
                # no clip: attach to the previous page so the text isn't lost
                target = max(prev_end_page, 0)
                texts[target] += [("", d) for d in pending_dirs] + [(it[1], it[2])]
                pending_dirs = []; continue
            first, last = vo_idx[span[0]], vo_idx[span[1] - 1]
            # stage directions: put them on silent / sfx pages before this line if any
            gap = [g for g in range(prev_end_page + 1, first)
                   if not texts[g] and (not cps[g]["audio"] or "_sfx_" in cps[g]["audio"])]
            for d in pending_dirs:
                if gap:
                    texts[gap.pop(0)].append(("", d))
                else:
                    texts[first].append(("", d))
            pending_dirs = []
            clip_pages = [vo_idx[x] for x in range(*span)]
            pieces = split_text(it[2], [dur.get(cps[g]["audio"]) or 2.0 for g in clip_pages])
            for g, piece in zip(clip_pages, pieces):
                if piece:
                    texts[g].append((it[1], piece))
            placed_lines += 1
            prev_end_page = last
        for d in pending_dirs:
            rest = [g for g in range(prev_end_page + 1, len(cps)) if g not in vo_idx]
            texts[rest[0] if rest else max(prev_end_page, 0)].append(("", d))

        unused = sum(1 for n in vo_idx if not texts[n] and cps[n]["audio"])
        nolines = sum(1 for k, s_ in zip(line_items, spans) if s_ is None and items[k][0] == "line")
        report.append("%-4s %3d clips  %3d wiki lines  %2d clips without text  %2d lines without clip" % (
            cid, len(vo_idx), len(line_items), unused, nolines))
        for n, p in enumerate(cps):
            if not texts[n]:
                out.append([p["page"], cid, p["audio"], "", ""])
            for who, t in texts[n]:
                out.append([p["page"], cid, p["audio"], who or "narrator", t])

    with open(tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["page", "chapter", "audio", "speaker", "text"])
        w.writerows(out)
    print("\n".join(report))


if __name__ == "__main__":
    main()
