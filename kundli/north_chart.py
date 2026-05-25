SIGNS = [
    "Ar",
    "Ta",
    "Ge",
    "Cn",
    "Le",
    "Vi",
    "Li",
    "Sc",
    "Sg",
    "Cp",
    "Aq",
    "Pi"
]


def generate_north_indian_chart(
    planets,
    house_rashi_map
):

    # =========================================
    # STORE PLANETS HOUSEWISE
    # =========================================

    house_data = {}

    for i in range(1, 13):
        house_data[i] = []

    for planet in planets:

        house = int(planet["house"])

        text = (
            f'{planet["planet"]} '
            f'{round(planet["degree_in_sign"], 1)}°'
        )

        house_data[house].append(text)

    # =========================================
    # HOUSE POSITIONS
    # =========================================

    house_positions = {

        1:  (600, 180),

        2:  (380, 280),
        3:  (200, 450),

        4:  (380, 600),

        5:  (200, 780),
        6:  (380, 950),

        7:  (600, 1040),

        8:  (820, 950),
        9:  (1000, 780),

        10: (820, 600),

        11: (1000, 450),
        12: (820, 280)
    }

    # =========================================
    # SVG START
    # =========================================

    svg = """
<svg width="1200" height="1200"
xmlns="http://www.w3.org/2000/svg">

<!-- OUTER SQUARE -->

<rect x="100"
      y="100"
      width="1000"
      height="1000"
      fill="white"
      stroke="black"
      stroke-width="5"/>

<!-- MAIN DIAGONALS -->

<line x1="100" y1="100"
      x2="1100" y2="1100"
      stroke="black"
      stroke-width="4"/>

<line x1="1100" y1="100"
      x2="100" y2="1100"
      stroke="black"
      stroke-width="4"/>

<!-- CENTER DIAMOND -->

<polygon points="
600,100
1100,600
600,1100
100,600"
fill="none"
stroke="black"
stroke-width="4"/>

<!-- TITLE -->

<text x="600"
      y="60"
      font-size="34"
      text-anchor="middle"
      font-weight="bold">
North Indian Kundli
</text>
"""

    # =========================================
    # DRAW HOUSES
    # =========================================

    for house, position in house_positions.items():

        x = position[0]
        y = position[1]

        rashi = house_rashi_map[house]["sign_no"]

        rashi_text = SIGNS[rashi - 1]

        # =====================================
        # RASHI NUMBER
        # =====================================

        svg += f"""
<text x="{x}"
      y="{y}"
      font-size="30"
      text-anchor="middle"
      font-weight="bold"
      fill="darkred">
{rashi}
</text>
"""

        # =====================================
        # RASHI NAME
        # =====================================

        svg += f"""
<text x="{x}"
      y="{y + 28}"
      font-size="16"
      text-anchor="middle"
      fill="blue">
{rashi_text}
</text>
"""

        # =====================================
        # PLANETS
        # =====================================

        yy = y + 60

        for item in house_data[house]:

            svg += f"""
<text x="{x}"
      y="{yy}"
      font-size="15"
      text-anchor="middle">
{item}
</text>
"""

            yy += 22

    # =========================================
    # SVG END
    # =========================================

    svg += "</svg>"

    return svg