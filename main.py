from fastapi import FastAPI, HTTPException, Query
import swisseph as swe
from datetime import datetime
import pytz

app = FastAPI(
    title="Advanced Jyotish API",
    description="Professional Astrology API using Swiss Ephemeris",
    version="3.0.0"
)

# =====================================
# ZODIAC SIGNS
# =====================================
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

# =====================================
# COMBUSTION LIMITS
# =====================================
COMBUST_LIMITS = {
    swe.MOON: 12,
    swe.MARS: 17,
    swe.MERCURY: 14,
    swe.JUPITER: 11,
    swe.VENUS: 10,
    swe.SATURN: 15
}

# =====================================
# PLANETS
# =====================================
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO
}

# =====================================
# FORMAT DEGREE
# =====================================
def format_degree(decimal_degree):
    degree = int(decimal_degree)

    minutes = int((decimal_degree - degree) * 60)

    seconds = round(
        ((((decimal_degree - degree) * 60) - minutes) * 60),
        2
    )

    return f'{degree}° {minutes}\' {seconds}"'


# =====================================
# HOUSE CALCULATOR
# =====================================
def get_house(planet_lon, asc_lon):

    asc_sign = int(asc_lon / 30)

    planet_sign = int(planet_lon / 30)

    house = (planet_sign - asc_sign) + 1

    if house <= 0:
        house += 12

    return house


# =====================================
# API ENDPOINT
# =====================================
@app.get("/api/v1/kundali")
def get_kundali(

    dob: str = Query(
        ...,
        description="Date of Birth in DD-MM-YYYY format",
        examples=["15-08-2002"]
    ),

    birth_time: str = Query(
        ...,
        description="Birth Time in HH:MM AM/PM OR HH:MM:SS",
        examples=["1:35 AM"]
    ),

    latitude: float = Query(
        ...,
        description="Latitude of Birth Place",
        examples=[26.8467]
    ),

    longitude: float = Query(
        ...,
        description="Longitude of Birth Place",
        examples=[80.9462]
    ),

    timezone: str = Query(
        default="Asia/Kolkata",
        description="Timezone",
        examples=["Asia/Kolkata"]
    )

):
    try:

        # =====================================
        # PARSE DATE
        # =====================================
        birth_date = datetime.strptime(
            dob,
            "%d-%m-%Y"
        )

        # =====================================
        # PARSE TIME
        # =====================================
        try:

            parsed_time = datetime.strptime(
                birth_time,
                "%I:%M %p"
            )

        except:

            parsed_time = datetime.strptime(
                birth_time,
                "%H:%M:%S"
            )

        # =====================================
        # COMBINE DATE + TIME
        # =====================================
        local_datetime = datetime(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            parsed_time.hour,
            parsed_time.minute,
            parsed_time.second
        )

        # =====================================
        # TIMEZONE
        # =====================================
        local_timezone = pytz.timezone(timezone)

        local_datetime = local_timezone.localize(local_datetime)

        utc_datetime = local_datetime.astimezone(pytz.utc)

        # =====================================
        # JULIAN DAY
        # =====================================
        jd = swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            utc_datetime.hour +
            utc_datetime.minute / 60 +
            utc_datetime.second / 3600
        )

        # =====================================
        # LAHIRI AYANAMSA
        # =====================================
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # =====================================
        # ASCENDANT
        # =====================================
        houses, ascmc = swe.houses_ex(
            jd,
            latitude,
            longitude,
            b'P',
            swe.FLG_SIDEREAL
        )

        ascendant_longitude = ascmc[0]

        asc_sign_no = int(ascendant_longitude / 30) + 1

        asc_sign = SIGNS[asc_sign_no - 1]

        # =====================================
        # SUN POSITION
        # =====================================
        sun_result, _ = swe.calc_ut(
            jd,
            swe.SUN,
            swe.FLG_SIDEREAL | swe.FLG_SPEED
        )

        sun_longitude = sun_result[0]

        # =====================================
        # PLANETARY DATA
        # =====================================
        planetary_data = {}

        for planet_name, planet_code in PLANETS.items():

            result, _ = swe.calc_ut(
                jd,
                planet_code,
                swe.FLG_SIDEREAL | swe.FLG_SPEED
            )

            longitude_value = result[0]

            speed = result[3]

            distance_au = result[2]

            sign_no = int(longitude_value / 30) + 1

            sign_name = SIGNS[sign_no - 1]

            degree_in_sign = longitude_value % 30

            # =====================================
            # RETROGRADE
            # =====================================
            retrograde = speed < 0

            # =====================================
            # COMBUST
            # =====================================
            combust = False

            if planet_code in COMBUST_LIMITS:

                angular_distance = abs(
                    longitude_value - sun_longitude
                )

                if angular_distance > 180:
                    angular_distance = 360 - angular_distance

                combust = (
                    angular_distance <=
                    COMBUST_LIMITS[planet_code]
                )

            # =====================================
            # HOUSE
            # =====================================
            house = get_house(
                longitude_value,
                ascendant_longitude
            )

            # =====================================
            # STORE DATA
            # =====================================
            planetary_data[planet_name] = {

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

                "house": house,

                "retrograde": retrograde,

                "combust": combust,

                "meta_data": {

                    "planet_speed": round(
                        speed,
                        6
                    ),

                    "distance_au": round(
                        distance_au,
                        6
                    )
                }
            }

        # =====================================
        # KETU
        # =====================================
        rahu_longitude = planetary_data["Rahu"]["longitude"]

        ketu_longitude = (
            rahu_longitude + 180
        ) % 360

        ketu_sign_no = int(
            ketu_longitude / 30
        ) + 1

        planetary_data["Ketu"] = {

            "sign_no": ketu_sign_no,

            "sign": SIGNS[ketu_sign_no - 1],

            "longitude": round(
                ketu_longitude,
                6
            ),

            "degree_in_sign": round(
                ketu_longitude % 30,
                6
            ),

            "final_degree": format_degree(
                ketu_longitude % 30
            ),

            "house": get_house(
                ketu_longitude,
                ascendant_longitude
            ),

            "retrograde": planetary_data["Rahu"]["retrograde"],

            "combust": False
        }

        # =====================================
        # RESPONSE
        # =====================================
        return {

            "status": "success",

            "birth_details": {

                "date_of_birth": dob,

                "birth_time": birth_time,

                "timezone": timezone
            },

            "location": {

                "latitude": latitude,

                "longitude": longitude
            },

            "ascendant": {

                "sign_no": asc_sign_no,

                "sign": asc_sign,

                "longitude": round(
                    ascendant_longitude,
                    6
                )
            },

            "meta": {

                "julian_day": round(
                    jd,
                    6
                ),

                "ayanamsa": round(
                    swe.get_ayanamsa_ut(jd),
                    6
                )
            },

            "planetary_data": planetary_data
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================
# RUN SERVER
# =====================================
if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )