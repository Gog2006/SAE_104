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
    generer_numero_serie,
    generer_numero_carte_grise_depuis_db,
    generer_numero_plaque_unique_depuis_db,
    generer_numero_serie_depuis_db
)
import os
from datetime import datetime

# Création de l'application Flask
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
            # 'flash' envoie un message temporaire à l'utilisateur (visible au prochain chargement de page)
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
    # Requête avec jointures (JOIN) pour récupérer les infos liées :
    # - Le propriétaire (via proprietaires p)
    # - Le modèle du véhicule (via modeles mo)
    # - La marque (via marques ma)
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
        1: {'pv': 190, 'pm': 370, 'permis': 'A2', 'pl': 2, 'cyl': 471, 'cv': 48, 'co2': 80, 'classe': 'Euro 5', 'cv_admin': 6, 'pl_debout': 0, 'db': 95, 'rpm': 8500, 'carburant': 'Essence'},   # CB500F
        2: {'pv': 201, 'pm': 390, 'permis': 'A', 'pl': 2, 'cyl': 999, 'cv': 217, 'co2': 160, 'classe': 'Euro 4', 'cv_admin': 15, 'pl_debout': 0, 'db': 105, 'rpm': 13000, 'carburant': 'Essence'},  # CBR1000RR
        3: {'pv': 1300, 'pm': 1800, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 182, 'co2': 128, 'classe': 'Euro 6d', 'cv_admin': 9, 'pl_debout': 0, 'db': 72, 'rpm': 6500, 'carburant': 'Essence'}, # Civic
        4: {'pv': 1600, 'pm': 2200, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 184, 'co2': 153, 'classe': 'Euro 6d', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 6000, 'carburant': 'Hybride'}, # CR-V
        5: {'pv': 2800, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2999, 'cv': 150, 'co2': 210, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4500, 'carburant': 'Diesel'}, # NT400
        6: {'pv': 2600, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 130, 'co2': 220, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 76, 'rpm': 4200, 'carburant': 'Diesel'}, # Cabstar
        # Peugeot
        7: {'pv': 95, 'pm': 270, 'permis': 'A1', 'pl': 2, 'cyl': 49, 'cv': 4, 'co2': 45, 'classe': 'Euro 5', 'cv_admin': 1, 'pl_debout': 0, 'db': 82, 'rpm': 8000, 'carburant': 'Essence'},     # Kisbee
        8: {'pv': 280, 'pm': 450, 'permis': 'A', 'pl': 2, 'cyl': 399, 'cv': 36, 'co2': 89, 'classe': 'Euro 5', 'cv_admin': 5, 'pl_debout': 0, 'db': 88, 'rpm': 7500, 'carburant': 'Essence'},    # Metropolis
        9: {'pv': 1050, 'pm': 1550, 'permis': 'B', 'pl': 5, 'cyl': 1199, 'cv': 100, 'co2': 102, 'classe': 'Euro 6d', 'cv_admin': 7, 'pl_debout': 0, 'db': 70, 'rpm': 6200, 'carburant': 'Essence'}, # 208
        10: {'pv': 1500, 'pm': 2100, 'permis': 'B', 'pl': 7, 'cyl': 1598, 'cv': 180, 'co2': 140, 'classe': 'Euro 6d', 'cv_admin': 9, 'pl_debout': 0, 'db': 73, 'rpm': 6000, 'carburant': 'Diesel'},# 5008
        11: {'pv': 2100, 'pm': 4400, 'permis': 'C', 'pl': 3, 'cyl': 2179, 'cv': 140, 'co2': 230, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 77, 'rpm': 4000, 'carburant': 'Diesel'},# Boxer
        12: {'pv': 1800, 'pm': 3100, 'permis': 'C', 'pl': 3, 'cyl': 1997, 'cv': 145, 'co2': 190, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 4500, 'carburant': 'Diesel'},# Expert
       
       # RENAULT (IDs 13 à 18)
        13: {'pv': 120, 'pm': 300, 'permis': 'A1', 'pl': 2, 'cyl': 124, 'cv': 11, 'co2': 55, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 85, 'rpm': 9000, 'couleur': 'Rouge', 'carburant': 'Essence'},     # Full 125
        14: {'pv': 160, 'pm': 340, 'permis': 'A2', 'pl': 2, 'cyl': 395, 'cv': 30, 'co2': 75, 'classe': 'Euro 5', 'cv_admin': 4, 'pl_debout': 0, 'db': 90, 'rpm': 8000, 'couleur': 'Jaune', 'carburant': 'Essence'},     # Sport 400
        15: {'pv': 1100, 'pm': 1600, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 90, 'co2': 110, 'classe': 'Euro 6d', 'cv_admin': 6, 'pl_debout': 0, 'db': 69, 'rpm': 6500, 'couleur': 'Gris', 'carburant': 'Essence'},   # Clio
        16: {'pv': 1400, 'pm': 1950, 'permis': 'B', 'pl': 5, 'cyl': 1332, 'cv': 140, 'co2': 130, 'classe': 'Euro 6d', 'cv_admin': 8, 'pl_debout': 0, 'db': 71, 'rpm': 6200, 'couleur': 'Bleu', 'carburant': 'Hybride'}, # Austral
        17: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2299, 'cv': 135, 'co2': 240, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 76, 'rpm': 4200, 'couleur': 'Jaune', 'carburant': 'Diesel'}, # Master
        18: {'pv': 2400, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 140, 'co2': 250, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4000, 'couleur': 'Blanc', 'carburant': 'Diesel'}, # Maxity

       # MERCEDES (19-24)
        19: {'pv': 130, 'pm': 310, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 12, 'co2': 60, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 83, 'rpm': 9500, 'couleur': 'Argent', 'carburant': 'Essence'},   # Citan Scooter
        20: {'pv': 210, 'pm': 400, 'permis': 'A', 'pl': 2, 'cyl': 998, 'cv': 200, 'co2': 155, 'classe': 'Euro 4', 'cv_admin': 14, 'pl_debout': 0, 'db': 102, 'rpm': 12500, 'couleur': 'Noir', 'carburant': 'Essence'},  # Vision GT
        21: {'pv': 1350, 'pm': 1900, 'permis': 'B', 'pl': 5, 'cyl': 1461, 'cv': 116, 'co2': 120, 'classe': 'Euro 6d', 'cv_admin': 7, 'pl_debout': 0, 'db': 68, 'rpm': 6800, 'couleur': 'Noir', 'carburant': 'Essence'}, # Classe A
        22: {'pv': 1800, 'pm': 2400, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 190, 'co2': 160, 'classe': 'Euro 6d', 'cv_admin': 10, 'pl_debout': 0, 'db': 74, 'rpm': 6200, 'couleur': 'Argent', 'carburant': 'Diesel'}, # GLC
        23: {'pv': 2600, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2143, 'cv': 163, 'co2': 215, 'classe': 'Euro 6', 'cv_admin': 13, 'pl_debout': 0, 'db': 79, 'rpm': 4500, 'couleur': 'Argent', 'carburant': 'Diesel'}, # Sprinter 5t
        24: {'pv': 2900, 'pm': 4800, 'permis': 'C', 'pl': 3, 'cyl': 4250, 'cv': 170, 'co2': 230, 'classe': 'Euro 6', 'cv_admin': 14, 'pl_debout': 0, 'db': 81, 'rpm': 3800, 'couleur': 'Blanc', 'carburant': 'Diesel'}, # Vario

        # IVECO (25-30)
        25: {'pv': 150, 'pm': 330, 'permis': 'A2', 'pl': 2, 'cyl': 300, 'cv': 28, 'co2': 70, 'classe': 'Euro 5', 'cv_admin': 3, 'pl_debout': 0, 'db': 87, 'rpm': 8500, 'couleur': 'Orange', 'carburant': 'Essence'},    # Daily Moto
        26: {'pv': 220, 'pm': 420, 'permis': 'A', 'pl': 2, 'cyl': 1100, 'cv': 210, 'co2': 165, 'classe': 'Euro 4', 'cv_admin': 15, 'pl_debout': 0, 'db': 106, 'rpm': 12000, 'couleur': 'Orange', 'carburant': 'Essence'},   # Turbo Bike
        27: {'pv': 2000, 'pm': 2800, 'permis': 'B', 'pl': 5, 'cyl': 2998, 'cv': 176, 'co2': 200, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 76, 'rpm': 5500, 'couleur': 'Vert', 'carburant': 'Diesel'}, # Massif
        28: {'pv': 1900, 'pm': 2600, 'permis': 'B', 'pl': 5, 'cyl': 2500, 'cv': 150, 'co2': 190, 'classe': 'Euro 6', 'cv_admin': 9, 'pl_debout': 0, 'db': 74, 'rpm': 5800, 'couleur': 'Bleu', 'carburant': 'Diesel'}, # Campagnola
        29: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2300, 'cv': 140, 'co2': 225, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 77, 'rpm': 4300, 'couleur': 'Blanc', 'carburant': 'Diesel'}, # Daily 35C
        30: {'pv': 2500, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2998, 'cv': 180, 'co2': 245, 'classe': 'Euro 6', 'cv_admin': 13, 'pl_debout': 0, 'db': 80, 'rpm': 4000, 'couleur': 'Rouge', 'carburant': 'Diesel'}, # Daily 50C

        # FORD (31-36)
        31: {'pv': 115, 'pm': 290, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 10, 'co2': 50, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 84, 'rpm': 9200, 'couleur': 'Bleu', 'carburant': 'Essence'},    # Street 125
        32: {'pv': 170, 'pm': 360, 'permis': 'A2', 'pl': 2, 'cyl': 450, 'cv': 35, 'co2': 78, 'classe': 'Euro 5', 'cv_admin': 4, 'pl_debout': 0, 'db': 89, 'rpm': 8200, 'couleur': 'Vert', 'carburant': 'Essence'},    # Ranger Bike
        33: {'pv': 1150, 'pm': 1650, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 95, 'co2': 115, 'classe': 'Euro 6d', 'cv_admin': 6, 'pl_debout': 0, 'db': 70, 'rpm': 6400, 'couleur': 'Vert', 'carburant': 'Essence'},   # Fiesta
        34: {'pv': 1300, 'pm': 1850, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 120, 'co2': 125, 'classe': 'Euro 6d', 'cv_admin': 8, 'pl_debout': 0, 'db': 72, 'rpm': 6300, 'couleur': 'Gris', 'carburant': 'Essence'}, # Focus
        35: {'pv': 2100, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 130, 'co2': 210, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 4600, 'couleur': 'Blanc', 'carburant': 'Diesel'}, # Transit 350
        36: {'pv': 2800, 'pm': 4700, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 170, 'co2': 245, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4400, 'couleur': 'Bleu', 'carburant': 'Diesel'}, # Transit 470
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
        # CAS 1 : L'utilisateur a cliqué sur "Charger les données du modèle"
        # On ne sauvegarde rien, on recharge juste la page avec les champs pré-remplis.
        if 'btn_load' in request.form and 'modele_id' in request.form:
            modele_id = request.form.get('modele_id')
            if modele_id and int(modele_id) in DONNEES_TECHNIQUES_REF:
                ref = DONNEES_TECHNIQUES_REF[int(modele_id)]
                # Mapping des données de référence vers les noms des champs du formulaire
                prefilled_data = {
                    'poids_vide': ref.get('pv'),
                    'poids_max': ref.get('pm'),
                    'categorie_permis': ref.get('permis'),
                    'carburant_energie': ref.get('carburant'),
                    'places_assises': ref.get('pl'),
                    'cylindree': ref.get('cyl'),
                    'puissance_chevaux': ref.get('cv'),
                    'emission_co2': ref.get('co2'),
                    'classe_environnementale': ref.get('classe'),
                    'puissance_administrative_cv': ref.get('cv_admin'),
                    'places_debout': ref.get('pl_debout'),
                    'niveau_sonore_db': ref.get('db'),
                    'vitesse_max_moteur_rpm': ref.get('rpm'),
                    'couleur_principale': ref.get('couleur')
                }

            # Réaffichage du formulaire avec les données pré-remplies
            return render_template('add.html', modeles=modeles, form_data=form_data, prefilled=prefilled_data, selected_modele_id=modele_id)

        # --- CAS 2 : Enregistrement de la nouvelle carte (clic sur 'Créer la Carte Grise') ---
        if 'btn_save' in request.form:
        
            try:
               # 1. Nettoyage des données (Sécurité)
                # On utilise escape() et strip() pour éviter les espaces vides et le code malveillant
                nom = str(escape(request.form.get('nom', '').strip()))
                prenom = str(escape(request.form.get('prenom', '').strip()))
                adresse = str(escape(request.form.get('adresse', '').strip()))
                modele_id = request.form.get('modele_id')
                date_premiere_immat = request.form.get('date_premiere_immat')
                numero_serie = str(escape(request.form.get('numero_serie', '').strip()))
                poids_vide = request.form.get('poids_vide')
                poids_max = request.form.get('poids_max')
                categorie_permis = request.form.get('categorie_permis')
                carburant_energie = str(escape(request.form.get('carburant_energie', '').strip()))
                cylindree = request.form.get('cylindree')
                puissance_chevaux = request.form.get('puissance_chevaux')
                puissance_administrative_cv = request.form.get('puissance_administrative_cv')
                places_assises = request.form.get('places_assises')
                places_debout = request.form.get('places_debout')
                emission_co2 = request.form.get('emission_co2')
                classe_env = str(escape(request.form.get('classe_environnementale', '').strip()))
                niveau_sonore_db = request.form.get('niveau_sonore_db')
                vitesse_max_moteur_rpm = request.form.get('vitesse_max_moteur_rpm')
                date_fin_validite = request.form.get('date_fin_validite')
                date_premier_controle = request.form.get('date_premier_controle')
                date_controle_2 = request.form.get('date_controle_2')
                date_controle_3 = request.form.get('date_controle_3')
                couleur_principale = str(escape(request.form.get('couleur_principale', '').strip()))

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

                # Génération des numéros
                
                # Génération du prochain numéro de carte grise
                numero_carte = generer_numero_carte_grise_depuis_db(db)
                
                # Génération du prochain numéro de plaque d'immatriculation
                numero_plaque = generer_numero_plaque_unique_depuis_db(db)
                
                if not numero_plaque:
                    flash('Erreur: Impossible de générer un numéro de plaque unique!', 'error')
                    return redirect(url_for('add_carte_grise'))
                
                # Génération du numéro de série du véhicule
                # On récupère le code fabricant du modèle choisi
                modele_info = db.fetch_one("""
                    SELECT m.*, ma.numero_fabricant 
                    FROM modeles m 
                    JOIN marques ma ON m.marque_id = ma.id 
                    WHERE m.id = %s
                """, (modele_id,))
                
                if not modele_info:
                    flash('Modèle de véhicule introuvable!', 'error')
                    return redirect(url_for('add_carte_grise'))
                
                # Génération du numéro de série (VIN) si pas fourni par l'utilisateur
                if numero_serie.strip():
                    # Utiliser le VIN fourni par l'utilisateur
                    # Vérifier qu'il n'existe pas déjà
                    existing_vin = db.fetch_one("SELECT id FROM cartes_grises WHERE numero_serie=%s", (numero_serie,))
                    if existing_vin:
                        flash('Ce numéro VIN existe déjà dans la base de données!', 'error')
                        return redirect(url_for('add_carte_grise'))
                else:
                    # Générer automatiquement le VIN
                    numero_serie = generer_numero_serie_depuis_db(db, modele_info['numero_fabricant'], date_premiere_immat)
                
                # Insertion de la nouvelle carte grise en base de données
                insert_carte = """
                    INSERT INTO cartes_grises (
                        numero_carte_grise, numero_immatriculation, date_premiere_immat,
                        proprietaire_id, est_conducteur, modele_id, numero_serie,
                        poids_vide_kg, poids_max_kg, date_immat_actuelle, categorie_permis,
                        carburant_energie, cylindree_cm3, puissance_chevaux, puissance_administrative_cv,
                        places_assises, places_debout, emission_co2_g_km,
                        classe_environnementale, niveau_sonore_db, vitesse_max_moteur_rpm,
                        couleur_principale, date_fin_validite, date_premier_controle, 
                        date_controle_2, date_controle_3
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    numero_carte, numero_plaque, date_premiere_immat,
                    proprietaire_id, True, modele_id, numero_serie,
                    poids_vide, poids_max, date_premiere_immat, categorie_permis,
                    carburant_energie if carburant_energie else None,
                    cylindree if cylindree else None,
                    puissance_chevaux if puissance_chevaux else None,
                    puissance_administrative_cv if puissance_administrative_cv else None,
                    places_assises if places_assises else None,
                    places_debout if places_debout else None,
                    emission_co2 if emission_co2 else None,
                    classe_env if classe_env else None,
                    niveau_sonore_db if niveau_sonore_db else None,
                    vitesse_max_moteur_rpm if vitesse_max_moteur_rpm else None,
                    couleur_principale if couleur_principale else None,
                    date_fin_validite if date_fin_validite else None,
                    date_premier_controle if date_premier_controle else None,
                    date_controle_2 if date_controle_2 else None,
                    date_controle_3 if date_controle_3 else None
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
        1: {'pv': 190, 'pm': 370, 'permis': 'A2', 'pl': 2, 'cyl': 471, 'cv': 48, 'co2': 80, 'classe': 'Euro 5', 'cv_admin': 6, 'pl_debout': 0, 'db': 95, 'rpm': 8500, 'couleur': 'Rouge'},
        2: {'pv': 201, 'pm': 390, 'permis': 'A', 'pl': 2, 'cyl': 999, 'cv': 217, 'co2': 160, 'classe': 'Euro 4', 'cv_admin': 15, 'pl_debout': 0, 'db': 105, 'rpm': 13000, 'couleur': 'Noir'},
        3: {'pv': 1300, 'pm': 1800, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 182, 'co2': 128, 'classe': 'Euro 6d', 'cv_admin': 9, 'pl_debout': 0, 'db': 72, 'rpm': 6500, 'couleur': 'Blanc'},
        4: {'pv': 1600, 'pm': 2200, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 184, 'co2': 153, 'classe': 'Euro 6d', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 6000, 'couleur': 'Gris'},
        5: {'pv': 2800, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2999, 'cv': 150, 'co2': 210, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4500, 'couleur': 'Blanc'},
        6: {'pv': 2600, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 130, 'co2': 220, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 76, 'rpm': 4200, 'couleur': 'Blanc'},
        # Peugeot
        7: {'pv': 95, 'pm': 270, 'permis': 'A1', 'pl': 2, 'cyl': 49, 'cv': 4, 'co2': 45, 'classe': 'Euro 5', 'cv_admin': 1, 'pl_debout': 0, 'db': 82, 'rpm': 8000, 'couleur': 'Bleu'},
        8: {'pv': 280, 'pm': 450, 'permis': 'A', 'pl': 2, 'cyl': 399, 'cv': 36, 'co2': 89, 'classe': 'Euro 5', 'cv_admin': 5, 'pl_debout': 0, 'db': 88, 'rpm': 7500, 'couleur': 'Argent'},
        9: {'pv': 1050, 'pm': 1550, 'permis': 'B', 'pl': 5, 'cyl': 1199, 'cv': 100, 'co2': 102, 'classe': 'Euro 6d', 'cv_admin': 7, 'pl_debout': 0, 'db': 70, 'rpm': 6200, 'couleur': 'Bleu'},
        10: {'pv': 1500, 'pm': 2100, 'permis': 'B', 'pl': 7, 'cyl': 1598, 'cv': 180, 'co2': 140, 'classe': 'Euro 6d', 'cv_admin': 9, 'pl_debout': 0, 'db': 73, 'rpm': 6000, 'couleur': 'Noir'},
        11: {'pv': 2100, 'pm': 4400, 'permis': 'C', 'pl': 3, 'cyl': 2179, 'cv': 140, 'co2': 230, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 77, 'rpm': 4000, 'couleur': 'Blanc'},
        12: {'pv': 1800, 'pm': 3100, 'permis': 'C', 'pl': 3, 'cyl': 1997, 'cv': 145, 'co2': 190, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 4500, 'couleur': 'Gris'},
        # RENAULT (IDs 13 à 18)
        13: {'pv': 120, 'pm': 300, 'permis': 'A1', 'pl': 2, 'cyl': 124, 'cv': 11, 'co2': 55, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 85, 'rpm': 9000, 'couleur': 'Rouge'},
        14: {'pv': 160, 'pm': 340, 'permis': 'A2', 'pl': 2, 'cyl': 395, 'cv': 30, 'co2': 75, 'classe': 'Euro 5', 'cv_admin': 4, 'pl_debout': 0, 'db': 90, 'rpm': 8000, 'couleur': 'Jaune'},
        15: {'pv': 1100, 'pm': 1600, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 90, 'co2': 110, 'classe': 'Euro 6d', 'cv_admin': 6, 'pl_debout': 0, 'db': 69, 'rpm': 6500, 'couleur': 'Gris'},
        16: {'pv': 1400, 'pm': 1950, 'permis': 'B', 'pl': 5, 'cyl': 1332, 'cv': 140, 'co2': 130, 'classe': 'Euro 6d', 'cv_admin': 8, 'pl_debout': 0, 'db': 71, 'rpm': 6200, 'couleur': 'Bleu'},
        17: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2299, 'cv': 135, 'co2': 240, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 76, 'rpm': 4200, 'couleur': 'Jaune'},
        18: {'pv': 2400, 'pm': 4500, 'permis': 'C', 'pl': 3, 'cyl': 2488, 'cv': 140, 'co2': 250, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4000, 'couleur': 'Blanc'},
        # MERCEDES (19-24)
        19: {'pv': 130, 'pm': 310, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 12, 'co2': 60, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 83, 'rpm': 9500, 'couleur': 'Argent'},
        20: {'pv': 210, 'pm': 400, 'permis': 'A', 'pl': 2, 'cyl': 998, 'cv': 200, 'co2': 155, 'classe': 'Euro 4', 'cv_admin': 14, 'pl_debout': 0, 'db': 102, 'rpm': 12500, 'couleur': 'Noir'},
        21: {'pv': 1350, 'pm': 1900, 'permis': 'B', 'pl': 5, 'cyl': 1461, 'cv': 116, 'co2': 120, 'classe': 'Euro 6d', 'cv_admin': 7, 'pl_debout': 0, 'db': 68, 'rpm': 6800, 'couleur': 'Noir'},
        22: {'pv': 1800, 'pm': 2400, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 190, 'co2': 160, 'classe': 'Euro 6d', 'cv_admin': 10, 'pl_debout': 0, 'db': 74, 'rpm': 6200, 'couleur': 'Argent'},
        23: {'pv': 2600, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2143, 'cv': 163, 'co2': 215, 'classe': 'Euro 6', 'cv_admin': 13, 'pl_debout': 0, 'db': 79, 'rpm': 4500, 'couleur': 'Argent'},
        24: {'pv': 2900, 'pm': 4800, 'permis': 'C', 'pl': 3, 'cyl': 4250, 'cv': 170, 'co2': 230, 'classe': 'Euro 6', 'cv_admin': 14, 'pl_debout': 0, 'db': 81, 'rpm': 3800, 'couleur': 'Blanc'},
        # IVECO (25-30)
        25: {'pv': 150, 'pm': 330, 'permis': 'A2', 'pl': 2, 'cyl': 300, 'cv': 28, 'co2': 70, 'classe': 'Euro 5', 'cv_admin': 3, 'pl_debout': 0, 'db': 87, 'rpm': 8500, 'couleur': 'Orange'},
        26: {'pv': 220, 'pm': 420, 'permis': 'A', 'pl': 2, 'cyl': 1100, 'cv': 210, 'co2': 165, 'classe': 'Euro 4', 'cv_admin': 15, 'pl_debout': 0, 'db': 106, 'rpm': 12000, 'couleur': 'Orange'},
        27: {'pv': 2000, 'pm': 2800, 'permis': 'B', 'pl': 5, 'cyl': 2998, 'cv': 176, 'co2': 200, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 76, 'rpm': 5500, 'couleur': 'Vert'},
        28: {'pv': 1900, 'pm': 2600, 'permis': 'B', 'pl': 5, 'cyl': 2500, 'cv': 150, 'co2': 190, 'classe': 'Euro 6', 'cv_admin': 9, 'pl_debout': 0, 'db': 74, 'rpm': 5800, 'couleur': 'Bleu'},
        29: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2300, 'cv': 140, 'co2': 225, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 77, 'rpm': 4300, 'couleur': 'Blanc'},
        30: {'pv': 2500, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2998, 'cv': 180, 'co2': 245, 'classe': 'Euro 6', 'cv_admin': 13, 'pl_debout': 0, 'db': 80, 'rpm': 4000, 'couleur': 'Rouge'},
        # FORD (31-36)
        31: {'pv': 115, 'pm': 290, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 10, 'co2': 50, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 84, 'rpm': 9200, 'couleur': 'Bleu'},
        32: {'pv': 170, 'pm': 360, 'permis': 'A2', 'pl': 2, 'cyl': 450, 'cv': 35, 'co2': 78, 'classe': 'Euro 5', 'cv_admin': 4, 'pl_debout': 0, 'db': 89, 'rpm': 8200, 'couleur': 'Vert'},
        33: {'pv': 1150, 'pm': 1650, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 95, 'co2': 115, 'classe': 'Euro 6d', 'cv_admin': 6, 'pl_debout': 0, 'db': 70, 'rpm': 6400, 'couleur': 'Vert'},
        34: {'pv': 1300, 'pm': 1850, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 120, 'co2': 125, 'classe': 'Euro 6d', 'cv_admin': 8, 'pl_debout': 0, 'db': 72, 'rpm': 6300, 'couleur': 'Gris'},
        35: {'pv': 2100, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 130, 'co2': 210, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 4600, 'couleur': 'Blanc'},
        36: {'pv': 2800, 'pm': 4700, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 170, 'co2': 245, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4400, 'couleur': 'Bleu'},
    
        19: {'pv': 130, 'pm': 310, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 12, 'co2': 60, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 83, 'rpm': 9500},
        20: {'pv': 210, 'pm': 400, 'permis': 'A', 'pl': 2, 'cyl': 998, 'cv': 200, 'co2': 155, 'classe': 'Euro 4', 'cv_admin': 14, 'pl_debout': 0, 'db': 102, 'rpm': 12500},
        21: {'pv': 1350, 'pm': 1900, 'permis': 'B', 'pl': 5, 'cyl': 1461, 'cv': 116, 'co2': 120, 'classe': 'Euro 6d', 'cv_admin': 7, 'pl_debout': 0, 'db': 68, 'rpm': 6800},
        22: {'pv': 1800, 'pm': 2400, 'permis': 'B', 'pl': 5, 'cyl': 1993, 'cv': 190, 'co2': 160, 'classe': 'Euro 6d', 'cv_admin': 10, 'pl_debout': 0, 'db': 74, 'rpm': 6200},
        23: {'pv': 2600, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2143, 'cv': 163, 'co2': 215, 'classe': 'Euro 6', 'cv_admin': 13, 'pl_debout': 0, 'db': 79, 'rpm': 4500},
        24: {'pv': 2900, 'pm': 4800, 'permis': 'C', 'pl': 3, 'cyl': 4250, 'cv': 170, 'co2': 230, 'classe': 'Euro 6', 'cv_admin': 14, 'pl_debout': 0, 'db': 81, 'rpm': 3800},
        # IVECO (25-30)
        25: {'pv': 150, 'pm': 330, 'permis': 'A2', 'pl': 2, 'cyl': 300, 'cv': 28, 'co2': 70, 'classe': 'Euro 5', 'cv_admin': 3, 'pl_debout': 0, 'db': 87, 'rpm': 8500},
        26: {'pv': 220, 'pm': 420, 'permis': 'A', 'pl': 2, 'cyl': 1100, 'cv': 210, 'co2': 165, 'classe': 'Euro 4', 'cv_admin': 15, 'pl_debout': 0, 'db': 106, 'rpm': 12000},
        27: {'pv': 2000, 'pm': 2800, 'permis': 'B', 'pl': 5, 'cyl': 2998, 'cv': 176, 'co2': 200, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 76, 'rpm': 5500},
        28: {'pv': 1900, 'pm': 2600, 'permis': 'B', 'pl': 5, 'cyl': 2500, 'cv': 150, 'co2': 190, 'classe': 'Euro 6', 'cv_admin': 9, 'pl_debout': 0, 'db': 74, 'rpm': 5800},
        29: {'pv': 2200, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 2300, 'cv': 140, 'co2': 225, 'classe': 'Euro 6', 'cv_admin': 11, 'pl_debout': 0, 'db': 77, 'rpm': 4300},
        30: {'pv': 2500, 'pm': 5000, 'permis': 'C', 'pl': 3, 'cyl': 2998, 'cv': 180, 'co2': 245, 'classe': 'Euro 6', 'cv_admin': 13, 'pl_debout': 0, 'db': 80, 'rpm': 4000},
        # FORD (31-36)
        31: {'pv': 115, 'pm': 290, 'permis': 'A1', 'pl': 2, 'cyl': 125, 'cv': 10, 'co2': 50, 'classe': 'Euro 5', 'cv_admin': 2, 'pl_debout': 0, 'db': 84, 'rpm': 9200},
        32: {'pv': 170, 'pm': 360, 'permis': 'A2', 'pl': 2, 'cyl': 450, 'cv': 35, 'co2': 78, 'classe': 'Euro 5', 'cv_admin': 4, 'pl_debout': 0, 'db': 89, 'rpm': 8200},
        33: {'pv': 1150, 'pm': 1650, 'permis': 'B', 'pl': 5, 'cyl': 999, 'cv': 95, 'co2': 115, 'classe': 'Euro 6d', 'cv_admin': 6, 'pl_debout': 0, 'db': 70, 'rpm': 6400},
        34: {'pv': 1300, 'pm': 1850, 'permis': 'B', 'pl': 5, 'cyl': 1498, 'cv': 120, 'co2': 125, 'classe': 'Euro 6d', 'cv_admin': 8, 'pl_debout': 0, 'db': 72, 'rpm': 6300},
        35: {'pv': 2100, 'pm': 3500, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 130, 'co2': 210, 'classe': 'Euro 6', 'cv_admin': 10, 'pl_debout': 0, 'db': 75, 'rpm': 4600},
        36: {'pv': 2800, 'pm': 4700, 'permis': 'C', 'pl': 3, 'cyl': 1995, 'cv': 170, 'co2': 245, 'classe': 'Euro 6', 'cv_admin': 12, 'pl_debout': 0, 'db': 78, 'rpm': 4400},
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
        if 'btn_load' in request.form and 'modele_id' in request.form:
            modele_id = request.form.get('modele_id')
            if modele_id and int(modele_id) in DONNEES_TECHNIQUES_REF:
                ref = DONNEES_TECHNIQUES_REF[int(modele_id)]
                prefilled_data = {
                    'poids_vide': ref.get('pv'),
                    'poids_max': ref.get('pm'),
                    'categorie_permis': ref.get('permis'),
                    'carburant_energie': ref.get('carburant'),
                    'places_assises': ref.get('pl'),
                    'cylindree': ref.get('cyl'),
                    'puissance_chevaux': ref.get('cv'),
                    'emission_co2': ref.get('co2'),
                    'classe_environnementale': ref.get('classe'),
                    'puissance_administrative_cv': ref.get('cv_admin'),
                    'places_debout': ref.get('pl_debout'),
                    'niveau_sonore_db': ref.get('db'),
                    'vitesse_max_moteur_rpm': ref.get('rpm'),
                    'couleur_principale': ref.get('couleur')
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
        
        try:
            # Récupération des données du formulaire
            nom = str(escape(request.form.get('nom', '').strip()))
            prenom = str(escape(request.form.get('prenom', '').strip()))
            adresse = str(escape(request.form.get('adresse', '').strip()))
            modele_id = request.form.get('modele_id')
            date_premiere_immat = request.form.get('date_premiere_immat')
            numero_serie = str(escape(request.form.get('numero_serie', '').strip()))
            categorie_permis = request.form.get('categorie_permis')
            carburant_energie = str(escape(request.form.get('carburant_energie', '').strip()))
            poids_vide = request.form.get('poids_vide')
            poids_max = request.form.get('poids_max')
            places_assises = request.form.get('places_assises')
            places_debout = request.form.get('places_debout')
            cylindree = request.form.get('cylindree')
            puissance_chevaux = request.form.get('puissance_chevaux')
            puissance_administrative_cv = request.form.get('puissance_administrative_cv')
            emission_co2 = request.form.get('emission_co2')
            classe_env = str(escape(request.form.get('classe_environnementale', '').strip()))
            niveau_sonore_db = request.form.get('niveau_sonore_db')
            vitesse_max_moteur_rpm = request.form.get('vitesse_max_moteur_rpm')
            date_fin_validite = request.form.get('date_fin_validite')
            date_premier_controle = request.form.get('date_premier_controle')
            date_controle_2 = request.form.get('date_controle_2')
            date_controle_3 = request.form.get('date_controle_3')
            
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
            
            # Vérification du VIN (ne doit pas exister pour d'autres véhicules)
            if numero_serie.strip():
                existing_vin = db.fetch_one("SELECT id FROM cartes_grises WHERE numero_serie=%s AND id!=%s", (numero_serie, carte_id))
                if existing_vin:
                    flash('Ce numéro VIN existe déjà pour un autre véhicule!', 'error')
                    return redirect(url_for('edit_carte_grise', carte_id=carte_id))
            
            # Mise à jour de la carte grise
            update_query = """
                UPDATE cartes_grises 
                SET proprietaire_id=%s, modele_id=%s, date_premiere_immat=%s, numero_serie=%s, categorie_permis=%s,
                    carburant_energie=%s, poids_vide_kg=%s, poids_max_kg=%s, places_assises=%s, places_debout=%s,
                    cylindree_cm3=%s, puissance_chevaux=%s, puissance_administrative_cv=%s,
                    emission_co2_g_km=%s, classe_environnementale=%s, niveau_sonore_db=%s,
                    vitesse_max_moteur_rpm=%s, date_fin_validite=%s, date_premier_controle=%s,
                    date_controle_2=%s, date_controle_3=%s
                WHERE id=%s
            """
            params = (
                proprietaire_id, modele_id, date_premiere_immat, numero_serie,
                categorie_permis,
                carburant_energie if carburant_energie else None,
                poids_vide, poids_max,
                places_assises if places_assises else None,
                places_debout if places_debout else None,
                cylindree if cylindree else None,
                puissance_chevaux if puissance_chevaux else None,
                puissance_administrative_cv if puissance_administrative_cv else None,
                emission_co2 if emission_co2 else None,
                classe_env if classe_env else None,
                niveau_sonore_db if niveau_sonore_db else None,
                vitesse_max_moteur_rpm if vitesse_max_moteur_rpm else None,
                date_fin_validite if date_fin_validite else None,
                date_premier_controle if date_premier_controle else None,
                date_controle_2 if date_controle_2 else None,
                date_controle_3 if date_controle_3 else None,
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
    
    # Import pour la date actuelle
    from datetime import date
    
    return render_template('edit.html', carte=carte, modeles=modeles, prefilled=prefilled_data, selected_modele_id=selected_modele_id, date_today=date.today())

@app.route('/delete/<int:carte_id>', methods=['POST'])
def delete_carte_grise(carte_id):
    """Suppression d'une carte grise"""
    # Note : On ne supprime pas le propriétaire, car il peut avoir d'autres véhicules.
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
    
    # Vérification : On ne traite que si le formulaire a été envoyé (méthode POST)
    if request.method == 'POST':

        # Récupération des données du formulaire HTML
        # request.form agit comme un dictionnaire contenant les inputs du formulaire
        search_type = request.form.get('search_type')

        # .strip() est crucial : il nettoie les espaces invisibles avant et après la saisie
        # Exemple : Si l'utilisateur tape " Dupont ", cela devient "Dupont"
        search_value = request.form.get('search_value', '').strip()
        
        # Recherche par nom du propriétaire
        if search_type == 'nom':
            # Construction de la requête SQL avec jointures (JOIN)
            # Les JOIN servent à récupérer les infos qui ne sont pas dans la table 'cartes_grises'
            # (ex: le nom du propriétaire est dans la table 'proprietaires')
            query = """
                SELECT cg.*, p.nom, p.prenom, mo.modele, ma.nom as marque_nom
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE p.nom LIKE %s
                ORDER BY p.nom, p.prenom
            """
            # Injection du paramètre avec des jokers (%) pour le LIKE SQL
            # f'%{valeur}%' signifie : "Contient cette valeur n'importe où"
            cartes = db.fetch_all(query, (f'%{search_value}%',))
        
        # Recherche par numéro de plaque
        # Logique : L'utilisateur peut écrire AA-123-BB ou AA123BB, le code doit comprendre les deux.
        elif search_type == 'plaque':
            # 2. Normalisation (Nettoyage) en Python
            # On retire les espaces et les tirets et on met tout en majuscules.
            # Cela permet de comparer uniquement les caractères alphanumériques.
            valeur_nettoyee = search_value.replace(' ', '').replace('-', '').strip().upper()

            # La requête SQL est astucieuse : elle compare deux choses
            # 1. La plaque telle qu'elle est stockée (avec tirets)
            # 2. La plaque stockée SANS tirets (via REPLACE SQL) pour matcher la saisie nettoyée
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

        # Recherche par numéro VIN (numéro de série)
        elif search_type == 'vin':
            # Nettoyage de la valeur saisie : suppression des espaces
            valeur_nettoyee = search_value.replace(' ', '').strip().upper()
            
            query = """
                SELECT cg.*, p.nom, p.prenom, mo.modele, ma.nom as marque_nom
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE cg.numero_serie LIKE %s
                ORDER BY cg.numero_serie
            """
            # Recherche partielle avec jokers pour permettre de chercher des fragments de VIN
            param = f'%{valeur_nettoyee}%'
            cartes = db.fetch_all(query, (param,))

        # Lister le nombre de véhicules > X années avec pollution > Y
        # Logique : L'utilisateur entre deux chiffres séparés par une virgule (ex: "10, 150")
        # Le premier est l'âge minimum, le second le CO2 minimum.
        elif search_type == 'critere_complexe':

            # Valeurs par défaut (si l'utilisateur ne remplit rien)
            age_min = 5
            co2_min = 120

            if ',' in search_value:
                try:
                    parts = search_value.split(',')  # Divise "10, 150" en ["10", " 150"]
                    age_min = int(parts[0].strip())  # Convertit "10" en entier 10
                    co2_min = int(parts[1].strip())  # Convertit "150" en entier 150
                except:
                    pass # On garde les valeurs par défaut si l'utilisateur écrit n'importe quoi

                    # L'instruction YEAR(CURRENT_DATE) - YEAR(date) permet de calculer l'âge
            # directement dans la base de données, sans avoir à le faire en Python.
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
    # Rendu final : on envoie la liste 'cartes' au template HTML
    return render_template('search.html', cartes=cartes)

# Point d'entrée de l'application
if __name__ == '__main__':
    # Configuration de mode debug, hôte et port depuis les variables d'environnement
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    # Lancement du serveur Flask
    app.run(debug=debug_mode, host=host, port=port)
