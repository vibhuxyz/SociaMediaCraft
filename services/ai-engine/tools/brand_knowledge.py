def fetch_brand_guidelines(brand_name: str) -> str:
    """
    Fetches the brand guidelines, tone, and colors for a specific company.
    """
    db = {
        "apple": "Tone: Minimalist, premium. Colors: White, Black, Silver. Focus: Privacy, Innovation.",
        "nike": "Tone: Inspiring, energetic. Colors: Black, White, Neon. Focus: Athletic excellence, determination."
    }
    
    return db.get(brand_name.lower(), "No specific brand guidelines found. Use standard best practices.")
