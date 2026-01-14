# SAE 1.04 - Système de Gestion des Cartes Grises

Système complet de gestion des cartes grises françaises - Base de données relationnelle avec interface web moderne et génération automatique de numéros.

## Description du Projet

Ce projet implémente un système de gestion des cartes grises entièrement conforme aux spécifications françaises avec toutes les rubriques officielles (0, A, B, C1-C4, D1-D2.1, E, F1-F2, H, I, J, P1-P3, S1-S2, U1-U2, V1-V2, X1-X1.7). Il permet de:

- **Gestion complète des cartes grises** avec tous les champs officiels français
- **Auto-remplissage intelligent** des caractéristiques techniques par modèle
- **Génération automatique** des numéros de cartes grises et plaques d'immatriculation
- **Interface web moderne** avec formulaires complets et tableau de bord détaillé
- **Base de données relationnelle** optimisée avec contraintes d'intégrité
- **36 modèles de véhicules prédéfinis** avec spécifications techniques complètes
- **Système de couleurs et dates de validité** intégré

## Nouveautés et Améliorations

### Conformité Carte Grise Française Complète
- **Tous les champs officiels** : Numéro VIN, couleur principale, puissance administrative CV, places debout
- **Dates de validité** : Certificat d'immatriculation, contrôles techniques programmés
- **Caractéristiques techniques avancées** : Niveau sonore (dB), vitesse maximale moteur (RPM)
- **Données techniques par défaut** pour 36 modèles de véhicules

### Auto-remplissage Intelligent
- **Bouton "Charger modèle"** : Remplit automatiquement tous les champs techniques
- **Données prédéfinies** : Poids, puissance, émissions, couleur, niveau sonore pour chaque modèle
- **Cohérence des données** : Spécifications réalistes par marque et type de véhicule

### Interface Enrichie
- **Tableau de bord complet** : Affichage de 15+ informations par véhicule
- **Index amélioré** : VIN, couleur, dates de validité, prochain contrôle technique
- **Formulaires complets** : Add/Edit avec tous les champs carte grise français

## Structure de la Base de Données

### Tables Principales

1. **cartes_grises** - Informations complètes des cartes grises (25+ champs conformes aux rubriques françaises)
2. **proprietaires** - Propriétaires des véhicules  
3. **modeles** - Modèles de véhicules avec spécifications techniques
4. **marques** - Marques de véhicules avec codes fabricant
5. **categories_vehicule** - 3 catégories: Deux roues, Automobile, Camion léger

### Champs Carte Grise (Conformité Française)

**Rubriques Administratives:**
- `numero_carte_grise` (0) - Numéro du certificat d'immatriculation
- `numero_immatriculation` (A) - Numéro d'immatriculation
- `date_premiere_immat` (B) - Date de première immatriculation 
- `numero_vin` (E) - Numéro d'identification du véhicule
- `couleur_principale` (C.1.3) - Couleur principale

**Caractéristiques Techniques:**
- `cylindree_cm3` (P1) - Cylindrée du moteur
- `puissance_chevaux` (P2) - Puissance maximale nette
- `puissance_administrative_cv` (P6) - Puissance administrative (CV fiscal)
- `niveau_sonore_db` (U1) - Niveau sonore à l'arrêt
- `vitesse_max_moteur_rpm` (U2) - Vitesse maximale du moteur
- `emission_co2_g_km` (V7) - Émissions de CO2
- `classe_environnementale` (V9) - Classe environnementale

**Poids et Places:**
- `poids_vide_kg` (G) - Poids à vide
- `poids_max_kg` (F1) - Poids total autorisé en charge
- `places_assises` (S1) - Nombre de places assises
- `places_debout` (S2) - Nombre de places debout

**Validité et Contrôles:**
- `date_fin_validite` (I) - Date de fin de validité du certificat
- `date_validite_certificat` - Date de validité du certificat d'immatriculation  
- `date_premier_controle` - Premier contrôle technique
- `date_prochain_controle` - Prochain contrôle technique programmé

### Schéma Relationnel

