## Speakers and their sprites.
## Sprites use placeholders until a PNG exists at the given path.
## Add expressions as new image lines, e.g.
##     image geist angry = vn_sprite("images/books/geist/geist_angry.png", "#2f5d50", "Lady Geist (angry)")

## narrator: see library/vn_narration.rpy

define geist    = Character("Lady Geist", color="#7fc4a8")
define infernus = Character("Infernus",   color="#e0704f")
define ivy      = Character("Ivy",        color="#a8c46a")
define holliday = Character("Holliday",   color="#e0a860")

image geist    = vn_sprite("images/books/geist/geist.png",       "#2f5d50", "Lady Geist")
image infernus = vn_sprite("images/books/infernus/infernus.png", "#7a2a1d", "Infernus")
image ivy      = vn_sprite("images/books/ivy/ivy.png",           "#4f6b2c", "Ivy")
image holliday = vn_sprite("images/books/holliday/holliday.png", "#8a5a2b", "Holliday")

image bg placeholder = vn_bg("images/bg_placeholder.png", "Background")

## Supporting cast (used by converted transcripts)
define oathkeeper = Character("Oathkeeper", color="#c0392b", what_italic=True)
define johann     = Character("Johann Jr.", color="#9fb8d6")
define dynamo     = Character("Dynamo",     color="#8e7cc3")
define mcginnis   = Character("McGinnis",   color="#e6a23c")
define abrams     = Character("Abrams",     color="#b08d57")
define patron     = Character("Amber Hand", color="#f0c674")
define fairfax    = Character("Fairfax",    color="#a3a3a3")
define bebop      = Character("Bebop",      color="#e8794a")
define hank       = Character("Hank",       color="#c9a86a")
define shelly     = Character("Ms. Shelly", color="#d4a5c9")

## Speakers that the converted scripts name with a plain string ("Wraith" "...")
## rather than a Character: their name colour is applied in screen say.
define VN_NAME_COLORS = {
    "Wraith": "#954E7A",
    "Lash":   "#444C57",
}
define wraith = Character("Wraith", color="#954E7A")
define lash   = Character("Lash",   color="#444C57")
