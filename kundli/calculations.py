import swisseph as swe

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


def calculate_planets(jd, asc_sign_no):

    planets_data = []

    for planet_name, planet_id in PLANETS.items():

        result = swe.calc_ut(
            jd,
            planet_id,
            swe.FLG_SIDEREAL | swe.FLG_SPEED
        )

        longitude = result[0][0]

        sign_no = int(longitude / 30) + 1

        sign_name = SIGNS[sign_no - 1]

        degree_in_sign = longitude % 30

        house = ((sign_no - asc_sign_no) % 12) + 1

        retrograde = result[0][3] < 0

        planets_data.append({
            "planet": planet_name,
            "longitude": round(longitude, 6),
            "sign_no": sign_no,
            "sign": sign_name,
            "degree_in_sign": round(degree_in_sign, 6),
            "house": int(house),
            "retrograde": retrograde
        })

    return planets_data