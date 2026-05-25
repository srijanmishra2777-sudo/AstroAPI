import swisseph as swe
import math

def calculate_navamsha(planets, ascendant_degree):
    """
    Calculate Navamsha (D9) positions for all planets and ascendant
    
    Navamsha divides each sign into 9 equal parts of 3°20' each
    The Navamsha sign depends on which pada (quarter) the planet falls in
    """
    
    # Each sign is divided into 9 parts of 3.333... degrees
    NAVAMSHA_DEGREE = 360 / (12 * 9)  # = 3.3333333333 degrees
    DEGREES_PER_SIGN = 30
    NAVAMSHAS_PER_SIGN = 9
    
    def get_navamsha_sign(degree, is_planet=True):
        """
        Calculate Navamsha sign for a given degree
        For planets: Movable/Fixed/Dual signs mapping
        For ascendant: Sequential mapping
        """
        # Get the sign number (0-11)
        sign_no = int(degree / DEGREES_PER_SIGN)
        degree_in_sign = degree % DEGREES_PER_SIGN
        
        # Calculate which navamsha part (0-8)
        navamsha_part = int(degree_in_sign / NAVAMSHA_DEGREE)
        
        if is_planet:
            # For planets: Special mapping based on sign type
            sign_type = sign_no % 3  # 0: Movable, 1: Fixed, 2: Dual
            
            # Navamsha sign mapping table
            if sign_type == 0:  # Movable signs (Aries, Cancer, Libra, Capricorn)
                navamsha_mapping = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # Same order
            elif sign_type == 1:  # Fixed signs (Taurus, Leo, Scorpio, Aquarius)
                navamsha_mapping = [8, 7, 6, 5, 4, 3, 2, 1, 0]  # Reverse order
            else:  # Dual signs (Gemini, Virgo, Sagittarius, Pisces)
                navamsha_mapping = [0, 2, 4, 6, 8, 1, 3, 5, 7]  # Special order
            
            navamsha_sign_no = navamsha_mapping[navamsha_part]
        else:
            # For ascendant: Sequential mapping
            # First navamsha goes to same sign, then next signs
            navamsha_sign_no = (sign_no + navamsha_part) % 12
        
        return navamsha_sign_no, navamsha_part + 1  # Return 1-based pada
    
    # Calculate Navamsha for each planet
    navamsha_data = []
    
    for planet in planets:
        navamsha_sign_no, pada = get_navamsha_sign(planet["longitude"], is_planet=True)
        
        # Calculate degree in navamsha sign
        degree_in_navamsha = (planet["degree_in_sign"] % NAVAMSHA_DEGREE) / NAVAMSHA_DEGREE * 30
        
        navamsha_data.append({
            "planet": planet["planet"],
            "original_sign": planet["sign"],
            "original_house": planet["house"],
            "original_degree": planet["degree_in_sign"],
            "navamsha_sign_no": navamsha_sign_no + 1,
            "navamsha_sign": get_sign_name(navamsha_sign_no),
            "navamsha_degree": round(degree_in_navamsha, 2),
            "pada": pada,
            "retrograde": planet.get("retrograde", False),
            "combust": planet.get("combust", False)
        })
    
    # Calculate Navamsha for Ascendant
    navamsha_asc_sign_no, asc_pada = get_navamsha_sign(ascendant_degree, is_planet=False)
    degree_in_navamsha_asc = (ascendant_degree % NAVAMSHA_DEGREE) / NAVAMSHA_DEGREE * 30
    
    return {
        "navamsha_planets": navamsha_data,
        "navamsha_ascendant": {
            "sign_no": navamsha_asc_sign_no + 1,
            "sign": get_sign_name(navamsha_asc_sign_no),
            "degree": round(degree_in_navamsha_asc, 2),
            "pada": asc_pada
        }
    }

def get_sign_name(sign_no):
    """Get sign name from sign number (0-11)"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[sign_no]