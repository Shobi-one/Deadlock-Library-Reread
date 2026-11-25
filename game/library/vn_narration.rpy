## Wiki stage directions ("Lady Geist goes outside.") are lines with no
## speaker. Valve's pages had no text layer at all: what happened was shown in
## the art. So on pages WITH real art (Geist, Infernus) those lines are not
## shown; the page behaves like Valve's: picture, sound if any, click.
## On artless books (Ivy, Holliday) they stay, as the only scene context.
## Skipped lines are still added to the History log.

init -1 python:
    import renpy.ast as _vnn_ast

    def _vn_more_text_on_page():
        """Is there another line of dialogue on this page (before the next
        page / menu / end of chapter)?"""
        try:
            n = renpy.game.script.lookup(renpy.game.context().current).next
        except Exception:
            return False
        while n is not None:
            if isinstance(n, _vnn_ast.Say):
                return True
            if isinstance(n, (_vnn_ast.Label, _vnn_ast.Return, _vnn_ast.Menu)):
                return False
            if isinstance(n, _vnn_ast.Python) and "vn_page(" in n.code.source:
                return False
            n = n.next
        return False

    class VNNarrator(ADVCharacter):
        def __call__(self, what, interact=True, *args, **kwargs):
            if (interact and store.vn_page_art and renpy.get_screen("dl_reader")
                    and not store.vn_skipping):
                try:
                    self.add_history("adv", None, what)
                except Exception:
                    pass
                if _vn_more_text_on_page():
                    return                      # the page's dialogue follows
                renpy.pause()                   # picture (+ sound effect), click
                return
            return super(VNNarrator, self).__call__(what, interact=interact, *args, **kwargs)

define narrator = VNNarrator(None, what_italic=False)
