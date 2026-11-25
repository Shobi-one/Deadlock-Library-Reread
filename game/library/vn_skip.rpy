## "No transcript left": on books without page art, when the rest of a chapter
## has no dialogue, ask once whether to skip to the chapter's end (its choices /
## the chapter select). Worked out at runtime from the loaded script (Ren'Py's
## AST), so it also works in builds without .rpy files.

default vn_skipping = False
default vn_skip_declined = set()
default vn_cur_scene = None

init 5 python:
    import re as _vn_re
    import renpy.ast as _vn_ast

    _vn_page_show = vn_page
    _vn_wait_real = vn_wait
    _vn_transition_saved = vn_page_transition

    def vn_start_skip():
        store.vn_skipping = True
        store.vn_page_transition = None
        renpy.music.set_volume(0.0, delay=0, channel="voice")

    def vn_stop_skip():
        if store.vn_skipping:
            store.vn_skipping = False
            store.vn_page_transition = _vn_transition_saved
            renpy.music.set_volume(1.0, delay=0, channel="voice")

    def _vn_dialogue_left():
        """True if the current chapter still has a line of dialogue after the
        statement being run now (walks the loaded script, stops at the
        chapter's end: return / next label / its choice menu)."""
        try:
            n = renpy.game.script.lookup(renpy.game.context().current).next
        except Exception:
            return True
        while n is not None and not isinstance(n, (_vn_ast.Label, _vn_ast.Return, _vn_ast.Menu)):
            if isinstance(n, _vn_ast.Say):
                return True
            n = n.next
        return False

    def _vn_empty_pages_left():
        """True if another empty page (vn_wait) follows in this chapter."""
        try:
            n = renpy.game.script.lookup(renpy.game.context().current).next
        except Exception:
            return True
        while n is not None and not isinstance(n, (_vn_ast.Label, _vn_ast.Return, _vn_ast.Menu)):
            if isinstance(n, _vn_ast.Python) and "vn_wait(" in n.code.source:
                return True
            n = n.next
        return False

    def vn_page(path, bg=None, who=None, intro=False):
        if store.vn_skipping:
            return
        _vn_page_show(path, bg=bg, who=who, intro=intro)
        # remember which chapter (scene) we're in: choices jump straight into
        # the next chapter's label within the same play session
        store.vn_cur_scene = bg or path.rsplit("/", 2)[-2]

    def vn_wait():
        """Empty page.
        - more dialogue later in the chapter: "No transcript for this line."
        - nothing left to read in this chapter: ask once whether to go on to
          the next scene; "No" keeps showing the empty pages as normal."""
        if store.vn_skipping:
            return
        if not store.vn_page_art and not _vn_dialogue_left():
            # the last empty page before the choice (or the chapter's end):
            # nothing to read or skip, go straight on
            if not _vn_empty_pages_left():
                return
            here = store.vn_cur_scene
            if here not in store.vn_skip_declined:
                store.vn_skip_declined.add(here)
                msg = __("No transcript left\nThe rest of this chapter has no transcript. Go to the next scene?")
                if renpy.call_screen("confirm", message=msg, yes_action=Return(True), no_action=Return(False)):
                    vn_start_skip()
                    return
        _vn_wait_real()
