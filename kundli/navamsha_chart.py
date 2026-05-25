def generate_navamsha_chart(navamsha_data, navamsha_ascendant):
    """
    Generate Navamsha (D9) chart as SVG
    Navamsha chart uses the same North Indian style layout
    """
    
    # =========================================================
    # ORGANIZE PLANETS BY NAVAMSHA HOUSE
    # =========================================================
    
    # Calculate Navamsha houses based on ascendant
    asc_sign_no = navamsha_ascendant["sign_no"]
    
    # Create house mapping (1-12 houses)
    house_rashi_map = {}
    for house in range(1, 13):
        rashi_no = ((asc_sign_no + house - 2) % 12) + 1
        house_rashi_map[house] = {
            "sign_no": rashi_no,
            "sign_name": get_sign_name_from_no(rashi_no)
        }
    
    # Place planets in Navamsha houses
    house_data = {i: [] for i in range(1, 13)}
    
    for planet in navamsha_data["navamsha_planets"]:
        # Calculate which house this planet falls in based on Navamsha ascendant
        planet_sign_no = planet["navamsha_sign_no"]
        house = ((planet_sign_no - asc_sign_no) % 12) + 1
        
        # Format planet text
        retro_text = " (R)" if planet.get("retrograde") else ""
        combust_text = " 🔥" if planet.get("combust") else ""
        pada_text = f" P{planet['pada']}"
        
        text = f'{planet["planet"]}{retro_text}{combust_text}\n{planet["navamsha_degree"]}°{pada_text}'
        
        house_data[house].append(text)
    
    # =========================================================
    # HOUSE POSITIONS FOR NAVAMSHA CHART
    # =========================================================
    
    house_positions = {
        1:  (600, 170),
        2:  (380, 280),
        3:  (200, 450),
        4:  (380, 600),
        5:  (200, 780),
        6:  (380, 950),
        7:  (600, 1040),
        8:  (820, 950),
        9:  (1000, 780),
        10: (820, 600),
        11: (1000, 450),
        12: (820, 280)
    }
    
    # =========================================================
    # CREATE CENTER GRAPHIC FOR NAVAMSHA
    # =========================================================
    
    center_graphic = """
    <g transform="translate(600, 600)">
        <!-- Outer decorative circle -->
        <circle cx="0" cy="0" r="100" fill="#faf0e6" stroke="#8B4513" stroke-width="3"/>
        <circle cx="0" cy="0" r="95" fill="none" stroke="#DAA520" stroke-width="1" stroke-dasharray="5,5"/>
        <circle cx="0" cy="0" r="85" fill="none" stroke="#8B4513" stroke-width="2"/>
        
        <!-- D9 / Navamsha Text -->
        <text x="0" y="-15" 
              font-size="42" 
              text-anchor="middle" 
              dominant-baseline="central"
              fill="#8B4513" 
              font-family="Arial, sans-serif"
              font-weight="bold">
            D9
        </text>
        
        <text x="0" y="20" 
              font-size="14" 
              text-anchor="middle" 
              fill="#DAA520" 
              font-family="Arial, sans-serif"
              font-weight="bold">
            Navamsha
        </text>
        
        <!-- Small decorative dots -->
        <circle cx="0" cy="-70" r="3" fill="#DAA520"/>
        <circle cx="60" cy="-35" r="3" fill="#DAA520"/>
        <circle cx="60" cy="35" r="3" fill="#DAA520"/>
        <circle cx="0" cy="70" r="3" fill="#DAA520"/>
        <circle cx="-60" cy="35" r="3" fill="#DAA520"/>
        <circle cx="-60" cy="-35" r="3" fill="#DAA520"/>
        
        <!-- Inner ring text -->
        <path id="ringText" d="M 0,-75 A 75,75 0 1,1 0,75 A 75,75 0 1,1 0,-75" fill="none"/>
        <text font-size="10" fill="#8B4513" font-family="Arial">
            <textPath href="#ringText" startOffset="50%" text-anchor="middle">
                ✧ DIVISIONAL CHART ✧
            </textPath>
        </text>
    </g>
"""
    
    # =========================================================
    # SVG START
    # =========================================================
    
    svg = f"""
<svg width="1200"
     height="1200"
     xmlns="http://www.w3.org/2000/svg">

    <!-- BACKGROUND -->
    <rect width="1200"
          height="1200"
          fill="#fdfaf6"/>

    <!-- OUTER BORDER -->
    <rect x="100"
          y="100"
          width="1000"
          height="1000"
          fill="none"
          stroke="#8B4513"
          stroke-width="5"
          rx="10"/>

    <!-- MAIN DIAGONALS -->
    <line x1="100"
          y1="100"
          x2="1100"
          y2="1100"
          stroke="#8B4513"
          stroke-width="4"/>

    <line x1="1100"
          y1="100"
          x2="100"
          y2="1100"
          stroke="#8B4513"
          stroke-width="4"/>

    <!-- CENTER DIAMOND -->
    <polygon points="
        600,100
        1100,600
        600,1100
        100,600"
        fill="none"
        stroke="#8B4513"
        stroke-width="4"/>

    <!-- CENTER CIRCLE BACKGROUND -->
    <circle cx="600"
            cy="600"
            r="120"
            fill="white"
            stroke="#8B4513"
            stroke-width="4"/>

    <!-- CENTER GRAPHIC -->
    {center_graphic}

    <!-- TITLE -->
    <text x="600"
          y="60"
          font-size="34"
          text-anchor="middle"
          font-weight="bold"
          fill="#8B4513"
          font-family="Arial, sans-serif">
        🕉️ Navamsha (D9) Chart
    </text>
    
    <!-- Subtitle -->
    <text x="600"
          y="85"
          font-size="14"
          text-anchor="middle"
          fill="#DAA520"
          font-family="Arial, sans-serif">
        Divisional Chart for Marriage, Dharma, and Fortune
    </text>
"""
    
    # =========================================================
    # DRAW HOUSES WITH RASHI SIGNS
    # =========================================================
    
    for house, (x, y) in house_positions.items():
        # Get rashi sign for this house
        rashi_name = house_rashi_map[house]["sign_name"][:3]
        
        # HOUSE NUMBER with background
        svg += f"""
    <!-- House {house} -->
    <rect x="{x-35}"
          y="{y-30}"
          width="70"
          height="50"
          fill="#faf0e6"
          rx="5"
          stroke="#DAA520"
          stroke-width="1.5"/>
    
    <text x="{x}"
          y="{y}"
          font-size="20"
          text-anchor="middle"
          font-weight="bold"
          fill="#8B4513"
          font-family="Arial, sans-serif">
        {house}
    </text>
    
    <text x="{x}"
          y="{y+18}"
          font-size="11"
          text-anchor="middle"
          fill="#DAA520"
          font-family="Arial, sans-serif">
        {rashi_name}
    </text>
"""
        
        yy = y + 38
        
        # PLANETS in this house
        for item in house_data[house][:4]:  # Max 4 planets per house
            # Determine color based on planet
            color = "#34495e"
            if "Sun" in item:
                color = "#e67e22"
            elif "Moon" in item:
                color = "#3498db"
            elif "Mars" in item:
                color = "#e74c3c"
            elif "Mercury" in item:
                color = "#27ae60"
            elif "Jupiter" in item:
                color = "#8e44ad"
            elif "Venus" in item:
                color = "#e84393"
            elif "Saturn" in item:
                color = "#2c3e50"
            elif "Rahu" in item:
                color = "#7f8c8d"
            elif "Ketu" in item:
                color = "#95a5a6"
            
            svg += f"""
    <text x="{x}"
          y="{yy}"
          font-size="12"
          text-anchor="middle"
          fill="{color}"
          font-family="Arial, sans-serif">
        {item}
    </text>
"""
            yy += 17
    
    # =========================================================
    # LEGEND AND FOOTER
    # =========================================================
    
    svg += f"""
    <!-- Legend -->
    <g transform="translate(100, 1130)">
        <text x="0" y="0" font-size="10" fill="#7f8c8d" font-family="Arial, sans-serif">
            🔥 Combust  |  (R) Retrograde  |  P1-P9: Navamsha Pada
        </text>
    </g>
    
    <!-- Footer -->
    <text x="600"
          y="1160"
          font-size="12"
          text-anchor="middle"
          fill="#95a5a6"
          font-family="Arial, sans-serif">
        Navamsha (D9) Chart • {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </text>
    
    </svg>
"""
    
    return svg

def get_sign_name_from_no(sign_no):
    """Get sign name from sign number (1-12)"""
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[sign_no - 1]