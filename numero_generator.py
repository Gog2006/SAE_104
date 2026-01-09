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
        # Default starting number: AA100AA
        return "AA100AA"
    
    lettres_gauche = numero_actuel[:2]
    chiffres = numero_actuel[2:5]
    lettres_droite = numero_actuel[5:7]
    
    # Convert to working numbers
    num_chiffres = int(chiffres)
    lg_1 = ord(lettres_gauche[0]) - ord('A')
    lg_2 = ord(lettres_gauche[1]) - ord('A')
    ld_1 = ord(lettres_droite[0]) - ord('A')
    ld_2 = ord(lettres_droite[1]) - ord('A')
    
    # Start incrementing from the rightmost position
    # Right-most letter (ld_2)
    ld_2 += 1
    if ld_2 <= 25:
        # No carry needed
        pass
    else:
        # Carry to next position (ld_1)
        ld_2 = 0
        ld_1 += 1
        if ld_1 <= 25:
            # No carry needed
            pass
        else:
            # Carry to middle digits
            ld_1 = 0
            num_chiffres += 1
            if num_chiffres <= 999:
                # No carry needed
                pass
            else:
                # Carry to left letters
                num_chiffres = 10  # Reset to minimum valid
                lg_2 += 1
                if lg_2 <= 25:
                    # No carry needed
                    pass
                else:
                    # Carry to leftmost letter
                    lg_2 = 0
                    lg_1 += 1
                    if lg_1 > 25:
                        # Maximum reached
                        return None
    
    # Reconstruct the plate
    lettres_gauche = chr(ord('A') + lg_1) + chr(ord('A') + lg_2)
    lettres_droite = chr(ord('A') + ld_1) + chr(ord('A') + ld_2)
    chiffres = f"{num_chiffres:03d}"
    
    # Validate the result
    if num_chiffres < 10 or num_chiffres > 999:
        return None
    
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
