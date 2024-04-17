import re

riscv_five_stage_markers = """
<marker
   style="overflow:visible"
   id="000000_ArchsimMarker_Triangle"
   refX="0"
   refY="0"
   orient="auto-start-reverse"
   inkscape:stockid="TriangleStart"
   markerWidth="2"
   markerHeight="2"
   viewBox="0 0 5.3244081 6.1553851"
   inkscape:isstock="true"
   inkscape:collect="always"
   preserveAspectRatio="none"><path
     transform="scale(0.5)"
     style="fill:#000000;fill-rule:evenodd;stroke:#000000;stroke-width:1pt"
     d="M 5.77,0 -2.88,5 V -5 Z"
     id="000000_ArchsimMarker_Triangle_Path" /></marker>
<marker
   style="overflow:visible"
   id="008000_ArchsimMarker_Triangle"
   refX="0"
   refY="0"
   orient="auto-start-reverse"
   inkscape:stockid="TriangleStart"
   markerWidth="2"
   markerHeight="2"
   viewBox="0 0 5.3244081 6.1553851"
   inkscape:isstock="true"
   inkscape:collect="always"
   preserveAspectRatio="none"><path
     transform="scale(0.5)"
     style="fill:#008000;fill-rule:evenodd;stroke:#008000;stroke-width:1pt"
     d="M 5.77,0 -2.88,5 V -5 Z"
     id="008000_ArchsimMarker_Triangle_Path" /></marker>
<marker
   style="overflow:visible"
   id="0000FF_ArchsimMarker_Triangle"
   refX="0"
   refY="0"
   orient="auto-start-reverse"
   inkscape:stockid="TriangleStart"
   markerWidth="2"
   markerHeight="2"
   viewBox="0 0 5.3244081 6.1553851"
   inkscape:isstock="true"
   inkscape:collect="always"
   preserveAspectRatio="none"><path
     transform="scale(0.5)"
     style="fill:#0000FF;fill-rule:evenodd;stroke:#0000FF;stroke-width:1pt"
     d="M 5.77,0 -2.88,5 V -5 Z"
     id="0000FF_ArchsimMarker_Triangle_Path" /></marker>
<marker
   style="overflow:visible"
   id="000000_ArchsimMarker_Dot"
   refX="0"
   refY="0"
   orient="auto"
   inkscape:stockid="Dot"
   markerWidth="2"
   markerHeight="2"
   viewBox="0 0 5.6666667 5.6666667"
   inkscape:isstock="true"
   inkscape:collect="always"
   preserveAspectRatio="xMidYMid"><path
     transform="scale(0.5)"
     style="fill:#000000;fill-rule:evenodd;stroke:none"
     d="M 5,0 C 5,2.76 2.76,5 0,5 -2.76,5 -5,2.76 -5,0 c 0,-2.76 2.3,-5 5,-5 2.76,0 5,2.24 5,5 z"
     id="Dot1"
     sodipodi:nodetypes="sssss" /></marker>
<marker
   style="overflow:visible"
   id="0000FF_ArchsimMarker_Dot"
   refX="0"
   refY="0"
   orient="auto"
   inkscape:stockid="Dot"
   markerWidth="2"
   markerHeight="2"
   viewBox="0 0 5.6666667 5.6666667"
   inkscape:isstock="true"
   inkscape:collect="always"
   preserveAspectRatio="xMidYMid"><path
     transform="scale(0.5)"
     style="fill:#0000FF;fill-rule:evenodd;stroke:none"
     d="M 5,0 C 5,2.76 2.76,5 0,5 -2.76,5 -5,2.76 -5,0 c 0,-2.76 2.3,-5 5,-5 2.76,0 5,2.24 5,5 z"
     id="Dot1"
     sodipodi:nodetypes="sssss" /></marker>
"""

