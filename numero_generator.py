"""
Utility functions for generating registration numbers
According to SAE 1.04 specifications
"""

def generer_prochain_numero_carte_grise(numero_actuel):
    """
    Generate next vehicle registration card number
    Format: YYYYAA00000 (Year + 2 letters + 5 digits)
    
    Increment from right to left:
    1. Increment the 5-digit number on the right
    2. Then increment the middle letters
    
    Examples:
    - 2026AA00010 -> 2026AA00011
    - 2026AA99999 -> 2026AB00000
    - 2026AZ99999 -> 2026BA00000
    - 2026ZZ99999 -> 2027AA00000
    """
    if not numero_actuel or len(numero_actuel) != 11:
        # Default starting number for current year
        from datetime import datetime
        year = datetime.now().year
        return f"{year}AA00001"
    
    # Extract components
    annee = numero_actuel[:4]
    lettres = numero_actuel[4:6]
    chiffres = numero_actuel[6:]
    
    # Increment the 5-digit number
    num = int(chiffres) + 1
    
    if num <= 99999:
        # Simple increment of the number
        return f"{annee}{lettres}{num:05d}"
    else:
        # Need to increment letters
        num = 0
        lettres_list = list(lettres)
        
        # Increment second letter
        if lettres_list[1] == 'Z':
            lettres_list[1] = 'A'
            # Increment first letter
            if lettres_list[0] == 'Z':
                # Year rollover
                annee = str(int(annee) + 1)
                lettres_list[0] = 'A'
            else:
                lettres_list[0] = chr(ord(lettres_list[0]) + 1)
        else:
            lettres_list[1] = chr(ord(lettres_list[1]) + 1)
        
        lettres = ''.join(lettres_list)
        return f"{annee}{lettres}{num:05d}"


def generer_prochain_numero_plaque(numero_actuel):
    """
    Generate next license plate number
    Format: AA000AA (2 letters + 3 digits + 2 letters)
    Letters from A to Z, digits from 0 to 9
    Middle digits must be >= 10
    
    Increment from right to left:
    1. Increment the right column letters
    2. Then increment the middle digits (must be >= 10)
    3. Finally increment the left column letters
    
    Examples:
    - AB 78 ZA -> AB 78 ZB
    - AB 78 ZZ -> AB 79 AA
    - AB 999 ZZ -> AC 10 AA
    - ZZ 999 ZZ is the maximum
    """
    # Remove spaces and extract components
    if numero_actuel:
        numero_actuel = numero_actuel.replace(' ', '').replace('-', '')
    
    if not numero_actuel or len(numero_actuel) != 7:
        # Default starting number
        return "AA10AA"
    
    lettres_gauche = numero_actuel[:2]
    chiffres = numero_actuel[2:5]
    lettres_droite = numero_actuel[5:7]
    
    # Convert to lists for easier manipulation
    lettres_d_list = list(lettres_droite)
    
    # Increment right letters
    if lettres_d_list[1] == 'Z':
        lettres_d_list[1] = 'A'
        if lettres_d_list[0] == 'Z':
            # Need to increment middle digits
            lettres_d_list[0] = 'A'
            num = int(chiffres) + 1
            
            if num <= 999:
                chiffres = f"{num:03d}"
            else:
                # Need to increment left letters
                chiffres = "010"  # Reset to minimum (10)
                lettres_g_list = list(lettres_gauche)
                
                if lettres_g_list[1] == 'Z':
                    lettres_g_list[1] = 'A'
                    if lettres_g_list[0] == 'Z':
                        # Maximum reached
                        return None
                    else:
                        lettres_g_list[0] = chr(ord(lettres_g_list[0]) + 1)
                else:
                    lettres_g_list[1] = chr(ord(lettres_g_list[1]) + 1)
                
                lettres_gauche = ''.join(lettres_g_list)
        else:
            lettres_d_list[0] = chr(ord(lettres_d_list[0]) + 1)
    else:
        lettres_d_list[1] = chr(ord(lettres_d_list[1]) + 1)
    
    lettres_droite = ''.join(lettres_d_list)
    return f"{lettres_gauche}{chiffres}{lettres_droite}"


def formater_numero_plaque(numero):
    """Format license plate number with spaces for display"""
    if len(numero) == 7:
        return f"{numero[:2]} {numero[2:5]} {numero[5:]}"
    return numero


def generer_numero_serie(numero_fabricant, annee, mois, numero_vehicule):
    """
    Generate vehicle serial number
    Format: NumeroFabricant + Year (Y) + Month (M) + 6-digit number
    
    Args:
        numero_fabricant: Manufacturer number (e.g., 'PGT', 'REN')
        annee: Manufacturing year
        mois: Manufacturing month (1-12)
        numero_vehicule: Sequential vehicle number (incremented per month)
    
    Returns:
        Serial number string
    """
    return f"{numero_fabricant}{annee}M{mois:02d}{numero_vehicule:06d}"
