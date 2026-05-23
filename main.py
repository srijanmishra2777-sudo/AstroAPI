from fastapi import FastAPI, Query
from fastapi.responses import Response
from datetime import datetime
import swisseph as swe
import pytz
from kundli.north_chart import generate_north_indian_chart
# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Advanced Kundli API",
    version="2.0.0"
)

# =========================================================
# CONSTANTS
# =========================================================

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
    "Rahu": swe.MEAN_NODE,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO
}

COMBUST_LIMITS = {
    "Moon": 12,
    "Mars": 17,
    "Mercury": 14,
    "Jupiter": 11,
    "Venus": 10,
    "Saturn": 15
}

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_sign(longitude):

    sign_no = int(longitude / 30) + 1

    sign_name = SIGNS[sign_no - 1]

    degree_in_sign = longitude % 30

    return sign_no, sign_name, degree_in_sign


def format_degree(value):

    d = int(value)

    m = int((value - d) * 60)

    s = round((((value - d) * 60) - m) * 60, 2)

    return f"{d}° {m}' {s}\""


def convert_julian_to_time(julian_value, timezone):

    jd = julian_value + 0.5

    Z = int(jd)

    F = jd - Z

    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)

        A = Z + 1 + alpha - int(alpha / 4)

    B = A + 1524

    C = int((B - 122.1) / 365.25)

    D = int(365.25 * C)

    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F

    month = E - 1 if E < 14 else E - 13

    year = C - 4716 if month > 2 else C - 4715

    day_int = int(day)

    fraction = day - day_int

    hours = fraction * 24

    hour = int(hours)

    minutes = (hours - hour) * 60

    minute = int(minutes)

    seconds = int((minutes - minute) * 60)

    utc_dt = datetime(
        year,
        month,
        day_int,
        hour,
        minute,
        seconds,
        tzinfo=pytz.utc
    )

    local_tz = pytz.timezone(timezone)

    local_dt = utc_dt.astimezone(local_tz)

    return local_dt.strftime("%I:%M:%S %p")


# =========================================================
# KUNDLI CHART DATA
# =========================================================

def generate_kundli_chart(planets):

    houses = {i: [] for i in range(1, 13)}

    for p in planets:

        text = (
            f'{p["planet"]} '
            f'({round(p["degree_in_sign"], 2)}°)'
        )

        houses[p["house"]].append(text)

    return houses


# =========================================================
# SVG KUNDLI GENERATOR
# =========================================================

def generate_kundli_svg(planets):

    house_data = {i: [] for i in range(1, 13)}

    for p in planets:

        text = (
            f'{p["planet"]} '
            f'{round(p["degree_in_sign"], 1)}°'
        )

        house_data[p["house"]].append(text)

    positions = {
        1:  (300, 80),
        2:  (430, 130),
        3:  (500, 230),
        4:  (430, 330),
        5:  (500, 430),
        6:  (430, 520),
        7:  (300, 560),
        8:  (170, 520),
        9:  (100, 430),
        10: (170, 330),
        11: (100, 230),
        12: (170, 130)
    }

    svg = """
    <svg width="600" height="600"
    xmlns="http://www.w3.org/2000/svg">

    <rect x="50" y="50"
    width="500" height="500"
    fill="white"
    stroke="black"
    stroke-width="2"/>

    <line x1="300" y1="50"
    x2="550" y2="300"
    stroke="black"/>

    <line x1="550" y1="300"
    x2="300" y2="550"
    stroke="black"/>

    <line x1="300" y1="550"
    x2="50" y2="300"
    stroke="black"/>

    <line x1="50" y1="300"
    x2="300" y2="50"
    stroke="black"/>

    <text x="200" y="30"
    font-size="24"
    font-weight="bold">
    North Indian Kundli
    </text>
    """

    for house, (x, y) in positions.items():

        svg += f'''
        <text x="{x}" y="{y}"
        font-size="14"
        font-weight="bold">
        H{house}
        </text>
        '''

        yy = y + 20

        for item in house_data[house]:

            svg += f'''
            <text x="{x}" y="{yy}"
            font-size="11">
            {item}
            </text>
            '''

            yy += 16

    svg += "</svg>"

    return svg


# =========================================================
# MAIN KUNDLI API
# =========================================================

