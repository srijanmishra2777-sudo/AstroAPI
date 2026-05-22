from fastapi import FastAPI, Query
from datetime import datetime
import swisseph as swe
import pytz

app = FastAPI(title="Advanced Kundli API")

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


def generate_kundli_chart(planets):

    houses = {i: [] for i in range(1, 13)}

    for p in planets:
        houses[p["house"]].append(p["planet"])

    return houses


@app.get("/api/v1/kundali")
def get_kundali(
    dob: str = Query(
        ...,
        description="DD-MM-YYYY",
        examples=["15-08-2002"]
    ),

    birth_time: str = Query(
        ...,
        description="HH:MM AM/PM",
        examples=["01:35 AM"]
    ),

    latitude: float = Query(
        ...,
        examples=[26.8467]
    ),

    longitude: float = Query(
        ...,
        examples=[80.9462]
    ),

    timezone: str = Query(
        default="Asia/Kolkata",
        examples=["Asia/Kolkata"]
    )
):

    local_tz = pytz.timezone(timezone)

    dt = datetime.strptime(
        f"{dob} {birth_time}",
        "%d-%m-%Y %I:%M %p"
    )

    local_dt = local_tz.localize(dt)

    utc_dt = local_dt.astimezone(pytz.utc)

    jd = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60
    )

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # ASCENDANT
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

    # SUNRISE / SUNSET
    geopos = (longitude, latitude, 0)

    sunrise = swe.rise_trans(
        jd,
        swe.SUN,
        swe.CALC_RISE,
        geopos
    )[1][0]

    sunset = swe.rise_trans(
        jd,
        swe.SUN,
        swe.CALC_SET,
        geopos
    )[1][0]

    planetary_data = []

    # FIRST PASS
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

        house = ((sign_no - asc_sign_no) % 12) + 1

        retrograde = speed < 0

        combust = False

        if planet_name in COMBUST_LIMITS and sun_longitude:

            diff = abs(longitude_value - sun_longitude)

            diff = min(diff, 360 - diff)

            combust = diff <= COMBUST_LIMITS[planet_name]

        planetary_data.append({
            "planet": planet_name,
            "sign_no": sign_no,
            "sign": sign_name,
            "longitude": round(longitude_value, 6),
            "degree_in_sign": round(degree_in_sign, 6),
            "final_degree": format_degree(degree_in_sign),
            "house": int(house),
            "retrograde": retrograde,
            "combust": combust,

            "meta_data": {
                "planet_speed": round(speed, 6),
                "latitude": round(latitude_value, 6),
                "distance_au": round(distance_au, 6),
                "raw_longitude": round(longitude_value, 6)
            }
        })

    kundli_chart = generate_kundli_chart(
        planetary_data
    )

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

        "sunrise_julian": sunrise,
        "sunset_julian": sunset,

        "ascendant": {
            "sign_no": asc_sign_no,
            "sign": asc_sign_name,
            "degree": round(asc_degree, 6)
        },

        "planetary_data": planetary_data,

        "kundli_chart": kundli_chart
    }