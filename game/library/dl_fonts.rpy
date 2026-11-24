## Deadlock's UI fonts (loaded from the git-ignored game/fonts folder).
## Defined early (init -3) so gui.rpy can use them for every menu and textbox.
## "serif" = ForevsDemo, "sans" = RetailDemo, body = Reaver. The demo fonts only
## contain letters, digits, space and . , so all other characters use Reaver.

init -3 python:

    def _dl_font(path, fallback="DejaVuSans.ttf"):
        return path if renpy.loadable(path) else fallback

    def _dl_demo_group(demo, filler):
        if not (renpy.loadable(demo) and renpy.loadable(filler)):
            return filler if renpy.loadable(filler) else "DejaVuSans.ttf"
        g = FontGroup()
        for a, b in ((0x20, 0x20), (0x2c, 0x2c), (0x2e, 0x2e),
                     (0x30, 0x39), (0x41, 0x5a), (0x61, 0x7a)):
            g.add(demo, a, b)
        g.add(filler, None, None)
        return g

    DL_BODY     = _dl_font("fonts/reaver-regular.otf")
    DL_SEMIBOLD = _dl_font("fonts/reaver-semibold.otf")
    DL_BOLD     = _dl_font("fonts/reaver-bold.otf")
    DL_SERIF    = _dl_demo_group("fonts/forevsdemo-bold.otf", "fonts/reaver-bold.otf")
    DL_SANS     = _dl_demo_group("fonts/retaildemo-bold.otf", "fonts/reaver-bold.otf")
    DL_SANS_REG = _dl_demo_group("fonts/retaildemo-regular.otf", "fonts/reaver-regular.otf")
