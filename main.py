from fastapi import FastAPI, Query
from fastapi.responses import Response
from datetime import datetime
import swisseph as swe
import pytz

# IMPORT MODULES
from kundli.north_chart import generate_north_indian_chart
from kundli.navamsha import calculate_navamsha
from kundli.navamsha_chart import generate_navamsha_chart
from kundli.chandra_kundli import generate_chandra_kundli

# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="Advanced Kundli API",
    version="2.0.0"
)

# ==================================================
# CONSTANTS
# ==================================================

SIGNS = [
    "Aries","Taurus","Gemini","Cancer",
    "Leo","Virgo","Libra","Scorpio",
    "Sagittarius","Capricorn","Aquarius","Pisces"
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
    "Moon":12,
    "Mars":17,
    "Mercury":14,
    "Jupiter":11,
    "Venus":10,
    "Saturn":15
}

# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message":"AstroAPI Running"
    }

# ==================================================
# HELPERS
# ==================================================

def get_sign(longitude):

    sign_no = int(longitude/30)+1

    return (
        sign_no,
        SIGNS[sign_no-1],
        longitude%30
    )


def format_degree(value):

    d=int(value)

    m=int((value-d)*60)

    s=round((((value-d)*60)-m)*60,2)

    return f"{d}° {m}' {s}\""

# ==================================================
# MAIN KUNDLI API
# ==================================================

@app.get("/api/v1/kundali")
def get_kundali(

    dob:str,

    birth_time:str,

    latitude:float,

    longitude:float,

    timezone:str="Asia/Kolkata"
):

    try:

        local_tz=pytz.timezone(timezone)

        dt=datetime.strptime(

            f"{dob} {birth_time.upper()}",

            "%d-%m-%Y %I:%M %p"
        )

        local_dt=local_tz.localize(dt)

        utc_dt=local_dt.astimezone(pytz.utc)

        jd=swe.julday(

            utc_dt.year,

            utc_dt.month,

            utc_dt.day,

            utc_dt.hour+
            utc_dt.minute/60+
            utc_dt.second/3600
        )

        swe.set_sid_mode(
            swe.SIDM_LAHIRI
        )

        houses,ascmc=swe.houses_ex(

            jd,

            latitude,

            longitude,

            b'P',

            swe.FLG_SIDEREAL
        )

        asc_long=ascmc[0]

        asc_sign_no,asc_sign,asc_degree=\
        get_sign(asc_long)

        planetary_data=[]

        for name,pid in PLANETS.items():

            result=swe.calc_ut(

                jd,

                pid,

                swe.FLG_SIDEREAL|
                swe.FLG_SPEED
            )

            longitude_value=result[0][0]

            speed=result[0][3]

            sign_no,sign_name,degree=\
            get_sign(longitude_value)

            house=((

                sign_no-
                asc_sign_no

            )%12)+1

            planetary_data.append({

                "planet":name,

                "sign":sign_name,

                "sign_no":sign_no,

                "degree_in_sign":
                round(degree,2),

                "longitude":
                round(longitude_value,6),

                "house":house,

                "retrograde":
                speed<0,

                "final_degree":
                format_degree(degree)
            })

        house_rashi_map={}

        for house in range(1,13):

            rashi=((

                asc_sign_no+
                house-
                2

            )%12)+1

            house_rashi_map[house]={

                "sign_no":rashi,

                "sign_name":
                SIGNS[rashi-1]
            }

        return {

            "status":"success",

            "planetary_data":
            planetary_data,

            "house_rashi_map":
            house_rashi_map,

            "ascendant":{

                "sign":
                asc_sign,

                "degree":
                asc_degree
            }
        }

    except Exception as e:

        return {

            "status":"error",

            "message":str(e)
        }

# ==================================================
# SVG API
# ==================================================

@app.get("/api/v1/kundli/svg")
def get_kundli_svg(

    dob:str,

    birth_time:str,

    latitude:float,

    longitude:float,

    timezone:str="Asia/Kolkata"
):

    result=get_kundali(

        dob,

        birth_time,

        latitude,

        longitude,

        timezone
    )

    svg=generate_north_indian_chart({

        "planetary_data":
        result["planetary_data"],

        "house_rashi_map":
        result["house_rashi_map"]
    })

    return Response(

        content=svg,

        media_type=
        "image/svg+xml"
    )

# ==================================================
# CHANDRA KUNDLI API
# ==================================================

@app.get("/api/v1/chandra-kundli")
def chandra_kundli(

    dob:str,

    birth_time:str,

    latitude:float,

    longitude:float,

    timezone:str="Asia/Kolkata"
):

    return generate_chandra_kundli(

        dob,

        birth_time,

        latitude,

        longitude,

        timezone
    )

# ==================================================
# NAVAMSHA API
# ==================================================

@app.get("/api/v1/navamsha")
def navamsha(

    dob:str,

    birth_time:str,

    latitude:float,

    longitude:float,

    timezone:str="Asia/Kolkata"
):

    kundali=get_kundali(

        dob,

        birth_time,

        latitude,

        longitude,

        timezone
    )

    return calculate_navamsha(

        kundali["planetary_data"],

        kundali["ascendant"]["degree"]
    )

# ==================================================
# NAVAMSHA SVG
# ==================================================

@app.get("/api/v1/navamsha/svg")
def navamsha_svg(

    dob:str,

    birth_time:str,

    latitude:float,

    longitude:float,

    timezone:str="Asia/Kolkata"
):

    kundali=get_kundali(

        dob,

        birth_time,

        latitude,

        longitude,

        timezone
    )

    nav=calculate_navamsha(

        kundali["planetary_data"],

        kundali["ascendant"]["degree"]
    )

    svg=generate_navamsha_chart(

        nav,

        nav["navamsha_ascendant"]
    )

    return Response(

        content=svg,

        media_type=
        "image/svg+xml"
    )