@app.get("/api/v1/kundali")
def get_kundali(

    dob: str = Query(
        ...,
        description="Date of Birth DD-MM-YYYY",
        examples=["15-08-2002"]
    ),

    birth_time: str = Query(
        ...,
        description="Birth Time HH:MM AM/PM",
        examples=["01:35 AM"]
    ),

    latitude: float = Query(
        ...,
        description="Latitude",
        examples=[26.8467]
    ),

    longitude: float = Query(
        ...,
        description="Longitude",
        examples=[80.9462]
    ),

    timezone: str = Query(
        default="Asia/Kolkata",
        description="Timezone",
        examples=["Asia/Kolkata"]
    )
):

    try:

        # =========================================================
        # DATETIME
        # =========================================================

        local_tz = pytz.timezone(timezone)

        dt = datetime.strptime(
            f"{dob} {birth_time.upper()}",
            "%d-%m-%Y %I:%M %p"
        )

        local_dt = local_tz.localize(dt)

        utc_dt = local_dt.astimezone(pytz.utc)

        # =========================================================
        # JULIAN DAY
        # =========================================================

        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour +
            utc_dt.minute / 60 +
            utc_dt.second / 3600
        )

        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # =========================================================
        # ASCENDANT
        # =========================================================

        houses, ascmc = swe.houses_ex(
            jd,
            latitude,
            longitude,
            b'P',
            swe.FLG_SIDEREAL
        )

        ascendant_longitude = ascmc[0]

        asc_sign_no, asc_sign_name, asc_degree = get_sign(
            ascendant_longitude
        )

        # =========================================================
        # SUNRISE / SUNSET
        # =========================================================

        geopos = (longitude, latitude, 0)

        sunrise_jd = swe.rise_trans(
            jd,
            swe.SUN,
            swe.CALC_RISE,
            geopos
        )[1][0]

        sunset_jd = swe.rise_trans(
            jd,
            swe.SUN,
            swe.CALC_SET,
            geopos
        )[1][0]

        # =========================================================
        # PLANETARY DATA
        # =========================================================

        planetary_data = []

        sun_longitude = None

        for planet_name, planet_id in PLANETS.items():

            result = swe.calc_ut(
                jd,
                planet_id,
                swe.FLG_SIDEREAL | swe.FLG_SPEED
            )

            longitude_value = result[0][0]

            latitude_value = result[0][1]

            distance_au = result[0][2]

            speed = result[0][3]

            if planet_name == "Sun":
                sun_longitude = longitude_value

            sign_no, sign_name, degree_in_sign = get_sign(
                longitude_value
            )

            house = (
                (sign_no - asc_sign_no) % 12
            ) + 1

            retrograde = speed < 0

            combust = False

            if (
                planet_name in COMBUST_LIMITS
                and sun_longitude is not None
            ):

                diff = abs(
                    longitude_value - sun_longitude
                )

                diff = min(diff, 360 - diff)

                combust = (
                    diff <= COMBUST_LIMITS[planet_name]
                )

            planetary_data.append({

                "planet": planet_name,

                "sign_no": sign_no,

                "sign": sign_name,

                "longitude": round(
                    longitude_value,
                    6
                ),

                "degree_in_sign": round(
                    degree_in_sign,
                    6
                ),

                "final_degree": format_degree(
                    degree_in_sign
                ),

                "house": int(house),

                "retrograde": retrograde,

                "combust": combust,

                "meta_data": {

                    "planet_speed": round(
                        speed,
                        6
                    ),

                    "latitude": round(
                        latitude_value,
                        6
                    ),

                    "distance_au": round(
                        distance_au,
                        6
                    ),

                    "raw_longitude": round(
                        longitude_value,
                        6
                    )
                }
            })

        # =========================================================
        # KUNDLI CHART
        # =========================================================

        kundli_chart = generate_kundli_chart(
            planetary_data
        )

        # =========================================================
        # FINAL RESPONSE
        # =========================================================

        return {

            "status": "success",

            "birth_details": {
                "dob": dob,
                "birth_time": birth_time,
                "timezone": timezone
            },

            "location": {
                "latitude": latitude,
                "longitude": longitude
            },

            "sunrise": convert_julian_to_time(
                sunrise_jd,
                timezone
            ),

            "sunset": convert_julian_to_time(
                sunset_jd,
                timezone
            ),

            "ascendant": {
                "sign_no": asc_sign_no,
                "sign": asc_sign_name,
                "degree": round(
                    asc_degree,
                    6
                )
            },

            "planetary_data": planetary_data,

            "kundli_chart": kundli_chart
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# =========================================================
# SVG API
# =========================================================

@app.get("/api/v1/kundli/svg")
def get_kundli_svg(

    dob: str,

    birth_time: str,

    latitude: float,

    longitude: float,

    timezone: str = "Asia/Kolkata"
):

    result = get_kundali(
        dob,
        birth_time,
        latitude,
        longitude,
        timezone
    )

    planets = result["planetary_data"]

    svg_chart = generate_north_indian_chart(
        planets
    )

    return Response(
        content=svg_chart,
        media_type="image/svg+xml"
    )


# =========================================================
# ROOT API
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Advanced Kundli API Running Successfully"
    }