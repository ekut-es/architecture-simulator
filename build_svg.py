import re

custom_markers = """
<marker
    style="overflow:visible"
    id="Triangle_000000"
    refX="0"
    refY="0"
    orient="auto-start-reverse"
    inkscape:stockid="TriangleStart"
    markerWidth="5.3244081"
    markerHeight="6.155385"
    viewBox="0 0 5.3244081 6.1553851"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#000000;fill-rule:evenodd;stroke:#000000;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="Triangle_000000_Path" /></marker><marker
    style="overflow:visible"
    id="Triangle_008000"
    refX="0"
    refY="0"
    orient="auto-start-reverse"
    inkscape:stockid="TriangleStart"
    markerWidth="5.3244081"
    markerHeight="6.155385"
    viewBox="0 0 5.3244081 6.1553851"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#008000;fill-rule:evenodd;stroke:#008000;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="Triangle_008000_Path" /></marker><marker
    style="overflow:visible"
    id="Triangle_0000FF"
    refX="0"
    refY="0"
    orient="auto-start-reverse"
    inkscape:stockid="TriangleStart"
    markerWidth="5.3244081"
    markerHeight="6.155385"
    viewBox="0 0 5.3244081 6.1553851"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#0000FF;fill-rule:evenodd;stroke:#0000FF;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="Triangle_0000FF_Path" /></marker><marker
    style="overflow:visible"
    id="Triangle_000000_reversed"
    refX="0"
    refY="0"
    orient="auto"
    inkscape:stockid="TriangleStart"
    markerWidth="5.3244081"
    markerHeight="6.155385"
    viewBox="0 0 5.3244081 6.1553851"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><g
        transform="rotate(180,0,0)"
        id="g45523"><path
        transform="scale(0.5)"
        style="fill:#000000;fill-rule:evenodd;stroke:#000000;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="Triangle_000000_reversed_Path" /></g></marker><marker
        style="overflow:visible"
    id="Triangle_008000_reversed"
    refX="0"
    refY="0"
    orient="auto"
    inkscape:stockid="TriangleStart"
    markerWidth="5.3244081"
    markerHeight="6.155385"
    viewBox="0 0 5.3244081 6.1553851"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><g
        transform="rotate(180,0,0)"
        id="g45523"><path
        transform="scale(0.5)"
        style="fill:#008000;fill-rule:evenodd;stroke:#008000;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="Triangle_008000_reversed_Path" /></g></marker><marker
    style="overflow:visible"
    id="Triangle_0000FF_reversed"
    refX="0"
    refY="0"
    orient="auto"
    inkscape:stockid="TriangleStart"
    markerWidth="5.3244081"
    markerHeight="6.155385"
    viewBox="0 0 5.3244081 6.1553851"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><g
        transform="rotate(180,0,0)"
        id="g45523"><path
        transform="scale(0.5)"
        style="fill:#0000FF;fill-rule:evenodd;stroke:#0000FF;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="Triangle_0000FF_reversed_Path" /></g></marker>
"""

if __name__ == "__main__":
    # open with read permissions
    riscv_svg = open("./webgui/src/img/riscv_pipeline.svg", "r+")

    # read everything
    old_content = riscv_svg.read()

    # go back to the beginning
    riscv_svg.seek(0)

    # search for the custom markers section
    match = re.search(
        r"<!--CUSTOM MARKERS START-->([\s\S]*)<!--CUSTOM MARKERS END-->", old_content
    )
    if match is None:
        raise Exception("Error: Did not find custom markers section in svg document")

    # replace that section with our desired markers
    section_start = match.start(1)
    section_end = match.end(1)
    new_content = (
        old_content[:section_start] + custom_markers + old_content[section_end:]
    )

    # write the new content to the svg
    riscv_svg.write(new_content)
    riscv_svg.truncate()
    riscv_svg.close()
