def generate_kundli_chart(planets):

    houses = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
        7: [],
        8: [],
        9: [],
        10: [],
        11: [],
        12: []
    }

    for planet in planets:

        house_no = planet["house"]

        houses[house_no].append(planet["planet"])

    return houses