```
marques (id, nom, numero_fabricant)
    |
    ├─> modeles (id, marque_id, categorie_id, type_vehicule, modele)
    |       |
    |       └─> cartes_grises (id, numero_carte_grise, numero_immatriculation,
    |                          numero_vin, couleur_principale, date_premiere_immat,
    |                          proprietaire_id, modele_id, numero_serie, 
    |                          poids_vide_kg, poids_max_kg, cylindree_cm3,
    |                          puissance_chevaux, puissance_administrative_cv,
    |                          places_assises, places_debout, emission_co2_g_km,
    |                          niveau_sonore_db, vitesse_max_moteur_rpm,
    |                          date_fin_validite, date_validite_certificat,
    |                          date_premier_controle, date_prochain_controle...)
    |                   |
proprietaires <────────┘
    (id, nom, prenom, adresse)
```

## Technologies Utilisées

- **Backend**: Python 3.x avec Flask (routes, templates, sécurité CSRF)
- **Base de données**: MySQL (contraintes d'intégrité, transactions)
- **Frontend**: HTML5 + CSS responsive (interface moderne et ergonomique)
- **Générateurs**: Algorithmes de génération de numéros conformes
- **Sécurité**: Protection CSRF, échappement HTML, requêtes paramétrées

## Installation

### Prérequis

- Python 3.7 ou supérieur
- MySQL ou MariaDB
- phpMyAdmin (optionnel, pour la gestion de la base)

### Étapes d'Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/Gog2006/SAE_104.git
cd SAE_104

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Créer le fichier .env avec vos paramètres de connexion
cp .env.example .env
# Puis éditer .env avec vos informations MySQL

# 4. Créer la base de données
mysql -u root -p < setup_complete.sql

# 5. Lancer l'application
python3 app.py
```

L'application sera accessible sur `http://localhost:5000`

## Configuration

Créez un fichier `.env` à la racine du projet avec les paramètres suivants:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=carte_grise_db
DB_PORT=3306

SECRET_KEY=votre_cle_secrete
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

## Fonctionnalités Avancées

### Auto-remplissage Intelligent des Caractéristiques

Le système inclut une base de données technique de **36 modèles de véhicules** avec toutes leurs spécifications:

**Honda** (6 modèles)
- CB500F (Moto A2) - Rouge, 48 CV, 471 cm³, 95 dB
- CBR1000RR (Moto A) - Noir, 217 CV, 999 cm³, 105 dB  
- Civic (Auto B) - Blanc, 182 CV, 1498 cm³, 72 dB
- CR-V, NT400, Cabstar 35...

**Peugeot** (6 modèles)
- Kisbee 50 (A1) - Bleu, 4 CV, 49 cm³, 82 dB
- 208 (Auto B) - Bleu, 100 CV, 1199 cm³, 70 dB
- Boxer 440 (Camion C) - Blanc, 140 CV, 2179 cm³, 77 dB
- Metropolis, 5008, Expert...

**+ Renault, Mercedes, Iveco, Ford** avec spécifications complètes

### Génération Automatique des Numéros

#### Numéro de Carte Grise
- **Format**: `YYYYAA00000` (Année + 2 lettres + 5 chiffres)
- **Algorithme intelligent** : Incrémentation de droite à gauche
- **Exemples**:
  - `2026AA00010` → `2026AA00011`
  - `2026AA99999` → `2026AB00000` 
  - `2026AZ99999` → `2026BA00000`
  - `2026ZZ99999` → `2027AA00000` (changement d'année automatique)

#### Numéro de Plaque d'Immatriculation  
- **Format**: `AA000AA` (2 lettres + 3 chiffres + 2 lettres)
- **Contrainte**: Les chiffres du milieu ≥ 100
- **Stockage**: Format unifié sans espaces ni tirets
- **Affichage**: Formatage automatique `AA 000 AA`
- **Exemples**:
  - `AA100AA` → `AA100AB`
  - `AA100AZ` → `AA101AA`  
  - `AA999ZZ` → `AB100AA`

#### Numéro de Série VIN
- **Format**: `CodeFabricant + Année + Mois + Numéro6digits`
- **Exemple**: `HON2024M05000001`, `PEU2024M03000002`
- **Incrémentation**: Par mois et par fabricant

### Interface Utilisateur Moderne

#### Page d'Accueil (index.html)
**Tableau enrichi avec 15 colonnes d'informations:**
- N° Carte, Plaque (formatée), Propriétaire
- Marque/Modèle, **VIN (8 derniers caractères)**
- Date Immat., Permis, **Puissance (CV)**
- **Carburant**, Poids (vide/max), CO2
- **Couleur**, **Validité Certificat**, **Prochain CT**
- Classe Environnementale, Actions

#### Formulaires Add/Edit
**Sections organisées:**
- **Informations Propriétaire** : Nom, prénom, adresse
- **Informations Véhicule** : Modèle + bouton "Charger modèle"
- **Caractéristiques Techniques** : Auto-remplissage complet
- **Validité et Contrôles** : Dates de certificat et contrôles techniques

### Opérations CRUD Complètes

1. **Créer** - Interface de création avec auto-remplissage des spécifications techniques
2. **Lire** - Tableau de bord complet avec toutes les informations carte grise  
3. **Mettre à jour** - Formulaire de modification avec préchargement des données existantes
4. **Supprimer** - Suppression sécurisée avec confirmation

### Recherche et Statistiques

- **Par nom de propriétaire** - Recherche alphabétique
- **Par numéro de plaque** - Recherche partielle (début, fin, milieu)  
- **Statistiques par marque** - Classement par nombre de véhicules immatriculés

## Données Prédéfinies Complètes

### Marques et Modèles (36 véhicules)
- **6 marques** : Honda, Peugeot, Renault, Mercedes-Benz, Iveco, Ford
- **3 catégories** : Deux roues (A1/A2/A), Automobile (B), Camion léger (C)
- **6 modèles par marque** : 2 deux-roues + 2 automobiles + 2 camions

### Spécifications Techniques Réalistes
- **Puissances** : 4 à 217 CV selon le type de véhicule
- **Cylindrées** : 49 cm³ (scooter) à 4250 cm³ (camion)  
- **Couleurs** : Palette variée par marque (Blanc, Noir, Rouge, Bleu, Gris, Argent, Jaune, Orange, Vert)
- **Niveaux sonores** : 67-106 dB selon la motorisation
- **Régimes moteur** : 3600-13000 tr/min selon le type

### Exemples de Données
- **Honda CB500F** : Rouge, 48 CV, 471 cm³, Permis A2, 95 dB, 8500 tr/min
- **Peugeot 208** : Bleu, 100 CV, 1199 cm³, Permis B, 70 dB, 6200 tr/min  
- **Mercedes Sprinter** : Argent, 163 CV, 2143 cm³, Permis C, 79 dB, 4500 tr/min

## Sécurité

- Protection CSRF sur tous les formulaires
- Échappement HTML pour prévenir les attaques XSS
- Requêtes SQL paramétrées contre les injections SQL
- Variables d'environnement pour les données sensibles
- Gestion robuste des connexions MySQL

## Conformité SAE 1.04

Ce projet dépasse largement les exigences de la SAE 1.04 :

### Exigences de Base (100% Complètes)
- Schéma relationnel établi et documenté  
- Tables implémentées sous MySQL avec contraintes d'intégrité
- Fichier SQL d'initialisation (setup_complete.sql)
- Programmes de génération de numéros conformes (carte grise, plaque, VIN)
- Requêtes de consultation et statistiques
- Opérations CRUD complètes (ajout, modification, suppression)
- Interface HTML pour toutes les opérations

### Extensions Avancées (Valeur Ajoutée)
- **Conformité française complète** : Tous les champs carte grise officiels
- **Auto-remplissage intelligent** : 36 modèles avec spécifications techniques
- **Interface moderne et ergonomique** : Tableau de bord enrichi
- **Génération automatique VIN** : Algorithme complet avec codes fabricant
- **Système de couleurs et dates** : Gestion complète validité/contrôles
- **Sécurité renforcée** : Protection CSRF, échappement HTML, requêtes paramétrées

## Structure du Projet

```
SAE_104/
├── app.py                      # Application Flask principale (668 lignes)
│   ├── Routes : /, /add, /edit, /delete, /search
│   ├── Auto-remplissage : DONNEES_TECHNIQUES_REF (36 modèles)
│   ├── Sécurité : CSRF, HTML escaping, validation
│   └── Génération : Numéros carte grise, plaques, VIN
├── database.py                 # Gestionnaire connexion MySQL
├── numero_generator.py         # Algorithmes génération numéros
├── setup_complete.sql          # Schéma complet + données (233 lignes)
├── requirements.txt            # Dépendances Python
├── static/
│   └── style.css              # Interface responsive moderne
├── templates/                 # Templates HTML Jinja2
│   ├── base.html             # Template de base avec navigation
│   ├── index.html            # Tableau de bord 15 colonnes
│   ├── add.html              # Formulaire création (auto-remplissage)
│   ├── edit.html             # Formulaire modification
│   └── search.html           # Interface recherche/statistiques
└── README.md                  # Documentation complète
```

## Installation et Démarrage

### Prérequis
- Python 3.7+ 
- MySQL 8.0+ 
- Navigateur moderne (Chrome, Firefox, Safari, Edge)

### Installation Rapide
```bash
# 1. Cloner et configurer
git clone https://github.com/Gog2006/SAE_104.git
cd SAE_104
pip install -r requirements.txt

# 2. Base de données (saisir mot de passe MySQL)
mysql -u root -p < setup_complete.sql

# 3. Lancer l'application  
python3 app.py
```

**Application accessible sur http://localhost:5000**

### Configuration Environnement (Optionnel)

Fichier `.env` pour personnaliser :
```env
DB_HOST=localhost
DB_USER=root  
DB_PASSWORD=votre_mot_de_passe
DB_NAME=carte_grise_db
SECRET_KEY=votre_cle_secrete_longue(pas obligatoire)
FLASK_DEBUG=False
```

## Utilisation du Système

### Créer une Nouvelle Carte Grise

1. Cliquer sur **"Nouvelle carte"** depuis la page d'accueil 
2. **Sélectionner le modèle de véhicule** dans la liste déroulante
3. **Cliquer "Charger modèle"** → Auto-remplissage de tous les champs techniques :
   - Poids à vide/maximal, cylindrée, puissance
   - Couleur principale, émissions CO2, classe environnementale  
   - Niveau sonore, vitesse maximale moteur, CV administratifs,couleur
4.**Choisir la date de mise en immatriculation** choix de la date jour/mois/an
5.**Remplir les informations propriétaire** : nom, prénom, adresse 
6. **Ajuster si nécessaire** les dates de validité et contrôles techniques
7. **Valider** → Génération automatique des numéros carte grise, plaque, et VIN

### Modifier une Carte Existante  

1. Cliquer **"Modifier"** sur la ligne du véhicule dans le tableau
2. Les données existantes sont pré-remplies dans le formulaire  
3. **Option "Charger modèle"** disponible pour réinitialiser les specs techniques
4. **Sauvegarder** → Mise à jour immédiate en base

### Rechercher et Consulter

1. **Page d'accueil** : Vue d'ensemble avec tableau complet (15 colonnes)
2. **Recherche** : Accès via le menu pour filtres spécifiques  
3. **Détails affichés** : N° de la Carte	Plaque	Propriétaire	Marque/Modèle	Détails (Age/CO2)

### Informations Affichées (Page d'Accueil)

Le tableau principal affiche pour chaque véhicule :
- **Identification** : N° Carte Grise, Plaque (AA 000 AA), VIN (8 derniers chiffres)
- **Propriétaire** : Nom complet  
- **Véhicule** : Marque/Modèle, carburant/énergie, couleur principale
- **Technique** : Puissance CV, poids vide/maximal, émissions CO2
- **Administratif** : Date immatriculation, catégorie permis, classe environnementale
- **Validité** : Validité certificat, prochain contrôle technique
- **Actions** : Modifier, Supprimer

## Licence

Ce projet est développé dans le cadre de la SAE 1.04 - BUT Informatique.

## Contribution

Développé pour le projet SAE 1.04 - Création d'une base de données relationnelle.
