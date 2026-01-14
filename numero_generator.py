
def generer_prochain_numero_carte_grise(numero_actuel):
    """
    Génère le prochain numéro de carte grise
    Format: YYYYAA00000 (Année + 2 lettres + 5 chiffres)
    
    Incrémentation de droite à gauche:
    1. Incrémentation des 5 chiffres à droite
    2. Puis incrémentation des 2 lettres du milieu
    
    Utilisé dans app.py lignes 212-216 pour la génération automatique
    
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
    
    Utilisé dans app.py lignes 219-240 avec gestion des collisions
    
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
    """
    Formate un numéro de plaque d'immatriculation avec espaces pour l'affichage
    
    Transforme le format compact 'AA000AA' en format lisible 'AA 000 AA'
    utilisé pour l'affichage dans les interfaces utilisateur.
    
    Utilisé dans app.py ligne 284 pour afficher la plaque dans les messages de succès
    
    Args:
        numero (str): Numéro de plaque au format compact (ex: 'AB123CD')
        
    Returns:
        str: Numéro formaté avec espaces (ex: 'AB 123 CD')
        
    Examples:
        >>> formater_numero_plaque('AB123CD')
        'AB 123 CD'
    """
    if len(numero) == 7:
        return f"{numero[:2]} {numero[2:5]} {numero[5:]}"
    return numero


def generer_numero_serie(numero_fabricant, annee, mois, numero_vehicule):
    """
    Génère automatiquement le numéro de série VIN du véhicule
    Format: NumeroFabricant + Année + 'M' + Mois + NuméroSéquentiel (6 chiffres)
    
    Cette fonction est appelée automatiquement lors de l'ajout d'une carte grise
    si l'utilisateur laisse le champ VIN vide. Le numéro est unique par fabricant/mois.
    
    Utilisé dans app.py lignes 270-285 avec logique de comptage de base de données
    
    Args:
        numero_fabricant (str): Code fabricant (ex: 'PEU', 'REN', 'HON')
        annee (int): Année de première immatriculation (ex: 2026)
        mois (int): Mois de première immatriculation (1-12)
        numero_vehicule (int): Compteur séquentiel pour ce fabricant/mois
    
    Returns:
        str: Numéro de série VIN complet (ex: 'PEU2026M01000001')
        
    Examples:
        >>> generer_numero_serie('PEU', 2026, 1, 1)
        'PEU2026M01000001'
        >>> generer_numero_serie('REN', 2026, 12, 157)
        'REN2026M12000157'
    """
    return f"{numero_fabricant}{annee}M{mois:02d}{numero_vehicule:06d}"


# =========================
# Fonctions de logique de base de données 
# (Déplacées depuis app.py lignes 210-285)
# =========================

def generer_numero_carte_grise_depuis_db(db):
    """
    Génère le prochain numéro de carte grise en interrogeant la base de données
    
    Remplace la logique des lignes 212-216 de app.py pour centraliser
    la génération des numéros de cartes grises.
    
    Args:
        db: Objet de connexion à la base de données
        
    Returns:
        str: Prochain numéro de carte grise
    """
    last_carte = db.fetch_one("SELECT numero_carte_grise FROM cartes_grises ORDER BY id DESC LIMIT 1")
    if last_carte and last_carte.get('numero_carte_grise'):
        return generer_prochain_numero_carte_grise(last_carte['numero_carte_grise'])
    else:
        return generer_prochain_numero_carte_grise(None)


def generer_numero_plaque_unique_depuis_db(db):
    """
    Génère un numéro de plaque unique en vérifiant les collisions dans la base de données
    
    Remplace la logique complexe des lignes 219-240 de app.py avec gestion
    des collisions et vérification d'unicité.
    
    Args:
        db: Objet de connexion à la base de données
        
    Returns:
        str: Numéro de plaque unique ou None si impossible
    """
    last_plaque = db.fetch_one("SELECT numero_immatriculation FROM cartes_grises ORDER BY id DESC LIMIT 1")
    if last_plaque and last_plaque.get('numero_immatriculation'):
        numero_plaque = generer_prochain_numero_plaque(last_plaque['numero_immatriculation'])
    else:
        numero_plaque = "AA100AA"
    
    # Vérification de l'unicité avec gestion des collisions
    max_attempts = 10
    attempts = 0
    
    while numero_plaque:
        # Vérification si cette plaque existe déjà
        existing = db.fetch_one("SELECT id FROM cartes_grises WHERE numero_immatriculation=%s", (numero_plaque,))
        if not existing:  # Plaque unique trouvée
            return numero_plaque
        
        # Essai du prochain numéro de plaque
        numero_plaque = generer_prochain_numero_plaque(numero_plaque)
        attempts += 1
        
        if attempts >= max_attempts or numero_plaque is None:
            return None  # Impossible de générer une plaque unique
    
    return None


def generer_numero_serie_depuis_db(db, numero_fabricant, date_premiere_immat):
    """
    Génère automatiquement le numéro VIN en comptant les véhicules existants
    
    Remplace la logique de comptage des lignes 270-285 de app.py pour
    centraliser la génération des VIN avec comptage par fabricant/mois.
    
    Args:
        db: Objet de connexion à la base de données
        numero_fabricant (str): Code fabricant (ex: 'PEU', 'REN')
        date_premiere_immat (str): Date au format 'YYYY-MM-DD'
        
    Returns:
        str: Numéro VIN généré automatiquement
    """
    from datetime import datetime
    
    date_obj = datetime.strptime(date_premiere_immat, '%Y-%m-%d')
    
    # Comptage des véhicules immatriculés pour ce fabricant/mois
    count_query = """
        SELECT COUNT(*) as count FROM cartes_grises 
        WHERE numero_serie LIKE %s
    """
    pattern = f"{numero_fabricant}{date_obj.year}M{date_obj.month:02d}%"
    count_result = db.fetch_one(count_query, (pattern,))
    numero_vehicule = (count_result['count'] + 1) if count_result and count_result.get('count') is not None else 1
    
    return generer_numero_serie(
        numero_fabricant,
        date_obj.year,
        date_obj.month,
        numero_vehicule
    )
