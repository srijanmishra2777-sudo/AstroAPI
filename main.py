from fastapi import FastAPI, HTTPException
from datetime import datetime
from jhora.panchanga import drik
import swisseph as swe
import math

app = FastAPI()

# =========================
# SIDEREAL MODE (LAHIRI)
# =========================
swe.set_sid_mode(swe.SIDM_LAHIRI)

# =========================
# PLANETS
# =========================
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO
}

# =========================
# ZODIAC SIGNS
# =========================
SIGNS = {
    1: "Aries",
    2: "Taurus",
    3: "Gemini",
    4: "Cancer",
    5: "Leo",
    6: "Virgo",
    7: "Libra",
    8: "Scorpio",
    9: "Sagittarius",
    10: "Capricorn",
    11: "Aquarius",
    12: "Pisces"
}

# =========================
# NAKSHATRAS
# =========================
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika",
    "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# =========================
# DEGREE FORMAT
# =========================
def decimal_to_dms(degree):
    d = int(degree)
    m_float = (degree - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60, 2)
    return f"{d}° {m}' {s}\""

# =========================
# NAKSHATRA
# =========================
def get_nakshatra(longitude):
    index = int(longitude / (360 / 27))
    return NAKSHATRAS[index]

# =========================
# COMBUST CHECK
# =========================
def is_combust(planet, planet_longitude, sun_longitude):

    if planet == "Sun":
        return False

    difference = abs(planet_longitude - sun_longitude)

    if difference > 180:
        difference = 360 - difference

    combust_limits = {
        "Moon": 12,
        "Mars": 17,
        "Mercury": 14,
        "Jupiter": 11,
        "Venus": 10,
        "Saturn": 15
    }

    limit = combust_limits.get(planet, 8)

    return difference < limit

# =========================
# VARGOTTAMA
# =========================
def check_vargottama(longitude, sign_no):

    degree_in_sign = longitude % 30

    navamsa_sign = int((degree_in_sign / (30 / 9))) + 1

    return sign_no == navamsa_sign

# =========================
# API
# =========================
@app.get("/")
def home():
    return {
        "message": "Astrology API Running Successfully"
    }

# =========================
# PLANETARY API
# =========================
@app.get("/planetary-positions")
def planetary_positions(
    dob: str,
    tob: str,
    latitude: float,
    longitude: float
):

    try:

        # =========================
        # DATE PARSE
        # =========================
        birth_date = datetime.strptime(dob, "%d-%m-%Y")

        # =========================
        # TIME PARSE
        # =========================
        birth_time = datetime.strptime(tob, "%I:%M %p")

        year = birth_date.year
        month = birth_date.month
        day = birth_date.day

        hour = birth_time.hour
        minute = birth_time.minute

        decimal_hour = hour + (minute / 60)

        # =========================
        # JULIAN DAY
        # =========================
        jd = swe.julday(
            year,
            month,
            day,
            decimal_hour
        )

        # =========================
        # SUNRISE / SUNSET
        # =========================
        place = drik.Place(
            "Custom Place",
            latitude,
            longitude,
            5.5
        )

        date_obj = drik.Date(year, month, day)

        sunrise = drik.sunrise(jd, place)
        sunset = drik.sunset(jd, place)

        # =========================
        # ASCENDANT
        # =========================
        houses = swe.houses(
            jd,
            latitude,
            longitude
        )

        asc_longitude = houses[1][0]

        asc_sign_no = int(asc_longitude / 30) + 1

        asc_sign = SIGNS[asc_sign_no]

        # =========================
        # SUN LONGITUDE
        # =========================
        sun_calc = swe.calc_ut(jd, swe.SUN)

        sun_longitude = sun_calc[0][0]

        results = []

        # =========================
        # PLANET LOOP
        # =========================
        for planet_name, planet_code in PLANETS.items():

            planet_calc = swe.calc_ut(jd, planet_code)

            planet_data = planet_calc[0]

            longitude_value = planet_data[0]

            latitude_value = planet_data[1]

            distance = planet_data[2]

            speed = planet_data[3]

            # =========================
            # SIGN
            # =========================
            sign_no = int(longitude_value / 30) + 1

            sign_name = SIGNS[sign_no]

            degree_in_sign = longitude_value % 30

            # =========================
            # RETROGRADE
            # =========================
            retrograde = speed < 0

            # =========================
            # NAKSHATRA
            # =========================
            nakshatra = get_nakshatra(longitude_value)

            # =========================
            # COMBUST
            # =========================
            combust = is_combust(
                planet_name,
                longitude_value,
                sun_longitude
            )

            # =========================
            # VARGOTTAMA
            # =========================
            vargottama = check_vargottama(
                longitude_value,
                sign_no
            )

            results.append({
                "planet": planet_name,

                "sign_no": sign_no,

                "sign": sign_name,

                "longitude": round(longitude_value, 6),

                "degree_in_sign": round(degree_in_sign, 6),

                "final_degree": decimal_to_dms(
                    degree_in_sign
                ),

                "nakshatra": nakshatra,

                "retrograde": retrograde,

                "combust": combust,

                "vargottama": vargottama,

                "altitude": round(latitude_value, 6),

                "meta_data": {
                    "planet_speed": round(speed, 6),
                    "distance_au": round(distance, 6),
                    "raw_longitude": round(longitude_value, 6)
                }
            })

        # =========================
        # FINAL RESPONSE
        # =========================
        return {

            "status": "success",

            "birth_details": {
                "date_of_birth": dob,
                "birth_time": tob
            },

            "location": {
                "latitude": latitude,
                "longitude": longitude
            },

            "current_local_time": datetime.now().strftime(
                "%Y-%m-%d %I:%M:%S %p"
            ),

            "sunrise": str(sunrise),

            "sunset": str(sunset),

            "atmospheric_pressure_hPa": 1013.25,

            "ascendant": {
                "sign_no": asc_sign_no,
                "sign": asc_sign,
                "degree": round(asc_longitude, 6)
            },

            "planetary_data": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )