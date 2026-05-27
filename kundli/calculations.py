import swisseph as swe

# ==========================
# SIGNS
# ==========================

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces"
]

# ==========================
# PLANETS
# ==========================

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}


# ==========================
# HOUSE CALCULATION
# ==========================

def calculate_house(
    sign_no,
    lagna_sign_no
):

    house = (
        (sign_no - lagna_sign_no) % 12
    ) + 1

    return house


# ==========================
# PLANET POSITION CALCULATION
# ==========================

def calculate_planets(
    jd,
    lagna_sign_no
):

    planetary_data = []

    for planet_name, planet_id in PLANETS.items():

        result = swe.calc_ut(
            jd,
            planet_id,
            swe.FLG_SIDEREAL | swe.FLG_SPEED
        )

        data = result[0]

        longitude = data[0]

        speed = data[3]

        sign_no = int(
            longitude / 30
        ) + 1

        sign_name = SIGNS[
            sign_no - 1
        ]

        degree_in_sign = (
            longitude % 30
        )

        house_no = calculate_house(
            sign_no,
            lagna_sign_no
        )

        planetary_data.append({

            "planet":
            planet_name,

            "longitude":
            round(
                longitude,
                6
            ),

            "sign_no":
            sign_no,

            "sign":
            sign_name,

            "degree_in_sign":
            round(
                degree_in_sign,
                2
            ),

            "house":
            house_no,

            "retrograde":
            speed < 0,

            "planet_speed":
            round(
                speed,
                6
            )

        })

    return planetary_data


# ==========================
# CHANDRA KUNDLI
# ==========================

def generate_chandra_chart(
    planetary_data
):

    moon = next(

        p for p in planetary_data

        if p["planet"] == "Moon"

    )

    moon_sign = moon["sign_no"]

    chandra_data = []

    for planet in planetary_data:

        house = calculate_house(

            planet["sign_no"],
            moon_sign

        )

        chandra_data.append({

            "planet":
            planet["planet"],

            "moon_house":
            house,

            "sign":
            planet["sign"],

            "degree":
            planet[
                "degree_in_sign"
            ],

            "retrograde":
            planet[
                "retrograde"
            ]

        })

    return {

        "moon_lagna":
        SIGNS[
            moon_sign - 1
        ],

        "planetary_positions":
        chandra_data

    }