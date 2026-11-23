#!/usr/bin/env python3
"""Convert Deadlock's Library book layouts into Ren'Py scripts.

Run from the repo root (Python 3.8+, no extra packages):

    python tools/convert.py

Inputs (all inside the git-ignored extracted/ folder):
    extracted/decompiled/book_*.xml     decompiled Panorama book layouts
    extracted/raw/scripts/book_library.txt
    extracted/text/<book>.tsv           optional transcripts (template is generated)
    game/audio/book/**                  decompiled voice lines

Outputs:
    game/generated/vn_books.rpy         book + chapter registry (replaces placeholders)
    game/generated/<book>.rpy           one label per chapter
    extracted/text/<book>.tsv           transcript template (only if missing)
    extracted/art_checklist.md          every page image the books need
"""

import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECOMP = os.path.join(ROOT, "extracted", "decompiled")
LIBRARY_TXT = os.path.join(ROOT, "extracted", "raw", "scripts", "book_library.txt")
TEXT_DIR = os.path.join(ROOT, "extracted", "text")
AUDIO_DIR = os.path.join(ROOT, "game", "audio", "book")
GAME = os.path.join(ROOT, "game")
OUT = os.path.join(GAME, "generated")
PAGES_DIR = "images/book_pages"          # relative to game/

# layout file -> our book id and shelf info
BOOKS = [
    dict(layout="book_test", id="geist", title="The Binding of Oathkeeper",
         hero="Lady Geist", accent="#2f5d50",
         blurb="Lady Geist has to find a way to deal with Oathkeeper."),
    dict(layout="book_inferno_1", id="infernus", title="Infernus' Visual Novel",
         hero="Infernus", accent="#7a2a1d",
         blurb="Infernus has to save Jezebel's, the bar he works at, from being closed."),
    dict(layout="book_ivy_1", id="ivy", title="Ivy's Visual Novel",
         hero="Ivy", accent="#4f6b2c",
         blurb="Ivy wants to get a job to help the Arroyos."),
    dict(layout="book_holliday_1", id="holliday", title="Holliday's Visual Novel",
         hero="Holliday", accent="#8a5a2b",
         blurb="Holliday arrives in New York on the hunt for the Troubadour."),
]

# transcript speaker name (lowercase) -> Character variable in characters.rpy
SPEAKERS = {
    "lady geist": "geist", "geist": "geist",
    "infernus": "infernus",
    "ivy": "ivy",
    "holliday": "holliday",
    "oathkeeper": "oathkeeper", "johann jr.": "johann", "johann": "johann",
    "dynamo": "dynamo", "mcginnis": "mcginnis", "abrams": "abrams",
    "amber hand": "patron", "fairfax": "fairfax", "bebop": "bebop",
    "hank": "hank", "ms. shelly": "shelly",
}

IMG_PREFIX = "s2r://panorama/images/book_images/"


# ---------------------------------------------------------------- helpers

def rpy_str(s):
    """Quote a string for Ren'Py, escaping interpolation characters."""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("[", "[[").replace("{", "{{")
    return '"%s"' % s


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]


def short_id(chapter_id):
    return chapter_id[len("Chapter"):] if chapter_id.startswith("Chapter") else chapter_id


def page_path(img):
    """s2r://.../book_images/geist/x/geist_scene1_01_jpg.vtex -> images/book_pages/geist/x/geist_scene1_01.jpg"""
    rel = img[len(IMG_PREFIX):] if img.startswith(IMG_PREFIX) else img
    rel = re.sub(r"_(jpg|png)\.vtex$", r".\1", rel)
    return PAGES_DIR + "/" + rel


def page_key(img):
    return os.path.splitext(os.path.basename(page_path(img)))[0]


def index_audio():
    found = {}
    for dirpath, _, files in os.walk(AUDIO_DIR):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() in (".mp3", ".wav", ".ogg", ".opus"):
                rel = os.path.relpath(os.path.join(dirpath, f), GAME).replace(os.sep, "/")
                found[name] = rel
    return found


def load_text(book_id):
    """{page_key: [(speaker, text), ...]} from extracted/text/<book>.tsv"""
    path = os.path.join(TEXT_DIR, book_id + ".tsv")
    lines = {}
    if not os.path.exists(path):
        return lines
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            text = (row.get("text") or "").strip()
            if text:
                lines.setdefault(row["page"].strip(), []).append(
                    ((row.get("speaker") or "").strip(), text))
    return lines


def covers_from_library():
    covers = {}
    if not os.path.exists(LIBRARY_TXT):
        return covers
    txt = open(LIBRARY_TXT, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'"ClientLayoutFile"\s+"layout/books/([^".]+)\.xml"\s+"CoverImage"\s+"([^"]+)"', txt):
        covers[m.group(1)] = m.group(2).replace("file://{images}/book_images/", "")
    return covers


# ---------------------------------------------------------------- converter

