# Importation des modules Flask pour les routes, templates et gestion des requêtes
from flask import Flask, render_template, request, redirect, url_for, flash
# Protection CSRF (Cross-Site Request Forgery)
from flask_wtf.csrf import CSRFProtect
# Fonction pour échapper les caractères HTML (sécurité)
from markupsafe import escape
# Module de gestion de la base de données
from database import Database
# Fonctions de génération de numéros pour cartes grises et plaques
from numero_generator import (
    generer_prochain_numero_carte_grise,
    generer_prochain_numero_plaque,
    formater_numero_plaque,
    generer_numero_serie
)
import os
from datetime import datetime

# Initialisation de l'application Flask
app = Flask(__name__)
# Configuration de la clé secrète pour les sessions (CSRF, etc.)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Activation de la protection CSRF (protection contre les attaques cross-site)
csrf = CSRFProtect(app)

# Initialisation de la connexion à la base de données
db = Database()

# Hook exécuté avant chaque requête HTTP
@app.before_request
def before_request():
    """Connexion à la base de données avant chaque requête"""
    if not db.connection or not db.connection.is_connected():
        if not db.connect():
            flash('Erreur de connexion à la base de données. Veuillez vérifier votre configuration.', 'error')

# Hook exécuté après chaque requête HTTP
@app.teardown_appcontext
def teardown_db(exception=None):
    """Ferme la connexion à la base de données après chaque requête"""
    if db.connection and db.connection.is_connected():
        db.connection.close()

@app.route('/')
def index():
    """Page d'accueil - Affiche toutes les cartes grises"""
    # Requête pour récupérer les cartes grises avec les informations du propriétaire et du modèle
    query = """
        SELECT cg.*, 
               p.nom, p.prenom, p.adresse,
               mo.modele, mo.type_vehicule,
               ma.nom as marque_nom
        FROM cartes_grises cg
        JOIN proprietaires p ON cg.proprietaire_id = p.id
        JOIN modeles mo ON cg.modele_id = mo.id
        JOIN marques ma ON mo.marque_id = ma.id
        ORDER BY cg.date_immat_actuelle DESC
    """
    cartes = db.fetch_all(query)
    return render_template('index.html', cartes=cartes)

