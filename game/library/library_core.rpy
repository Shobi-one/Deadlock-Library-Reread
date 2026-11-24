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

        def __init__(self, id, title, label, requires=None, any_of=False, hidden=False, flag=None, desc="", thumb="", parent=None):
            self.id = id
            self.title = title
            self.label = label
            self.requires = list(requires or [])
            self.any_of = any_of
            self.hidden = hidden
            self.flag = flag
            self.desc = desc
            self.thumb = thumb
            self.parent = parent


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

        def cover(self, size=(360, 540)):
            return vn_img("images/books/%s/cover.png" % self.id,
                          self.accent, self.title, size)

        def logo(self):
            path = "images/books/%s/logo.png" % self.id
            return path if renpy.loadable(path) else None

        def toc_background(self):
            path = "images/books/%s/toc_bg.png" % self.id
            return path if renpy.loadable(path) else None


    ## Book registry. Filled by game/generated/vn_books.rpy (init -1) when the
    ## converter has been run, otherwise by the placeholder library_books.rpy.
    VN_BOOKS = []
    VN_GENERATED = False

    def vn_register(book):
        VN_BOOKS.append(book)

    def vn_book(book_id):
        for b in VN_BOOKS:
            if b.id == book_id:
                return b
        raise KeyError("Unknown book %r" % book_id)

    ## ---- UI strings ----
    ## Valve's own wording is extracted by tools/convert.py into the git-ignored
    ## game/generated/vn_strings.rpy (init -1); these are neutral fallbacks.
    VN_STR_DEFAULTS = {
        "library_title": "The Library",
        "library_desc": "Stories from the world of Deadlock, recovered from the game's removed Library.",
        "library_future_label": "About this port",
        "library_future_desc": "An unofficial fan preservation of Valve's unreleased visual novels, rebuilt in Ren'Py.",
        "library_available": "Available Books",
    }
    VN_STR = {}

    def vn_str(key):
        return VN_STR.get(key) or VN_STR_DEFAULTS.get(key, key)

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

    def vn_unlock_all(book_id):
        """Open every chapter of a book (sets each chapter's 'reached' flag)."""
        for c in vn_book(book_id).chapters:
            if c.flag:
                persistent.vn_flags.add(c.flag)
        renpy.restart_interaction()

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
        w, h = size
        if renpy.loadable(path):
            # scale real art to the slot (covers, sprites, backgrounds)
            return Fixed(Solid("#0b0a09"),
                         Transform(path, fit="contain", xysize=size, align=(0.5, 0.5)),
                         xysize=size)
        return Fixed(
            Solid(color, xysize=size),
            Solid("#00000055", xysize=(w - 16, h - 16), align=(0.5, 0.5)),
            Text(text, size=28, color="#f3e9d2", text_align=0.5,
                 xmaximum=w - 40, align=(0.5, 0.5)),
            xysize=size,
        )

    ## ---- Book pages (used by converted chapters) ----

    vn_page_transition = Dissolve(0.2)

    def vn_art(rel):
        if not rel:
            return None
        path = "images/book_art/" + rel
        return path if renpy.loadable(path) else None

    def vn_page(path, bg=None, who=None, intro=False):
        """Show a book page in Valve's 1700x956 reader viewer if the original
        page image exists, otherwise a scene rebuilt from wiki art."""
        global vn_page_art
        w, h = config.screen_width, config.screen_height
        vx, vy, vw, vh = DL_VIEWER
        renpy.scene()
        store.quick_menu = False        # Valve's reader controls replace it
        renpy.show_screen("dl_reader")
        vn_page_art = renpy.loadable(path)
        if vn_page_art:
            renpy.show("vn_page", what=Solid("#000000", xysize=(w, h)))
            renpy.show("vn_pageimg",
                       what=Transform(path, fit="contain", xysize=(vw, vh), xpos=vx, ypos=vy),
                       at_list=[dl_page_color_in] if intro else [])
            return
        book = (bg or "").split("_")[0]
        bg_img = vn_art(VN_BG.get(bg)) or vn_art(VN_BG.get(book))
        if bg_img:
            renpy.show("vn_bg", what=Transform(bg_img, fit="cover", xysize=(w, h)))
        else:
            renpy.show("vn_bg", what=Fixed(Solid("#14110f"),
                Solid("#c9a86a10", xysize=(w, int(h * 0.62)), yalign=1.0), xysize=(w, h)))
        char = vn_art(VN_CHAR.get(who))
        if char:
            renpy.show("vn_char", what=Transform(char, fit="contain", xysize=(int(w * 0.6), int(h * 0.92)),
                                                 xalign=0.5, yalign=1.0))

    def vn_hide_textbox():
        """True on pages whose original art already contains the dialogue."""
        return vn_page_art and not persistent.vn_textbox_over_art

    def vn_wait():
        """Wait for a click on pages that have no transcript text yet."""
        renpy.pause()

    def vn_sprite(path, color, name):
        return vn_img(path, color, name, (500, 900))

    def vn_bg(path, name):
        return vn_img(path, "#1b1f1c", name, (config.screen_width, config.screen_height))


default persistent.vn_completed = set()
default persistent.vn_endings = set()
default persistent.vn_flags = set()

## Original pages have their dialogue drawn in, so our text box hides on them
## (lines still go to History). Players can turn it back on in Preferences.
default vn_page_art = False
default persistent.vn_textbox_over_art = False

transform vn_textbox_alpha(hidden):
    alpha (0.0 if hidden else 1.0)
