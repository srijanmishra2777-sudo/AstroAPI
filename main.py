from fastapi import FastAPI
from datetime import datetime
import swisseph as swe
import requests

app = FastAPI()

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

def zodiac_sign(longitude):
    return SIGNS[int(longitude // 30)]

@app.get("/")
def home():
    return {
        "message": "Birth Planetary API Running"
    }

@app.get("/planetary-positions")
def planetary_positions(

    birth_date: str = "2000-01-01",
    birth_time: str = "10:30",
    am_pm: str = "AM",

    latitude: float = 28.6139,
    longitude: float = 77.2090
):

    # Convert time to 24-hour format
    hour, minute = map(int, birth_time.split(":"))

    if am_pm.upper() == "PM" and hour != 12:
        hour += 12

    if am_pm.upper() == "AM" and hour == 12:
        hour = 0

    # Parse birth date
    date_obj = datetime.strptime(
        birth_date,
        "%Y-%m-%d"
    )

    # Julian Day
    jd = swe.julday(
        date_obj.year,
        date_obj.month,
        date_obj.day,
        hour + minute / 60
    )

    planetary_result = []

    # Planet calculations
    for planet_name, planet_code in PLANETS.items():

        data = swe.calc_ut(jd, planet_code)

        longitude_value = data[0][0]

        speed = data[0][3]

        planetary_result.append({
            "planet": planet_name,
            "longitude": round(longitude_value, 2),
            "sign": zodiac_sign(longitude_value),
            "retrograde": speed < 0
        })

    # Weather API
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&current=surface_pressure"
        f"&daily=sunrise,sunset"
        f"&timezone=auto"
    )

    weather_response = requests.get(weather_url)

    weather_data = weather_response.json()

    pressure = weather_data["current"]["surface_pressure"]

    sunrise = weather_data["daily"]["sunrise"][0]

    sunset = weather_data["daily"]["sunset"][0]

    local_time = weather_data["current"]["time"]

    return {

        "status": "success",

        "birth_details": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "am_pm": am_pm
        },

        "location": {
            "latitude": latitude,
            "longitude": longitude
        },

        "current_local_time": local_time,

        "sunrise": sunrise,

        "sunset": sunset,

        "atmospheric_pressure_hPa": pressure,

        "planetary_data": planetary_result
    }