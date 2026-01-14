# SAE 1.04 - Création d'une Base de Données

Système de gestion des cartes grises (vehicle registration cards) - Base de données relationnelle avec interface web.

## Description du Projet

Ce projet implémente un système complet de gestion des cartes grises conformément aux spécifications de la SAE 1.04. Il permet de:

- Créer et gérer une base de données relationnelle pour les cartes grises
- Générer automatiquement les numéros de cartes grises et de plaques d'immatriculation
- Ajouter, modifier et supprimer des cartes grises
- Rechercher et filtrer les cartes grises selon différents critères
- Consulter des statistiques (ex: nombre de véhicules par marque)
- Interface HTML pour toutes les opérations

## Structure de la Base de Données

### Tables Principales

1. **cartes_grises** - Informations complètes des cartes grises
2. **proprietaires** - Propriétaires des véhicules
3. **modeles** - Modèles de véhicules
4. **marques** - Marques de véhicules
5. **categories_vehicule** - 3 catégories: Deux roues, Automobile, Camion léger
6. **controles_techniques** - Historique des contrôles techniques

### Schéma Relationnel

```
marques (id, nom, numero_fabricant)
    |
    ├─> modeles (id, marque_id, categorie_id, type_vehicule, modele)
    |       |
    |       └─> cartes_grises (id, numero_carte_grise, numero_immatriculation, 
    |                          date_premiere_immat, proprietaire_id, modele_id,
    |                          numero_serie, poids_vide_kg, poids_max_kg, ...)
    |                   |
proprietaires <────────┘
    (id, nom, prenom, adresse)

cartes_grises ─> controles_techniques (id, carte_grise_id, date_controle, ...)
```

## Technologies Utilisées

- **Backend**: Python 3.x avec Flask
- **Base de données**: MySQL/MariaDB (compatible phpMyAdmin)
- **Frontend**: HTML5 avec CSS intégré
- **Sécurité**: CSRF protection, HTML escaping

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

## Fonctionnalités Implémentées

### Génération Automatique de Numéros

#### Numéro de Carte Grise
- Format: `YYYYAA00000` (Année + 2 lettres + 5 chiffres)
- Exemples:
  - `2026AA00010` → `2026AA00011`
  - `2026AA99999` → `2026AB00000`
  - `2026AZ99999` → `2026BA00000`

#### Numéro de Plaque d'Immatriculation
- Format: `AA000AA` (2 lettres + 3 chiffres + 2 lettres)
- Les chiffres du milieu doivent être ≥ 100
- Exemples:
  - `AB 78 ZA` → `AB 78 ZB`
  - `AB 78 ZZ` → `AB 79 AA`
  - `AB 999 ZZ` → `AC 10 AA`

#### Numéro de Série
- Format: `NuméroFabricant + Année + Mois + Numéro à 6 chiffres`
- Exemple: `PGT2026M01000001`

### Opérations CRUD

1. **Créer** - Ajouter une nouvelle carte grise via interface HTML
2. **Lire** - Consulter toutes les cartes grises avec leurs détails
3. **Mettre à jour** - Modifier les caractéristiques techniques d'une carte
4. **Supprimer** - Supprimer une carte grise

### Recherche et Filtres

- **Par nom de propriétaire** - Recherche alphabétique
- **Par numéro de plaque** - Recherche partielle (début, fin, milieu)
- **Statistiques par marque** - Classement décroissant des marques les plus immatriculées

## Données Prédéfinies

Le système inclut des données d'exemple:

- **Marques**: Peugeot, Renault, Honda, Yamaha, Ford, Mercedes
- **3 catégories**: Deux roues, Automobile, Camion léger
- **Modèles**: 2 modèles par catégorie pour chaque marque
- **Propriétaires**: Exemples de propriétaires
- **Cartes grises**: Exemples avec dates entre 2020 et 2026
- **Permis requis**: A1, A2, A, B, C

## Sécurité

- Protection CSRF sur tous les formulaires
- Échappement HTML pour prévenir les attaques XSS
- Requêtes SQL paramétrées contre les injections SQL
- Variables d'environnement pour les données sensibles
- Gestion robuste des connexions MySQL

## Structure du Projet

```
SAE_104/
├── app.py                      # Application Flask principale
├── database.py                 # Gestion de la connexion MySQL
├── numero_generator.py         # Génération des numéros
├── setup_complete.sql          # Schéma et données initiales
├── requirements.txt            # Dépendances Python
├── static/
│   └── style.css              # Feuille de styles CSS
├── templates/                 # Templates HTML
│   ├── base.html             # Template de base
│   ├── index.html            # Liste des cartes grises
│   ├── add.html              # Ajouter une carte
│   ├── edit.html             # Modifier une carte
│   └── search.html           # Recherche et filtres
└── README.md                  # Ce fichier
```

## Conformité SAE 1.04

Ce projet répond à toutes les exigences de la SAE 1.04:

- Schéma relationnel établi et documenté
- Tables implémentées sous MySQL
- Fichier SQL pour initialiser les tables
- Programmes de génération de numéros (carte grise, plaque)
- Requêtes de consultation et statistiques
- Ajout de nouvelles cartes (SQL + interface HTML)
- Mise à jour des cartes (SQL + interface HTML)
- Suppression des cartes (SQL + interface HTML)

## Utilisation

### Ajouter une Carte Grise

1. Cliquer sur "Nouvelle carte"
2. Remplir les informations du propriétaire
3. Sélectionner le modèle de véhicule
4. Renseigner les caractéristiques techniques
5. Les numéros de carte et de plaque sont générés automatiquement

### Rechercher

1. Cliquer sur "Rechercher"
2. Choisir le type de recherche
3. Saisir la valeur de recherche
4. Consulter les résultats

### Statistiques

Utiliser la recherche "Statistiques par marque" pour voir le classement des marques par nombre de véhicules immatriculés.

## Licence

Ce projet est développé dans le cadre de la SAE 1.04 - BUT Informatique.

## Contribution

Développé pour le projet SAE 1.04 - Création d'une base de données relationnelle.