@app.route('/add', methods=['GET', 'POST'])
def add_carte_grise():
    """Ajoute une nouvelle carte grise avec fonction d'auto-remplissage des caractéristiques"""

    # Données techniques de référence pour chaque modèle
    # Format: ID_MODELE: {'pv': poids_vide, 'pm': poids_max, 'permis': catégorie, 'pl': places, 'cyl': cylindrée, 'cv': chevaux, 'co2': émission}
    DONNEES_TECHNIQUES_REF = {
        # Honda
        1: {'pv': 190, 'pm': 370, 'permis': 'A2', 'pl': 2, 'cyl': 471, 'cv': 48, 'co2': 80, 'classe': 'Euro 5'},   # CB500F
        2: {'pv': 201, 'pm': 390, 'permis': 'A', 'pl': 2, 'cyl': 999, 'cv': 217, 'co2': 160, 'classe': 'Euro 4'},  # CBR1000RR
        3: {'pv': 1300, 'pm': 1800, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 182, 'co2': 128, 'classe': 'Euro 6d'}, # Civic
        4: {'pv': 1600, 'pm': 2200, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 184, 'co2': 153, 'classe': 'Euro 6d'}, # CR-V
        5: {'pv': 2800, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2999, 'cv': 150, 'co2': 210, 'classe': 'Euro 6'}, # NT400
        6: {'pv': 2600, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 130, 'co2': 220, 'classe': 'Euro 6'}, # Cabstar
        # Peugeot
        7: {'pv': 95, 'pm': 270, 'permis': 'A1', 'pl': 2, 'cyl': 49, 'cv': 4, 'co2': 45, 'classe': 'Euro 5'},     # Kisbee
        8: {'pv': 280, 'pm': 450, 'permis': 'A', 'pl': 2, 'cyl': 399, 'cv': 36, 'co2': 89, 'classe': 'Euro 5'},    # Metropolis
        9: {'pv': 1050, 'pm': 1550, 'permis': 'B', 'pl': 5, 'cyl': 1199, 'cv': 100, 'co2': 102, 'classe': 'Euro 6d'}, # 208
        10: {'pv': 1500, 'pm': 2100, 'permis': 'B', 'pl': 7, 'cyl': 1598, 'cv': 180, 'co2': 140, 'classe': 'Euro 6d'},# 5008
        11: {'pv': 2100, 'pm': 4400, 'permis': 'C', 'pl': 3, 'cyl': 2179, 'cv': 140, 'co2': 230, 'classe': 'Euro 6'},# Boxer
        12: {'pv': 1800, 'pm': 3100, 'permis': 'C', 'pl': 3, 'cyl': 1997, 'cv': 145, 'co2': 190, 'classe': 'Euro 6'},# Expert
       
       # RENAULT (IDs 13 à 18)
        13: {'pv': 120, 'pm': 300, 'permis': 'A1', 'pl': 2, 'cyl': 124, 'cv': 11, 'co2': 55, 'classe': 'Euro 5'},     # Full 125
        14: {'pv': 160, 'pm': 340, 'permis': 'A2', 'pl': 2, 'cyl': 395, 'cv': 30, 'co2': 75, 'classe': 'Euro 5'},     # Sport 400
        15: {'pv': 1100, 'pm': 1600, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 90, 'co2': 110, 'classe': 'Euro 6d'},   # Clio
        16: {'pv': 1400, 'pm': 1950, 'permis': 'B', 'pl': 5, 'cyl': 1332, 'cv': 140, 'co2': 130, 'classe': 'Euro 6d'}, # Austral
        17: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2299, 'cv': 135, 'co2': 240, 'classe': 'Euro 6'}, # Master
        18: {'pv': 2400, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 140, 'co2': 250, 'classe': 'Euro 6'}, # Maxity

       # MERCEDES (19-24)
        19: {'pv': 130, 'pm': 310, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 12, 'co2': 60, 'classe': 'Euro 5'},   # Citan Scooter
        20: {'pv': 210, 'pm': 400, 'permis': 'A', 'pl': 2, 'cyl': 998, 'cv': 200, 'co2': 155, 'classe': 'Euro 4'},  # Vision GT
        21: {'pv': 1350, 'pm': 1900, 'permis': 'B', 'pl': 5, 'cyl': 1461, 'cv': 116, 'co2': 120, 'classe': 'Euro 6d'}, # Classe A
        22: {'pv': 1800, 'pm': 2400, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 190, 'co2': 160, 'classe': 'Euro 6d'}, # GLC
        23: {'pv': 2600, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2143, 'cv': 163, 'co2': 215, 'classe': 'Euro 6'}, # Sprinter 5t
        24: {'pv': 2900, 'pm': 4800, 'permis': 'C', 'pl': 3, 'cyl': 4250, 'cv': 170, 'co2': 230, 'classe': 'Euro 6'}, # Vario

        # IVECO (25-30)
        25: {'pv': 150, 'pm': 330, 'permis': 'A2', 'pl': 2, 'cyl': 300, 'cv': 28, 'co2': 70, 'classe': 'Euro 5'},    # Daily Moto
        26: {'pv': 220, 'pm': 420, 'permis': 'A', 'pl': 2, 'cyl': 1100, 'cv': 210, 'co2': 165, 'classe': 'Euro 4'},   # Turbo Bike
        27: {'pv': 2000, 'pm': 2800, 'permis': 'B', 'pl': 5, 'cyl': 2998, 'cv': 176, 'co2': 200, 'classe': 'Euro 6'}, # Massif
        28: {'pv': 1900, 'pm': 2600, 'permis': 'B', 'pl': 5, 'cyl': 2500, 'cv': 150, 'co2': 190, 'classe': 'Euro 6'}, # Campagnola
        29: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2300, 'cv': 140, 'co2': 225, 'classe': 'Euro 6'}, # Daily 35C
        30: {'pv': 2500, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2998, 'cv': 180, 'co2': 245, 'classe': 'Euro 6'}, # Daily 50C

        # FORD (31-36)
        31: {'pv': 115, 'pm': 290, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 10, 'co2': 50, 'classe': 'Euro 5'},    # Street 125
        32: {'pv': 170, 'pm': 360, 'permis': 'A2', 'pl': 2, 'cyl': 450, 'cv': 35, 'co2': 78, 'classe': 'Euro 5'},    # Ranger Bike
        33: {'pv': 1150, 'pm': 1650, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 95, 'co2': 115, 'classe': 'Euro 6d'},   # Fiesta
        34: {'pv': 1300, 'pm': 1850, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 120, 'co2': 125, 'classe': 'Euro 6d'}, # Focus
        35: {'pv': 2100, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 130, 'co2': 210, 'classe': 'Euro 6'}, # Transit 350
        36: {'pv': 2800, 'pm': 4700, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 170, 'co2': 245, 'classe': 'Euro 6'}, # Transit 470
    }


    # Récupération des modèles de véhicules pour le menu déroulant (Nécessaire pour GET et POST)
    query_modeles = """
        SELECT m.id, m.modele, m.type_vehicule, ma.nom as marque_nom
        FROM modeles m
        JOIN marques ma ON m.marque_id = ma.id
        ORDER BY ma.nom, m.modele
    """
    modeles = db.fetch_all(query_modeles)

    prefilled_data = None
    form_data = request.form

    if request.method == 'POST':
        # --- CAS 1 : Clic sur 'Charger modèle' pour auto-remplir
        if 'btn_load' in request.form and 'modele_id' in request.form:
            modele_id = request.form.get('modele_id')
            if modele_id and int(modele_id) in DONNEES_TECHNIQUES_REF:
                ref = DONNEES_TECHNIQUES_REF[int(modele_id)]
                # Map reference keys to template field names
                prefilled_data = {
                    'poids_vide': ref.get('pv'),
                    'poids_max': ref.get('pm'),
                    'categorie_permis': ref.get('permis'),
                    'places_assises': ref.get('pl'),
                    'cylindree': ref.get('cyl'),
                    'puissance_chevaux': ref.get('cv'),
                    'emission_co2': ref.get('co2'),
                    'classe_environnementale': ref.get('classe')
                }

            # Réaffichage du formulaire avec les données pré-remplies
            return render_template('add.html', modeles=modeles, form_data=form_data, prefilled=prefilled_data, selected_modele_id=modele_id)

        # --- CAS 2 : Enregistrement de la nouvelle carte (clic sur 'Créer la Carte Grise') ---
        if 'btn_save' in request.form:
        
            try:
                # Récupération des données du formulaire
                nom = str(escape(request.form.get('nom', '').strip()))
                prenom = str(escape(request.form.get('prenom', '').strip()))
                adresse = str(escape(request.form.get('adresse', '').strip()))
                modele_id = request.form.get('modele_id')
                date_premiere_immat = request.form.get('date_premiere_immat')
                poids_vide = request.form.get('poids_vide')
                poids_max = request.form.get('poids_max')
                categorie_permis = request.form.get('categorie_permis')
                cylindree = request.form.get('cylindree')
                puissance_chevaux = request.form.get('puissance_chevaux')
                places_assises = request.form.get('places_assises')
                emission_co2 = request.form.get('emission_co2')
                classe_env = str(escape(request.form.get('classe_environnementale', '').strip()))

                # Validation des champs obligatoires
                if not all([nom, prenom, adresse, modele_id, date_premiere_immat]):
                    flash('Les champs nom, prénom, adresse, modèle et date sont obligatoires!', 'error')
                    return redirect(url_for('add_carte_grise'))
            
                # Vérification ou création du propriétaire
                query_prop = "SELECT id FROM proprietaires WHERE nom=%s AND prenom=%s AND adresse=%s"
                proprietaire = db.fetch_one(query_prop, (nom, prenom, adresse))
                
                if not proprietaire:
                    insert_prop = "INSERT INTO proprietaires (nom, prenom, adresse) VALUES (%s, %s, %s)"
                    proprietaire_id = db.execute_query(insert_prop, (nom, prenom, adresse))
                else:
                    proprietaire_id = proprietaire['id']
                
                # Génération du prochain numéro de carte grise
                last_carte = db.fetch_one("SELECT numero_carte_grise FROM cartes_grises ORDER BY id DESC LIMIT 1")
                if last_carte and last_carte.get('numero_carte_grise'):
                    numero_carte = generer_prochain_numero_carte_grise(last_carte['numero_carte_grise'])
                else:
                    numero_carte = generer_prochain_numero_carte_grise(None)
                
                # Génération du prochain numéro de plaque d'immatriculation
                last_plaque = db.fetch_one("SELECT numero_immatriculation FROM cartes_grises ORDER BY id DESC LIMIT 1")
                if last_plaque and last_plaque.get('numero_immatriculation'):
                    numero_plaque = generer_prochain_numero_plaque(last_plaque['numero_immatriculation'])
                else:
                    numero_plaque = "AA100AA"
                
                # Vérification de l'unicité de la plaque - génération d'une nouvelle si doublon
                max_attempts = 10  # Trouve généralement une plaque unique rapidement
                attempts = 0
                
                while numero_plaque:
                    # Vérification si cette plaque existe déjà
                    existing = db.fetch_one("SELECT id FROM cartes_grises WHERE numero_immatriculation=%s", (numero_plaque,))
                    if not existing:  # Plaque unique trouvée
                        break
                    
                    # Essai du prochain numéro de plaque
                    numero_plaque = generer_prochain_numero_plaque(numero_plaque)
                    attempts += 1
                    
                    if attempts >= max_attempts or numero_plaque is None:
                        flash('Erreur: Impossible de générer un numéro de plaque unique!', 'error')
                        return redirect(url_for('add_carte_grise'))
                
                if not numero_plaque:
                    flash('Erreur: Impossible de générer un numéro de plaque valide!', 'error')
                    return redirect(url_for('add_carte_grise'))
                
                # Génération du numéro de série du véhicule
                modele_info = db.fetch_one("""
                    SELECT m.*, ma.numero_fabricant 
                    FROM modeles m 
                    JOIN marques ma ON m.marque_id = ma.id 
                    WHERE m.id = %s
                """, (modele_id,))
                
                if not modele_info:
                    flash('Modèle de véhicule introuvable!', 'error')
                    return redirect(url_for('add_carte_grise'))
                
                date_obj = datetime.strptime(date_premiere_immat, '%Y-%m-%d')
                # Récupération du nombre de véhicules immatriculés pour ce mois
                count_query = """
                    SELECT COUNT(*) as count FROM cartes_grises 
                    WHERE numero_serie LIKE %s
                """
                pattern = f"{modele_info['numero_fabricant']}{date_obj.year}M{date_obj.month:02d}%"
                count_result = db.fetch_one(count_query, (pattern,))
                numero_vehicule = (count_result['count'] + 1) if count_result and count_result.get('count') is not None else 1
                
                numero_serie = generer_numero_serie(
                    modele_info['numero_fabricant'],
                    date_obj.year,
                    date_obj.month,
                    numero_vehicule
                )
                
                # Insertion de la nouvelle carte grise en base de données
                insert_carte = """
                    INSERT INTO cartes_grises (
                        numero_carte_grise, numero_immatriculation, date_premiere_immat,
                        proprietaire_id, est_conducteur, modele_id, numero_serie,
                        poids_vide_kg, poids_max_kg, date_immat_actuelle, categorie_permis,
                        cylindree_cm3, puissance_chevaux, places_assises, emission_co2_g_km,
                        classe_environnementale
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    numero_carte, numero_plaque, date_premiere_immat,
                    proprietaire_id, True, modele_id, numero_serie,
                    poids_vide, poids_max, date_premiere_immat, categorie_permis,
                    cylindree if cylindree else None,
                    puissance_chevaux if puissance_chevaux else None,
                    places_assises if places_assises else None,
                    emission_co2 if emission_co2 else None,
                    classe_env if classe_env else None
                )
                
                if db.execute_query(insert_carte, params):
                    flash(f'Carte grise créée avec succès! Numéro: {numero_carte}, Plaque: {formater_numero_plaque(numero_plaque)}', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Erreur lors de la création de la carte grise!', 'error')
        
            except Exception as e:
                flash(f'Erreur: {str(e)}', 'error')
    
    # Récupération des modèles pour le menu déroulant
    modeles = db.fetch_all("""
        SELECT m.id, m.modele, m.type_vehicule, ma.nom as marque_nom, c.nom as categorie_nom
        FROM modeles m
        JOIN marques ma ON m.marque_id = ma.id
        JOIN categories_vehicule c ON m.categorie_id = c.id
        ORDER BY ma.nom, m.modele
    """)
    
    return render_template('add.html', modeles=modeles)

@app.route('/edit/<int:carte_id>', methods=['GET', 'POST'])
def edit_carte_grise(carte_id):
    """Modification d'une carte grise existante"""
    
    # Données techniques de référence (same as add route)
    DONNEES_TECHNIQUES_REF = {
        # Honda
        1: {'pv': 190, 'pm': 370, 'permis': 'A2', 'pl': 2, 'cyl': 471, 'cv': 48, 'co2': 80, 'classe': 'Euro 5'},
        2: {'pv': 201, 'pm': 390, 'permis': 'A', 'pl': 2, 'cyl': 999, 'cv': 217, 'co2': 160, 'classe': 'Euro 4'},
        3: {'pv': 1300, 'pm': 1800, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 182, 'co2': 128, 'classe': 'Euro 6d'},
        4: {'pv': 1600, 'pm': 2200, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 184, 'co2': 153, 'classe': 'Euro 6d'},
        5: {'pv': 2800, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2999, 'cv': 150, 'co2': 210, 'classe': 'Euro 6'},
        6: {'pv': 2600, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 130, 'co2': 220, 'classe': 'Euro 6'},
        7: {'pv': 95, 'pm': 270, 'permis': 'A1', 'pl': 2, 'cyl': 49, 'cv': 4, 'co2': 45, 'classe': 'Euro 5'},
        8: {'pv': 280, 'pm': 450, 'permis': 'A', 'pl': 2, 'cyl': 399, 'cv': 36, 'co2': 89, 'classe': 'Euro 5'},
        9: {'pv': 1050, 'pm': 1550, 'permis': 'B', 'pl': 5, 'cyl': 1199, 'cv': 100, 'co2': 102, 'classe': 'Euro 6d'},
        10: {'pv': 1500, 'pm': 2100, 'permis': 'B', 'pl': 7, 'cyl': 1598, 'cv': 180, 'co2': 140, 'classe': 'Euro 6d'},
        11: {'pv': 2100, 'pm': 4400, 'permis': 'C', 'pl': 3, 'cyl': 2179, 'cv': 140, 'co2': 230, 'classe': 'Euro 6'},
        12: {'pv': 1800, 'pm': 3100, 'permis': 'C', 'pl': 3, 'cyl': 1997, 'cv': 145, 'co2': 190, 'classe': 'Euro 6'},
        13: {'pv': 120, 'pm': 300, 'permis': 'A1', 'pl': 2, 'cyl': 124, 'cv': 11, 'co2': 55, 'classe': 'Euro 5'},
        14: {'pv': 160, 'pm': 340, 'permis': 'A2', 'pl': 2, 'cyl': 395, 'cv': 30, 'co2': 75, 'classe': 'Euro 5'},
        15: {'pv': 1100, 'pm': 1600, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 90, 'co2': 110, 'classe': 'Euro 6d'},
        16: {'pv': 1400, 'pm': 1950, 'permis': 'B', 'pl': 5, 'cyl': 1332, 'cv': 140, 'co2': 130, 'classe': 'Euro 6d'},
        17: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2299, 'cv': 135, 'co2': 240, 'classe': 'Euro 6'},
        18: {'pv': 2400, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 140, 'co2': 250, 'classe': 'Euro 6'},
        19: {'pv': 130, 'pm': 310, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 12, 'co2': 60, 'classe': 'Euro 5'},
        20: {'pv': 210, 'pm': 400, 'permis': 'A', 'pl': 2, 'cyl': 998, 'cv': 200, 'co2': 155, 'classe': 'Euro 4'},
        21: {'pv': 1350, 'pm': 1900, 'permis': 'B', 'pl': 5, 'cyl': 1461, 'cv': 116, 'co2': 120, 'classe': 'Euro 6d'},
        22: {'pv': 1800, 'pm': 2400, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 190, 'co2': 160, 'classe': 'Euro 6d'},
        23: {'pv': 2600, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2143, 'cv': 163, 'co2': 215, 'classe': 'Euro 6'},
        24: {'pv': 2900, 'pm': 4800, 'permis': 'C', 'pl': 3, 'cyl': 4250, 'cv': 170, 'co2': 230, 'classe': 'Euro 6'},
        25: {'pv': 150, 'pm': 330, 'permis': 'A2', 'pl': 2, 'cyl': 300, 'cv': 28, 'co2': 70, 'classe': 'Euro 5'},
        26: {'pv': 220, 'pm': 420, 'permis': 'A', 'pl': 2, 'cyl': 1100, 'cv': 210, 'co2': 165, 'classe': 'Euro 4'},
        27: {'pv': 2000, 'pm': 2800, 'permis': 'B', 'pl': 5, 'cyl': 2998, 'cv': 176, 'co2': 200, 'classe': 'Euro 6'},
        28: {'pv': 1900, 'pm': 2600, 'permis': 'B', 'pl': 5, 'cyl': 2500, 'cv': 150, 'co2': 190, 'classe': 'Euro 6'},
        29: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2300, 'cv': 140, 'co2': 225, 'classe': 'Euro 6'},
        30: {'pv': 2500, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2998, 'cv': 180, 'co2': 245, 'classe': 'Euro 6'},
        31: {'pv': 115, 'pm': 290, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 10, 'co2': 50, 'classe': 'Euro 5'},
        32: {'pv': 170, 'pm': 360, 'permis': 'A2', 'pl': 2, 'cyl': 450, 'cv': 35, 'co2': 78, 'classe': 'Euro 5'},
        33: {'pv': 1150, 'pm': 1650, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 95, 'co2': 115, 'classe': 'Euro 6d'},
        34: {'pv': 1300, 'pm': 1850, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 120, 'co2': 125, 'classe': 'Euro 6d'},
        35: {'pv': 2100, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 130, 'co2': 210, 'classe': 'Euro 6'},
        36: {'pv': 2800, 'pm': 4700, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 170, 'co2': 245, 'classe': 'Euro 6'},
    }
    
    # Récupération des modèles
    query_modeles = """
        SELECT m.id, m.modele, m.type_vehicule, ma.nom as marque_nom
        FROM modeles m
        JOIN marques ma ON m.marque_id = ma.id
        ORDER BY ma.nom, m.modele
    """
    modeles = db.fetch_all(query_modeles)
    
    prefilled_data = None
    selected_modele_id = None
    
    if request.method == 'POST':
        # --- CAS 1 : Clic sur 'Charger modèle' pour auto-remplir
        if 'btn_load' in request.form and 'modele_id' in request.form:
            modele_id = request.form.get('modele_id')
            if modele_id and int(modele_id) in DONNEES_TECHNIQUES_REF:
                ref = DONNEES_TECHNIQUES_REF[int(modele_id)]
                prefilled_data = {
                    'poids_vide': ref.get('pv'),
                    'poids_max': ref.get('pm'),
                    'categorie_permis': ref.get('permis'),
                    'places_assises': ref.get('pl'),
                    'cylindree': ref.get('cyl'),
                    'puissance_chevaux': ref.get('cv'),
                    'emission_co2': ref.get('co2'),
                    'classe_environnementale': ref.get('classe')
                }
                selected_modele_id = modele_id
            
            # Récupération des données de la carte grise pour l'affichage
            carte = db.fetch_one("""
                SELECT cg.*, 
                       p.nom, p.prenom, p.adresse,
                       mo.modele, mo.type_vehicule,
                       ma.nom as marque_nom
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE cg.id = %s
            """, (carte_id,))
            
            return render_template('edit.html', carte=carte, modeles=modeles, prefilled=prefilled_data, selected_modele_id=selected_modele_id)
        
        # --- CAS 2 : Enregistrement des modifications
        try:
            # Récupération des données du formulaire
            nom = str(escape(request.form.get('nom', '').strip()))
            prenom = str(escape(request.form.get('prenom', '').strip()))
            adresse = str(escape(request.form.get('adresse', '').strip()))
            modele_id = request.form.get('modele_id')
            date_premiere_immat = request.form.get('date_premiere_immat')
            categorie_permis = request.form.get('categorie_permis')
            poids_vide = request.form.get('poids_vide')
            poids_max = request.form.get('poids_max')
            places_assises = request.form.get('places_assises')
            cylindree = request.form.get('cylindree')
            puissance_chevaux = request.form.get('puissance_chevaux')
            emission_co2 = request.form.get('emission_co2')
            classe_env = str(escape(request.form.get('classe_environnementale', '').strip()))
            
            # Validation des champs obligatoires
            if not all([nom, prenom, adresse, modele_id, date_premiere_immat, categorie_permis]):
                flash('Les champs nom, prénom, adresse, modèle, date et catégorie de permis sont obligatoires!', 'error')
                return redirect(url_for('edit_carte_grise', carte_id=carte_id))
            
            # Vérification ou création du propriétaire
            query_prop = "SELECT id FROM proprietaires WHERE nom=%s AND prenom=%s AND adresse=%s"
            proprietaire = db.fetch_one(query_prop, (nom, prenom, adresse))
            
            if not proprietaire:
                insert_prop = "INSERT INTO proprietaires (nom, prenom, adresse) VALUES (%s, %s, %s)"
                proprietaire_id = db.execute_query(insert_prop, (nom, prenom, adresse))
            else:
                proprietaire_id = proprietaire['id']
            
            # Mise à jour de la carte grise
            update_query = """
                UPDATE cartes_grises 
                SET proprietaire_id=%s, modele_id=%s, date_premiere_immat=%s, categorie_permis=%s,
                    poids_vide_kg=%s, poids_max_kg=%s, places_assises=%s,
                    cylindree_cm3=%s, puissance_chevaux=%s, emission_co2_g_km=%s,
                    classe_environnementale=%s
                WHERE id=%s
            """
            params = (
                proprietaire_id, modele_id, date_premiere_immat, categorie_permis,
                poids_vide, poids_max,
                places_assises if places_assises else None,
                cylindree if cylindree else None,
                puissance_chevaux if puissance_chevaux else None,
                emission_co2 if emission_co2 else None,
                classe_env if classe_env else None,
                carte_id
            )
            
            if db.execute_query(update_query, params):
                flash('Carte grise mise à jour avec succès!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Erreur lors de la mise à jour!', 'error')
        
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    # Récupération des données de la carte grise
    carte = db.fetch_one("""
        SELECT cg.*, 
               p.nom, p.prenom, p.adresse,
               mo.modele, mo.type_vehicule,
               ma.nom as marque_nom
        FROM cartes_grises cg
        JOIN proprietaires p ON cg.proprietaire_id = p.id
        JOIN modeles mo ON cg.modele_id = mo.id
        JOIN marques ma ON mo.marque_id = ma.id
        WHERE cg.id = %s
    """, (carte_id,))
    
    if not carte:
        flash('Carte grise introuvable!', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit.html', carte=carte, modeles=modeles, prefilled=prefilled_data, selected_modele_id=selected_modele_id)

@app.route('/delete/<int:carte_id>', methods=['POST'])
def delete_carte_grise(carte_id):
    """Suppression d'une carte grise"""
    query = "DELETE FROM cartes_grises WHERE id=%s"
    
    if db.execute_query(query, (carte_id,)):
        flash('Carte grise supprimée avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression!', 'error')
    
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Recherche et filtrage des cartes grises"""
    cartes = []
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        search_value = request.form.get('search_value', '').strip()
        
        # Recherche par nom du propriétaire
        if search_type == 'nom':
            query = """
                SELECT cg.*, p.nom, p.prenom, mo.modele, ma.nom as marque_nom
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE p.nom LIKE %s
                ORDER BY p.nom, p.prenom
            """
            cartes = db.fetch_all(query, (f'%{search_value}%',))
        
        # Recherche par numéro de plaque
        elif search_type == 'plaque':
            valeur_nettoyee = search_value.replace(' ', '').replace('-', '').strip().upper()

            query = """
                SELECT cg.*, p.nom, p.prenom, mo.modele, ma.nom as marque_nom
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE cg.numero_immatriculation LIKE %s
                OR
                REPLACE(cg.numero_immatriculation, '-', '') LIKE %s
                ORDER BY cg.numero_immatriculation
            """
            param = f'%{valeur_nettoyee}%'
            cartes = db.fetch_all(query, (param, param))
        
        # Recherche par marque - (Ordre décroissant)
        elif search_type == 'marque':
            query = """
                SELECT ma.nom as marque_nom, COUNT(*) as count
                FROM cartes_grises cg
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                GROUP BY ma.nom
                ORDER BY count DESC
            """
            cartes = db.fetch_all(query)

        # Lister le nombre de véhicules > X années avec pollution > Y
        elif search_type == 'critere_complexe':
            age_min = 5
            co2_min = 120

            if ',' in search_value:
                try:
                    parts = search_value.split(',')
                    age_min = int(parts[0].strip())
                    co2_min = int(parts[1].strip())
                except:
                    pass # On garde les valeurs par défaut si l'utilisateur écrit n'importe quoi

            query = """
                SELECT cg.*, p.nom, p.prenom, mo.modele, ma.nom as marque_nom,
                       (YEAR(CURRENT_DATE) - YEAR(cg.date_premiere_immat)) as age_vehicule
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE (YEAR(CURRENT_DATE) - YEAR(cg.date_premiere_immat)) > %s
                  AND cg.emission_co2_g_km > %s
                ORDER BY cg.emission_co2_g_km DESC
            """
            cartes = db.fetch_all(query, (age_min, co2_min))
    
    return render_template('search.html', cartes=cartes)

# Point d'entrée de l'application
if __name__ == '__main__':
    # Configuration de mode debug, hôte et port depuis les variables d'environnement
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    # Lancement du serveur Flask
    app.run(debug=debug_mode, host=host, port=port)
