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