riscv_single_stage_markers = """
    <marker
    style="overflow:visible"
    id="000000_ArchsimMarker_Dot"
    refX="0"
    refY="0"
    orient="auto"
    inkscape:stockid="Dot"
    markerWidth="0.40000001"
    markerHeight="0.40000001"
    viewBox="0 0 1 1"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#000000;fill-rule:evenodd;stroke:none"
        d="M 5,0 C 5,2.76 2.76,5 0,5 -2.76,5 -5,2.76 -5,0 c 0,-2.76 2.3,-5 5,-5 2.76,0 5,2.24 5,5 z"
        sodipodi:nodetypes="sssss"
        id="path78" /></marker>
    <marker
    style="overflow:visible"
    id="008000_ArchsimMarker_Dot"
    refX="0"
    refY="0"
    orient="auto"
    inkscape:stockid="Dot"
    markerWidth="0.40000001"
    markerHeight="0.40000001"
    viewBox="0 0 1 1"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#008000;fill-rule:evenodd;stroke:none"
        d="M 5,0 C 5,2.76 2.76,5 0,5 -2.76,5 -5,2.76 -5,0 c 0,-2.76 2.3,-5 5,-5 2.76,0 5,2.24 5,5 z"
        sodipodi:nodetypes="sssss"
        id="path78" /></marker>
    <marker
    style="overflow:visible"
    id="0000FF_ArchsimMarker_Dot"
    refX="0"
    refY="0"
    orient="auto"
    inkscape:stockid="Dot"
    markerWidth="0.40000001"
    markerHeight="0.40000001"
    viewBox="0 0 1 1"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#0000FF;fill-rule:evenodd;stroke:none"
        d="M 5,0 C 5,2.76 2.76,5 0,5 -2.76,5 -5,2.76 -5,0 c 0,-2.76 2.3,-5 5,-5 2.76,0 5,2.24 5,5 z"
        sodipodi:nodetypes="sssss"
        id="path78" /></marker>
        <marker
    style="overflow:visible"
    id="000000_ArchsimMarker_Triangle_Reversed"
    refX="0"
    refY="0"
    orient="auto-start-reverse"
    inkscape:stockid="Triangle arrow"
    markerWidth="1"
    markerHeight="1"
    viewBox="0 0 1 1"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#000000;fill-rule:evenodd;stroke:#000000;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="path135" /></marker>
        <marker
    style="overflow:visible"
    id="008000_ArchsimMarker_Triangle_Reversed"
    refX="0"
    refY="0"
    orient="auto-start-reverse"
    inkscape:stockid="Triangle arrow"
    markerWidth="1"
    markerHeight="1"
    viewBox="0 0 1 1"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#008000;fill-rule:evenodd;stroke:#008000;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="path135" /></marker>
        <marker
    style="overflow:visible"
    id="0000FF_ArchsimMarker_Triangle_Reversed"
    refX="0"
    refY="0"
    orient="auto-start-reverse"
    inkscape:stockid="Triangle arrow"
    markerWidth="1"
    markerHeight="1"
    viewBox="0 0 1 1"
    inkscape:isstock="true"
    inkscape:collect="always"
    preserveAspectRatio="xMidYMid"><path
        transform="scale(0.5)"
        style="fill:#0000FF;fill-rule:evenodd;stroke:#0000FF;stroke-width:1pt"
        d="M 5.77,0 -2.88,5 V -5 Z"
        id="path135" /></marker>
         """

if __name__ == "__main__":
    for filename, markers in [
        ("riscv_five_stage_pipeline.svg", riscv_five_stage_markers),
        ("riscv_single_stage_pipeline.svg", riscv_single_stage_markers),
    ]:
        # open with read permissions
        file = open("./webgui/src/img/" + filename, "r+")

        # read everything
        old_content = file.read()

        # go back to the beginning
        file.seek(0)

        # search for the custom markers section
        match = re.search(
            r"<!--CUSTOM MARKERS START-->([\s\S]*)<!--CUSTOM MARKERS END-->",
            old_content,
        )
        if match is None:
            raise Exception(
                "Error: Did not find custom markers section in svg document"
            )

        # replace that section with our desired markers
        section_start = match.start(1)
        section_end = match.end(1)
        new_content = old_content[:section_start] + markers + old_content[section_end:]

        # write the new content to the svg
        file.write(new_content)
        file.truncate()
        file.close()