class BookConverter(object):

    def __init__(self, book, audio, warnings):
        self.b = book
        self.id = book["id"]
        self.audio = audio
        self.warnings = warnings
        self.text = load_text(self.id)
        tree = ET.parse(os.path.join(DECOMP, book["layout"] + ".xml"))
        panel = tree.getroot().find("Panel")
        self.chapters = panel.find("./Panel[@id='ChapterList']").findall("BookChapter")
        self.pagelist = panel.find("BookPageList")
        self.children = {}       # chapter -> [(prompt, child chapter)]
        self.parent = {}         # chapter -> parent chapter
        self.root_chapter = None
        self.pages = []          # (chapter, page_key, image path, audio name) for checklist/template
        self.missing_audio = set()
        self._walk_links(self.pagelist)

    # chapter graph from BookPageList
    def _walk_links(self, node, parent=None, prompt=None):
        for link in node.findall("BookChapterLink"):
            cid = short_id(link.get("chapter"))
            if parent is None and self.root_chapter is None:
                self.root_chapter = cid
            if parent is not None:
                self.children.setdefault(parent, []).append((prompt, cid))
                self.parent.setdefault(cid, parent)
            for choice in link.findall("BookChoice"):
                self._walk_links(choice, cid, choice.get("prompt", "Continue"))

    def label(self, cid):
        return "vn_%s_%s" % (self.id, cid)

    # ------------------------------------------------ chapter bodies
    def emit_page(self, page, cid, out, ind):
        img = page.get("img")
        if not img:
            return
        path, key = page_path(img), page_key(img)
        snd = page.get("snd")
        audio = None
        if snd:
            name = re.sub(r"_book$", "", snd)
            audio = self.audio.get(name)
            if audio is None:
                self.missing_audio.add(name)
        # template "audio" column: file name, or the sound name if Valve removed the file
        slot = os.path.basename(audio) if audio else (re.sub(r"_book$", "", snd) + "  (missing)" if snd else "")
        self.pages.append((cid, key, path, audio or "", slot))

        out.append(ind + "$ vn_page(%s)" % rpy_str(path))
        out.append(ind + "with vn_page_transition")
        lines = self.text.get(key)
        # play the clip with the first spoken line (stage directions come first on some pages)
        voice_at = 0
        if lines:
            spoken = [n for n, (sp, _) in enumerate(lines) if sp and sp.lower() not in ("narrator", "-")]
            voice_at = spoken[0] if spoken else 0
        if audio and not lines:
            out.append(ind + "voice %s" % rpy_str(audio))
        if lines:
            for n, (speaker, text) in enumerate(lines):
                if audio and n == voice_at:
                    out.append(ind + "voice %s" % rpy_str(audio))
                var = SPEAKERS.get(speaker.lower())
                if var:
                    out.append(ind + "%s %s" % (var, rpy_str(text)))
                elif speaker and speaker.lower() not in ("narrator", "-"):
                    out.append(ind + "%s %s" % (rpy_str(speaker), rpy_str(text)))
                else:
                    out.append(ind + rpy_str(text))
        else:
            out.append(ind + "$ vn_wait()")

    def emit_nodes(self, nodes, cid, out, ind, terminal, path):
        """Emit pages and in-chapter choices. Returns True if a menu was emitted."""
        had_menu = False
        nodes = list(nodes)
        i = 0
        while i < len(nodes):
            n = nodes[i]
            if n.tag == "BookImagePage":
                self.emit_page(n, cid, out, ind)
                inner = [c for c in n if c.tag in ("BookChoice", "BookImagePage")]
                if inner:
                    had_menu |= self.emit_nodes(inner, cid, out, ind, terminal, path)
                i += 1
            elif n.tag == "BookChoice":
                run = []
                while i < len(nodes) and nodes[i].tag == "BookChoice":
                    run.append(nodes[i]); i += 1
                had_menu = True
                out.append(ind + "menu:")
                for ch in run:
                    prompt = ch.get("prompt", "Continue")
                    out.append(ind + "    %s:" % rpy_str(prompt))
                    body_start = len(out)
                    sub_path = path + [slug(prompt)]
                    sub_menu = self.emit_nodes(list(ch), cid, out, ind + "        ", terminal, sub_path)
                    if terminal and not sub_menu:
                        out.append(ind + "        $ vn_ending(%s)" % rpy_str("_".join([self.id, cid] + sub_path)))
                    if len(out) == body_start:
                        out.append(ind + "        pass")
            else:
                i += 1   # TOCEntry, BookTOCPage, BookAchievementPage: not needed in Ren'Py
        return had_menu

    def convert(self):
        out = [
            "## GENERATED by tools/convert.py from %s.xml - do not edit by hand." % self.b["layout"],
            "## Re-run the converter instead (e.g. after adding transcripts).",
            "",
        ]
        reg = []
        for chap in self.chapters:
            cid = short_id(chap.get("id"))
            toc = chap.find(".//TOCEntry")
            title = toc.get("title") if toc is not None else "Chapter " + cid
            desc = toc.get("desc") if toc is not None else ""
            kids = self.children.get(cid, [])
            terminal = not kids

            out.append("label %s:" % self.label(cid))
            out.append("    $ vn_flag(%s)" % rpy_str("%s_reached_%s" % (self.id, cid)))
            had_menu = self.emit_nodes(list(chap), cid, out, "    ", terminal, [])
            out.append("    $ vn_complete(%s, %s)" % (rpy_str(self.id), rpy_str(cid)))
            if kids:
                out.append("    menu:")
                for prompt, child in kids:
                    out.append("        %s:" % rpy_str(prompt))
                    out.append("            jump %s" % self.label(child))
                out.append('        "(Return to the Library)":')
                out.append("            return")
            else:
                if not had_menu:
                    out.append("    $ vn_ending(%s)" % rpy_str("%s_%s" % (self.id, cid)))
                out.append("    return")
            out.append("")

            is_root = cid == self.root_chapter or (self.root_chapter is None and not reg)
            reg.append((cid, title, desc, is_root))
        return "\n".join(out), reg

    def registry(self, reg):
        lines = ["    vn_register(VNBook(",
                 "        id=%s," % rpy_str(self.id),
                 "        title=%s," % rpy_str(self.b["title"]),
                 "        hero=%s," % rpy_str(self.b["hero"]),
                 "        blurb=%s," % rpy_str(self.b["blurb"]),
                 "        accent=%s," % rpy_str(self.b["accent"]),
                 "        chapters=["]
        for cid, title, desc, is_root in reg:
            flag = "None" if is_root else rpy_str("%s_reached_%s" % (self.id, cid))
            lines.append("            VNChapter(%s, %s, %s, flag=%s, desc=%s)," % (
                rpy_str(cid), rpy_str("%s · %s" % (cid, title)), rpy_str(self.label(cid)),
                flag, rpy_str(desc)))
        lines += ["        ],", "    ))", ""]
        return "\n".join(lines)

    def write_text_template(self, reset=False):
        os.makedirs(TEXT_DIR, exist_ok=True)
        path = os.path.join(TEXT_DIR, self.id + ".tsv")
        if os.path.exists(path) and not reset:
            return False
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["page", "chapter", "audio", "speaker", "text"])
            for cid, key, _, _, slot in self.pages:
                w.writerow([key, cid, slot, "", ""])
        return True


