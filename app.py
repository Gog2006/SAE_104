from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from markupsafe import escape
from database import Database
from numero_generator import (
    generer_prochain_numero_carte_grise,
    generer_prochain_numero_plaque,
    formater_numero_plaque,
    generer_numero_serie
)
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Enable CSRF protection
csrf = CSRFProtect(app)

# Initialize database
db = Database()

@app.before_request
def before_request():
    """Connect to database before each request"""
    if not db.connection or not db.connection.is_connected():
        if not db.connect():
            flash('Erreur de connexion à la base de données. Veuillez vérifier votre configuration.', 'error')

@app.teardown_appcontext
def teardown_db(exception=None):
    """Close database connection after each request"""
    pass  # Keep connection open for performance

@app.route('/')
def index():
    """Home page - display all vehicle registration cards"""
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
    """Add new vehicle registration card"""
    if request.method == 'POST':
        try:
            # Get form data
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
            
            # Validate required fields
            if not all([nom, prenom, adresse, modele_id, date_premiere_immat]):
                flash('Les champs nom, prénom, adresse, modèle et date sont obligatoires!', 'error')
                return redirect(url_for('add_carte_grise'))
            
            # Get or create proprietaire
            query_prop = "SELECT id FROM proprietaires WHERE nom=%s AND prenom=%s AND adresse=%s"
            proprietaire = db.fetch_one(query_prop, (nom, prenom, adresse))
            
            if not proprietaire:
                insert_prop = "INSERT INTO proprietaires (nom, prenom, adresse) VALUES (%s, %s, %s)"
                proprietaire_id = db.execute_query(insert_prop, (nom, prenom, adresse))
            else:
                proprietaire_id = proprietaire['id']
            
            # Generate next registration card number
            last_carte = db.fetch_one("SELECT numero_carte_grise FROM cartes_grises ORDER BY id DESC LIMIT 1")
            if last_carte and last_carte.get('numero_carte_grise'):
                numero_carte = generer_prochain_numero_carte_grise(last_carte['numero_carte_grise'])
            else:
                numero_carte = generer_prochain_numero_carte_grise(None)
            
            # Generate next license plate number
            last_plaque = db.fetch_one("SELECT numero_immatriculation FROM cartes_grises ORDER BY id DESC LIMIT 1")
            if last_plaque and last_plaque.get('numero_immatriculation'):
                numero_plaque = generer_prochain_numero_plaque(last_plaque['numero_immatriculation'])
            else:
                numero_plaque = "AA10AA"
            
            # Ensure plate is unique - if duplicate, try next one
            while db.fetch_one("SELECT id FROM cartes_grises WHERE numero_immatriculation=%s", (numero_plaque,)):
                numero_plaque = generer_prochain_numero_plaque(numero_plaque)
                if numero_plaque is None:
                    flash('Erreur: Impossible de générer un numéro de plaque unique!', 'error')
                    return redirect(url_for('add_carte_grise'))
            
            # Generate serial number
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
            # Get count of vehicles for this month
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
            
            # Insert carte grise
            insert_carte = """
                INSERT INTO cartes_grises (
                    numero_carte_grise, numero_immatriculation, date_premiere_immat,
                    proprietaire_id, est_conducteur, modele_id, numero_serie,
                    poids_vide_kg, poids_max_kg, date_immat_actuelle, categorie_permis,
                    cylindree_cm3, puissance_chevaux, places_assises, emission_co2_g_km
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                numero_carte, numero_plaque, date_premiere_immat,
                proprietaire_id, True, modele_id, numero_serie,
                poids_vide, poids_max, date_premiere_immat, categorie_permis,
                cylindree if cylindree else None,
                puissance_chevaux if puissance_chevaux else None,
                places_assises if places_assises else None,
                emission_co2 if emission_co2 else None
            )
            
            if db.execute_query(insert_carte, params):
                flash(f'Carte grise créée avec succès! Numéro: {numero_carte}, Plaque: {formater_numero_plaque(numero_plaque)}', 'success')
                return redirect(url_for('index'))
            else:
                flash('Erreur lors de la création de la carte grise!', 'error')
        
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    # Get modeles for dropdown
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
    """Edit existing vehicle registration card"""
    if request.method == 'POST':
        try:
            # Get form data
            poids_vide = request.form.get('poids_vide')
            poids_max = request.form.get('poids_max')
            cylindree = request.form.get('cylindree')
            puissance_chevaux = request.form.get('puissance_chevaux')
            emission_co2 = request.form.get('emission_co2')
            classe_env = str(escape(request.form.get('classe_environnementale', '').strip()))
            
            # Update carte grise
            update_query = """
                UPDATE cartes_grises 
                SET poids_vide_kg=%s, poids_max_kg=%s, cylindree_cm3=%s,
                    puissance_chevaux=%s, emission_co2_g_km=%s, classe_environnementale=%s
                WHERE id=%s
            """
            params = (
                poids_vide, poids_max,
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
    
    # Get carte grise data
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
    
    return render_template('edit.html', carte=carte)

@app.route('/delete/<int:carte_id>', methods=['POST'])
def delete_carte_grise(carte_id):
    """Delete vehicle registration card"""
    query = "DELETE FROM cartes_grises WHERE id=%s"
    
    if db.execute_query(query, (carte_id,)):
        flash('Carte grise supprimée avec succès!', 'success')
    else:
        flash('Erreur lors de la suppression!', 'error')
    
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search and filter vehicle registration cards"""
    cartes = []
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        search_value = request.form.get('search_value', '').strip()
        
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
        
        elif search_type == 'plaque':
            query = """
                SELECT cg.*, p.nom, p.prenom, mo.modele, ma.nom as marque_nom
                FROM cartes_grises cg
                JOIN proprietaires p ON cg.proprietaire_id = p.id
                JOIN modeles mo ON cg.modele_id = mo.id
                JOIN marques ma ON mo.marque_id = ma.id
                WHERE cg.numero_immatriculation LIKE %s
                ORDER BY cg.numero_immatriculation
            """
            cartes = db.fetch_all(query, (f'%{search_value}%',))
        
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
    
    return render_template('search.html', cartes=cartes)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host=host, port=port)
