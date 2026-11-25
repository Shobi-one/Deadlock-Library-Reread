# Changelog

## v1.1 (25 Nov 2026)

### Audio
- **Dynamo's "Medieval History" line (Geist 3a, page 2) kept as Valve shipped it.**
  John Patrick Lowrie's take, the one in every Steam build (Sep, Nov and Dec 2024), cuts
  off after 2.7 s. The 25 May 2024 build (shared by Gammaton32) has the full line, but
  recorded by Fred Tatasciore, Dynamo's original voice for the Library before John
  re-recorded his lines. Mixing the two voices in one scene was rejected. Fred's take is
  saved in `extracted/backup_audio/` for a possible "Dynamo's original voice" extra.
- Compared all 526 Geist clips against the May build: 16 differ (mostly chapter 2a).
  These are most likely Dynamo's lines, recorded by Fred Tatasciore in May and
  re-recorded by John Patrick Lowrie later. The shipped (John) versions are kept.

### Reader
- **Footer rebuilt 1:1 from Valve's reader in the May 2024 build** (the Library was
  live then):
  - three hints: ESC Back, → Next, Space Play;
  - ← Back + → Next shown as a centred pair, Next alone on a chapter's first page,
    Back alone at a choice;
  - fonts from that build's own style sheets: Retail Demo 18 px labels and Retail Demo
    Bold key caps;
  - key caps #53504F, at least 32 px tall, 10 px side padding; arrow caps 53×36 with a
    white arrow;
  - exact positions (52 / 817–963 / 1716);
  - hover: brightness and 2 px lift over 0.1 s (from Valve's CSS).
- **Footer and menu hints now share one design:** the flat grey key cap and menu fonts
  from the original menu Back hint. The layout and behaviour are the May 2024 ones above,
  and the menus' ESC Back hint got the same hover.
- **Wiki stage directions hidden on pages with real art** (Geist, Infernus). Lines like
  "Lady Geist goes outside." were added by wiki editors, not Valve. Sound-effect pages
  still play their sound, and the lines stay in the History log. Ivy and Holliday keep
  them as scene context. (`library/vn_narration.rpy`)
- **Choice summaries removed.** The wiki's one-line list of a chapter's choices
  ("Take A Job As A Waitress - Take A Job As A Process Server - ...") no longer shows
  as narration right before the choice.
- **No popup right before a choice.** The last empty page of a chapter no longer
  triggers "No transcript left"; the reader goes straight to the choice.

### Dialogs
- **Confirm dialog rebuilt from Valve's generic pop-up in the May 2024 build:**
  - dark smoky panel (Valve's smoke texture at 30%) with 5 px grey bars along the top and
    bottom edges;
  - Forevs Demo 50 px title in normal case, with 20 px body text;
  - outlined pill buttons that fill on hover;
  - Valve's open animation;
  - ESC CLOSE hint removed (Valve's pop-up has none).
- Fixed the pop-up texture spilling outside the panel (also fixes the disclaimer).

### Infernus book
- **Matched pages 1–8 to the art.** The text and dialogue were one page late. The line
  "That's a great question… do you mind if I…" is split across pages 6 and 7, as in the
  art, and page 8 reads "Of course...".
- **Infernus voice extra:** the Infernus opening can play Lady Geist's voice lines from
  chapter 3b, which is the same scene, including a trimmed "Of course". Valve shipped
  this book silent, so it's an optional extra (see Extras).

### Extras
- **New Extras menu** (main menu and in-game menu) for Restoration Extras: additions Valve
  didn't ship, each off by default, with an On/Off switch and an explanation.
  (`library/vn_extras.rpy`, which replaces the earlier single Preferences toggle; that
  setting carries over.)
  - **Infernus book: Lady Geist's voice lines** (see above).
  - **Interface: 2026 style:** switches the reader hints, the pop-up dialogs and the menus'
    Back hint to the leftover versions in today's Deadlock (dimmed capitals in the
    fallback font, the paper-style pop-up with ESC CLOSE).
  - Coming soon: Dynamo's original voice (Fred Tatasciore) and Patron voices (Hidden King /
    Archmother).

### About and credits
- Added **Gammaton32** to the Thanks list (linked to their wiki page) for sharing the
  May 2024 build.
- "What's missing" now explains the cut Dynamo line and the Fred Tatasciore / John Patrick
  Lowrie recast.

### Research (no game changes yet)
- Ran the May 2024 build offline and captured the original chapter tree, reader, choice
  screen and "Insufficient Unlocks" pop-up.
- Findings from a deep dive of that build:
  - Geist's book is identical to the later version (17 chapters, 585 pages, same titles
    and choices).
  - Each chapter cost 100 key progress.
  - Ivy, Holliday and Infernus were 39-page placeholders.
  - There are no page images in this build.
  - A developer "Control Zoo" page lists Valve's type scale.
- **Found 45 unused Patron voice lines** for Geist chapters 5g, 5h and 5i, recorded by the
  Hidden King (male Patron) and the Archmother (female Patron), plus 7 `book_alt` lines.
  They're extracted to `extracted/patron_vo/`, with a side-by-side listening folder in
  `extracted/patron_compare/`. Possible future Restoration Extra.

### Known issues
- `README.md` was removed in commit 7d4c4a1 and still needs to be recreated.
- Saves made in the middle of the Infernus book's opening may resume a page off, because
  those pages were re-aligned.

## v1.0
- First playable build: the Library shelf, chapter tree and reader rebuilt in Ren'Py,
  four books, Valve's voice lines and the original page art for Lady Geist and Infernus.
