from datetime import datetime
import swisseph as swe
import pytz


PLANETS = {

    swe.SUN: "Sun",
    swe.MOON: "Moon",
    swe.MARS: "Mars",
    swe.MERCURY: "Mercury",
    swe.JUPITER: "Jupiter",
    swe.VENUS: "Venus",
    swe.SATURN: "Saturn",
    swe.MEAN_NODE: "Rahu"

}


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


HOUSE_LORDS = {

    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter"

}


BENEFIC = [

    "Jupiter",
    "Venus",
    "Mercury"

]


MALEFIC = [

    "Saturn",
    "Mars",
    "Rahu",
    "Ketu"

]


def calculate_planets(

    dob,
    birth_time,
    latitude,
    longitude,
    timezone

):

    tz = pytz.timezone(timezone)

    birth = datetime.strptime(

        f"{dob} {birth_time.upper()}",
        "%d-%m-%Y %I:%M %p"

    )

    birth = tz.localize(birth)

    utc = birth.astimezone(pytz.utc)

    jd = swe.julday(

        utc.year,
        utc.month,
        utc.day,

        utc.hour +
        utc.minute/60 +
        utc.second/3600

    )

    swe.set_sid_mode(
        swe.SIDM_LAHIRI
    )

    planets = {}

    for pid,name in PLANETS.items():

        result = swe.calc_ut(

            jd,
            pid,
            swe.FLG_SIDEREAL

        )[0]

        longitude_value = result[0]

        sign_no = int(
            longitude_value/30
        )

        planets[name] = {

            "longitude":
            round(
                longitude_value,
                2
            ),

            "sign":
            SIGNS[
                sign_no
            ]

        }

    rahu = planets["Rahu"]["longitude"]

    ketu = (

        rahu + 180

    ) % 360

    planets["Ketu"] = {

        "longitude":
        round(
            ketu,
            2
        ),

        "sign":

        SIGNS[
            int(
                ketu/30
            )
        ]

    }

    return planets


def get_moon_lagna(

    planets

):

    return planets["Moon"]["sign"]


def get_planetary_houses(

    planets

):

    moon_sign = SIGNS.index(

        planets["Moon"]["sign"]

    )

    houses = {}

    for planet,data in planets.items():

        sign = SIGNS.index(

            data["sign"]

        )

        house = (

            sign -
            moon_sign

        ) % 12 + 1

        houses[planet] = house

    return houses


def get_house_lords(

    houses

):

    output = {}

    for house in range(1,13):

        lord = HOUSE_LORDS[house]

        output[
            f"House_{house}"
        ] = {

            "lord":
            lord,

            "placed_in":

            houses.get(
                lord
            )

        }

    return output


def get_moon_aspects(

    houses

):

    aspects=[]

    for planet,house in houses.items():

        if house==7:

            aspects.append(
                planet
            )

    return aspects


def get_influence(

    houses

):

    return {

        "benefic":[

            p for p in houses

            if p in BENEFIC

        ],

        "malefic":[

            p for p in houses

            if p in MALEFIC

        ]

    }


def get_yogas(

    houses

):

    yogas=[]

    if houses.get(

        "Jupiter"

    ) in [

        1,4,7,10

    ]:

        yogas.append(

            "Gaja Kesari Yoga"

        )

    return yogas


def generate_chandra_kundli(

    dob,
    birth_time,
    latitude,
    longitude,
    timezone

):

    planets = calculate_planets(

        dob,
        birth_time,
        latitude,
        longitude,
        timezone

    )

    houses = get_planetary_houses(
        planets
    )

    return {

        "moon_lagna":

        get_moon_lagna(
            planets
        ),

        "planetary_house_positions":

        houses,

        "house_lord_placements":

        get_house_lords(
            houses
        ),

        "moon_aspects":

        get_moon_aspects(
            houses
        ),

        "benefic_malefic_influence":

        get_influence(
            houses
        ),

        "moon_chart_yogas":

        get_yogas(
            houses
        )

    }