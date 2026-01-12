"""
Fonctions utilitaires pour la génération des numéros d'immatriculation
Selon les spécifications SAE 1.04
"""

def generer_prochain_numero_carte_grise(numero_actuel):
    """
    Génère le prochain numéro de carte grise
    Format: YYYYAA00000 (Année + 2 lettres + 5 chiffres)
    
    Incrémentation de droite à gauche:
    1. Incrémentation des 5 chiffres à droite
    2. Puis incrémentation des 2 lettres du milieu
    
    Exemples:
    - 2026AA00010 -> 2026AA00011
    - 2026AA99999 -> 2026AB00000
    - 2026AZ99999 -> 2026BA00000
    - 2026ZZ99999 -> 2027AA00000
    """
    if not numero_actuel or len(numero_actuel) != 11:
        # Numéro de départ pour l'année courante
        from datetime import datetime
        year = datetime.now().year
        return f"{year}AA00001"
    
    # Extraction des composantes
    annee = numero_actuel[:4]
    lettres = numero_actuel[4:6]
    chiffres = numero_actuel[6:]
    
    # Incrémentation des 5 chiffres
    num = int(chiffres) + 1
    
    if num <= 99999:
        # Simple incrémentation du nombre
        return f"{annee}{lettres}{num:05d}"
    else:
        # Besoin d'incrémenter les lettres
        num = 0
        lettres_list = list(lettres)
        
        # Incrémentation de la deuxième lettre
        if lettres_list[1] == 'Z':
            lettres_list[1] = 'A'
            # Incrémentation de la première lettre
            if lettres_list[0] == 'Z':
                # Changement d'année
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
    Génère le prochain numéro de plaque d'immatriculation
    Format: AA000AA (2 lettres + 3 chiffres + 2 lettres)
    Les lettres vont de A à Z, les chiffres de 0 à 9
    Les 3 chiffres du milieu doivent être >= 10
    
    Incrémentation de droite à gauche:
    1. Incrémentation des lettres de droite
    2. Puis incrémentation des 3 chiffres du milieu (>=10)
    3. Enfin incrémentation des lettres de gauche
    
    Exemples:
    - AB 78 ZA -> AB 78 ZB
    - AB 78 ZZ -> AB 79 AA
    - AB 999 ZZ -> AC 10 AA
    - ZZ 999 ZZ est le maximum
    """
    # Suppression des espaces et tirets
    if numero_actuel:
        numero_actuel = numero_actuel.replace(' ', '').replace('-', '')
    
    if not numero_actuel or len(numero_actuel) != 7:
        # Numéro de départ: AA100AA
        return "AA100AA"
    
    lettres_gauche = numero_actuel[:2]
    chiffres = numero_actuel[2:5]
    lettres_droite = numero_actuel[5:7]
    
    # Conversion en nombres de travail
    num_chiffres = int(chiffres)
    lg_1 = ord(lettres_gauche[0]) - ord('A')
    lg_2 = ord(lettres_gauche[1]) - ord('A')
    ld_1 = ord(lettres_droite[0]) - ord('A')
    ld_2 = ord(lettres_droite[1]) - ord('A')
    
    # Début de l'incrémentation à partir de la position la plus à droite
    # Lettre la plus à droite (ld_2)
    ld_2 += 1
    if ld_2 <= 25:
        # Pas de report nécessaire
        pass
    else:
        # Report à la position suivante (ld_1)
        ld_2 = 0
        ld_1 += 1
        if ld_1 <= 25:
            # Pas de report nécessaire
            pass
        else:
            # Report aux chiffres du milieu
            ld_1 = 0
            num_chiffres += 1
            if num_chiffres <= 999:
                # Pas de report nécessaire
                pass
            else:
                # Report aux lettres de gauche
                num_chiffres = 10  # Réinitialisation au minimum valide
                lg_2 += 1
                if lg_2 <= 25:
                    # Pas de report nécessaire
                    pass
                else:
                    # Report à la lettre la plus à gauche
                    lg_2 = 0
                    lg_1 += 1
                    if lg_1 > 25:
                        # Maximum atteint
                        return None
    
    # Reconstruction de la plaque
    lettres_gauche = chr(ord('A') + lg_1) + chr(ord('A') + lg_2)
    lettres_droite = chr(ord('A') + ld_1) + chr(ord('A') + ld_2)
    chiffres = f"{num_chiffres:03d}"
    
    # Validation du résultat
    if num_chiffres < 10 or num_chiffres > 999:
        return None
    
    return f"{lettres_gauche}{chiffres}{lettres_droite}"


def formater_numero_plaque(numero):
    """Formate le numéro de plaque avec espaces pour l'affichage"""
    if len(numero) == 7:
        return f"{numero[:2]} {numero[2:5]} {numero[5:]}"
    return numero


def generer_numero_serie(numero_fabricant, annee, mois, numero_vehicule):
    """
    Génère le numéro de série du véhicule
    Format: NumeroFabricant + Année (Y) + Mois (M) + nombre 6 chiffres
    
    Args:
        numero_fabricant: Numéro du fabricant (ex: 'PGT', 'REN')
        annee: Année de fabrication
        mois: Mois de fabrication (1-12)
        numero_vehicule: Numéro séquentiel du véhicule (incrémenté par mois)
    
    Returns:
        Chaîne contenant le numéro de série
    """
    return f"{numero_fabricant}{annee}M{mois:02d}{numero_vehicule:06d}"
