## The Library - core data model, progress tracking and placeholder helpers.
##
## Everything about which books exist and how their chapters connect lives in
## library_books.rpy. This file only holds the machinery.

init -10 python:

    import re

    class VNChapter(object):
        """One playable chapter of a book.

        id        short id shown in the UI, e.g. "1", "3a", "5b"
        title     chapter title
        label     Ren'Py label that plays the chapter
        requires  chapter ids that must be finished before this one unlocks.
                  An empty list means it is always unlocked.
        any_of    if True, finishing ANY one of `requires` is enough
                  (useful for branches that merge back together)
        hidden    if True, the chapter isn't listed until it is unlocked
                  (for secret endings)
        flag      optional choice flag (set with vn_flag() inside a chapter)
                  that must also be set, so a choice decides which branch opens
        """

        def __init__(self, id, title, label, requires=None, any_of=False, hidden=False, flag=None):
            self.id = id
            self.title = title
            self.label = label
            self.requires = list(requires or [])
            self.any_of = any_of
            self.hidden = hidden
            self.flag = flag


    class VNBook(object):
        """One visual novel on the Library shelf."""

        def __init__(self, id, title, hero, blurb, chapters, accent="#c9a86a"):
            self.id = id
            self.title = title
            self.hero = hero
            self.blurb = blurb
            self.chapters = chapters
            self.accent = accent

        def chapter(self, chapter_id):
            for c in self.chapters:
                if c.id == chapter_id:
                    return c
            raise KeyError("Book %r has no chapter %r" % (self.id, chapter_id))

        def is_unlocked(self, chapter):
            if chapter.flag and chapter.flag not in persistent.vn_flags:
                return False
            if not chapter.requires:
                return True
            done = [vn_is_complete(self.id, r) for r in chapter.requires]
            return any(done) if chapter.any_of else all(done)

        def visible_chapters(self):
            return [c for c in self.chapters if not c.hidden or self.is_unlocked(c)]

        def progress(self):
            done = len([c for c in self.chapters if vn_is_complete(self.id, c.id)])
            return done, len(self.chapters)

        def cover(self):
            return vn_img("images/books/%s/cover.png" % self.id,
                          self.accent, self.title, (360, 540))


    ## Book registry, filled in by library_books.rpy (init 0).
    VN_BOOKS = []

    def vn_register(book):
        VN_BOOKS.append(book)

    def vn_book(book_id):
        for b in VN_BOOKS:
            if b.id == book_id:
                return b
        raise KeyError("Unknown book %r" % book_id)

    ## ---- Progress (persistent: survives across saves and restarts) ----

    def _key(book_id, chapter_id):
        return "%s:%s" % (book_id, chapter_id)

    def vn_is_complete(book_id, chapter_id):
        return _key(book_id, chapter_id) in persistent.vn_completed

    def vn_complete(book_id, chapter_id):
        persistent.vn_completed.add(_key(book_id, chapter_id))

    def vn_ending(ending_id):
        """Call from inside a chapter when the player reaches an ending.
        This is where cosmetic-style unlock rewards would hook in."""
        persistent.vn_endings.add(ending_id)

    def vn_flag(name):
        """Remember a choice across the whole Library, e.g. vn_flag("geist_path_a")."""
        persistent.vn_flags.add(name)

    def vn_has_flag(name):
        return name in persistent.vn_flags

    def vn_reset_progress():
        persistent.vn_completed = set()
        persistent.vn_endings = set()
        persistent.vn_flags = set()

    ## ---- Placeholder art ----
    ## Real files win automatically: drop a PNG at the expected path and the
    ## placeholder disappears.

    def vn_img(path, color, text, size):
        if renpy.loadable(path):
            return path
        w, h = size
        return Fixed(
            Solid(color, xysize=size),
            Solid("#00000055", xysize=(w - 16, h - 16), align=(0.5, 0.5)),
            Text(text, size=28, color="#f3e9d2", text_align=0.5,
                 xmaximum=w - 40, align=(0.5, 0.5)),
            xysize=size,
        )

    def vn_sprite(path, color, name):
        return vn_img(path, color, name, (500, 900))

    def vn_bg(path, name):
        return vn_img(path, "#1b1f1c", name, (config.screen_width, config.screen_height))


default persistent.vn_completed = set()
default persistent.vn_endings = set()
default persistent.vn_flags = set()
