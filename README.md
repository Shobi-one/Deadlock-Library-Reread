
## Converting the original books

Everything Valve-made stays in git-ignored folders (`extracted/`, `game/generated/`,
`game/audio/`, `game/images/book_pages/`).

1. Download an old build's book archives with DepotDownloader (depot 1422456,
   e.g. manifest 3820560092668742677 from 8 Nov 2024) into `extracted/depot/`.
2. Extract `panorama/layout/books/*`, `scripts/book_library.txt` and `sounds/vo/book/*`
   from the VPKs into `extracted/raw/`.
3. Decompile with Source2Viewer-CLI:
   - layouts → `extracted/decompiled/`
   - voice lines → `game/audio/book/` (`--recursive`)
4. `python tools/convert.py` generates `game/generated/*.rpy` with the real chapter tree,
   every choice, voice lines on each page, plus:
   - `extracted/text/<book>.tsv`: transcript template (one row per page; fill
     `speaker` + `text`, add extra rows with the same `page` for more lines)
   - `extracted/art_checklist.md`: every page image and where to put it
5. Re-run the converter whenever you add text or art.
