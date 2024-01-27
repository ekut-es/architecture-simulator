# Pipeline SVG arrow heads (markers)
Our js code can change the color of arrows. Thanks to `context-stroke` and `context-fill`, the arrow heads (the path markers) will automatically use the same color as the path. Unfortunately, these two features are not supported in chrome (https://bugs.chromium.org/p/chromium/issues/detail?id=367737) and has only recently been fixed in firefox (https://bugzilla.mozilla.org/show_bug.cgi?id=752638). To still get colored arrow heads, we define one marker per color (actually two, because it also needs a reversed version) and then in the js code, we look into the style attribute of the path and look for a `marker-start:` string and replace it with the correct one for the desired color (which sucks, but works reliably).

If you want to use our hacky solution, you need to name your markers `XXXXXX_ArchsimMarker*` - the Xs are the hex color of your marker and the pattern can be followed by anything. The js will then look for that pattern and only change the color code.

## Dont lose the markers
Since the svg only uses black markers, Inkscape will think that all the other markers are useless and it deletes them ._.

To work around that, we created a build script for our SVGs, `/build_svg.py`. If you want to use it, you need to find the place in your SVG where your markers are defined (marker definitions start with a `<marker` tag). Surround the whole section with the comments `<!--CUSTOM MARKERS START-->` and `<!--CUSTOM MARKERS END-->`. The script will replace the code between that with the string you provide in the script (you need to add it there first, of course). `/buld.sh` will execute the svg build script.