def main():
    if not os.path.isdir(DECOMP):
        sys.exit("No decompiled layouts in %s - decompile them with Source2Viewer first." % DECOMP)
    audio = index_audio()
    covers = covers_from_library()
    os.makedirs(OUT, exist_ok=True)

    registry = [
        "## GENERATED by tools/convert.py - do not edit by hand.",
        "## Real chapter graph from Deadlock's Library; overrides library_books.rpy.",
        "",
        "init -1 python:",
        "    VN_GENERATED = True",
        "",
    ]
    checklist = ["# Art checklist", "",
                 "Put each image at the path shown (relative to `game/`). "
                 "Missing pages show a placeholder; this list is regenerated on every run.", ""]
    warnings = []
    summary = []

    for book in BOOKS:
        src = os.path.join(DECOMP, book["layout"] + ".xml")
        if not os.path.exists(src):
            warnings.append("missing layout %s.xml - skipped %s" % (book["layout"], book["id"]))
            continue
        conv = BookConverter(book, audio, warnings)
        script, reg = conv.convert()
        with open(os.path.join(OUT, book["id"] + ".rpy"), "w", encoding="utf-8") as f:
            f.write(script + "\n")
        registry.append(conv.registry(reg))
        made_tpl = conv.write_text_template(reset=("--reset-text=" + book["id"]) in sys.argv)

        have = sum(1 for p in conv.pages if os.path.exists(os.path.join(GAME, p[2])))
        voiced = sum(1 for p in conv.pages if p[3])
        texted = sum(1 for p in conv.pages if p[1] in conv.text)
        summary.append("%-9s %2d chapters  %4d pages  %4d voiced  %4d with text  %4d/%d art%s" % (
            book["id"], len(reg), len(conv.pages), voiced, texted, have, len(conv.pages),
            "  (new transcript template)" if made_tpl else ""))
        for name in sorted(conv.missing_audio):
            warnings.append("%s: no audio file for sound '%s'" % (book["id"], name))

        checklist.append("## %s (%d/%d)" % (book["title"], have, len(conv.pages)))
        if book["layout"] in covers:
            checklist.append("- cover: `images/books/%s/cover.png` (Valve name: %s)" % (book["id"], covers[book["layout"]]))
        current = None
        for cid, key, path, _, _ in conv.pages:
            if cid != current:
                checklist.append("\n**Chapter %s**\n" % cid)
                current = cid
            mark = "x" if os.path.exists(os.path.join(GAME, path)) else " "
            checklist.append("- [%s] `%s`" % (mark, path))
        checklist.append("")

    with open(os.path.join(OUT, "vn_books.rpy"), "w", encoding="utf-8") as f:
        f.write("\n".join(registry) + "\n")
    with open(os.path.join(ROOT, "extracted", "art_checklist.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(checklist) + "\n")

    print("\n".join(summary))
    for w in warnings:
        print("warning:", w)
    print("wrote game/generated/, extracted/art_checklist.md, extracted/text/")


if __name__ == "__main__":
    main()
