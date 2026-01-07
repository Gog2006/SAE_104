-- SAE 1.04: Création d'une base de données pour les cartes grises
-- Database for vehicle registration cards (cartes grises)

CREATE DATABASE IF NOT EXISTS carte_grise_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE carte_grise_db;

-- Table des propriétaires (owners)
CREATE TABLE IF NOT EXISTS proprietaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    adresse TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nom (nom),
    INDEX idx_prenom (prenom)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des marques (brands)
CREATE TABLE IF NOT EXISTS marques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    numero_fabricant VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des catégories de véhicules (vehicle categories)
CREATE TABLE IF NOT EXISTS categories_vehicule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    permis_requis VARCHAR(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des modèles de véhicules (vehicle models)
CREATE TABLE IF NOT EXISTS modeles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    marque_id INT NOT NULL,
    categorie_id INT NOT NULL,
    type_vehicule VARCHAR(100) NOT NULL,
    modele VARCHAR(100) NOT NULL,
    FOREIGN KEY (marque_id) REFERENCES marques(id) ON DELETE CASCADE,
    FOREIGN KEY (categorie_id) REFERENCES categories_vehicule(id) ON DELETE CASCADE,
    INDEX idx_marque (marque_id),
    INDEX idx_categorie (categorie_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des cartes grises (vehicle registration cards)
CREATE TABLE IF NOT EXISTS cartes_grises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_carte_grise VARCHAR(20) NOT NULL UNIQUE COMMENT 'Format: YYYYAA00000',
    numero_immatriculation VARCHAR(20) NOT NULL UNIQUE COMMENT 'Format: AA000AA',
    date_premiere_immat DATE NOT NULL,
    proprietaire_id INT NOT NULL,
    est_conducteur BOOLEAN DEFAULT TRUE COMMENT 'C4: Si conducteur = propriétaire',
    modele_id INT NOT NULL,
    numero_serie VARCHAR(50) NOT NULL UNIQUE,
    poids_vide_kg INT NOT NULL COMMENT 'F1',
    poids_max_kg INT NOT NULL COMMENT 'F2',
    date_fin_validite DATE COMMENT 'H',
    date_immat_actuelle DATE NOT NULL COMMENT 'I',
    categorie_permis VARCHAR(10) NOT NULL COMMENT 'J: A1, A2, A, B, C',
    cylindree_cm3 INT COMMENT 'P1',
    puissance_chevaux INT COMMENT 'P2',
    puissance_cv INT COMMENT 'P3',
    places_assises INT COMMENT 'S1',
    places_debout INT DEFAULT 0 COMMENT 'S2',
    niveau_sonore_db INT COMMENT 'U1',
    vitesse_max_tr_mn INT COMMENT 'U2',
    emission_co2_g_km INT COMMENT 'V1',
    classe_environnementale VARCHAR(20) COMMENT 'V2',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (proprietaire_id) REFERENCES proprietaires(id) ON DELETE CASCADE,
    FOREIGN KEY (modele_id) REFERENCES modeles(id) ON DELETE CASCADE,
    INDEX idx_numero_carte (numero_carte_grise),
    INDEX idx_numero_plaque (numero_immatriculation),
    INDEX idx_date_immat (date_immat_actuelle),
    INDEX idx_proprietaire (proprietaire_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table des contrôles techniques (technical inspections)
CREATE TABLE IF NOT EXISTS controles_techniques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carte_grise_id INT NOT NULL,
    date_controle DATE NOT NULL,
    numero_controle INT NOT NULL COMMENT '1 pour premier, 2 pour deuxième, etc.',
    resultat ENUM('Favorable', 'Défavorable', 'Contre-visite') DEFAULT 'Favorable',
    FOREIGN KEY (carte_grise_id) REFERENCES cartes_grises(id) ON DELETE CASCADE,
    INDEX idx_carte_grise (carte_grise_id),
    INDEX idx_date_controle (date_controle)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insérer les catégories de véhicules
INSERT INTO categories_vehicule (code, nom, permis_requis) VALUES
('DEUX_ROUES', 'Deux roues', 'A1'),
('AUTOMOBILE', 'Automobile', 'B'),
('CAMION_LEGER', 'Camion léger (3000-5000kg)', 'C');

-- Insérer les marques avec leurs numéros de fabricant
INSERT INTO marques (nom, numero_fabricant) VALUES
('Peugeot', 'PGT'),
('Renault', 'REN'),
('Honda', 'HND'),
('Yamaha', 'YMH'),
('Ford', 'FRD'),
('Mercedes', 'MRC');

-- Insérer les modèles (2 modèles par catégorie pour chaque marque)
-- Deux roues
INSERT INTO modeles (marque_id, categorie_id, type_vehicule, modele) VALUES
((SELECT id FROM marques WHERE nom='Honda'), (SELECT id FROM categories_vehicule WHERE code='DEUX_ROUES'), 'Moto', 'CB500F'),
((SELECT id FROM marques WHERE nom='Honda'), (SELECT id FROM categories_vehicule WHERE code='DEUX_ROUES'), 'Moto', 'CBR600RR'),
((SELECT id FROM marques WHERE nom='Yamaha'), (SELECT id FROM categories_vehicule WHERE code='DEUX_ROUES'), 'Moto', 'MT-07'),
((SELECT id FROM marques WHERE nom='Yamaha'), (SELECT id FROM categories_vehicule WHERE code='DEUX_ROUES'), 'Moto', 'R1');

-- Automobiles
INSERT INTO modeles (marque_id, categorie_id, type_vehicule, modele) VALUES
((SELECT id FROM marques WHERE nom='Peugeot'), (SELECT id FROM categories_vehicule WHERE code='AUTOMOBILE'), 'Berline', '308'),
((SELECT id FROM marques WHERE nom='Peugeot'), (SELECT id FROM categories_vehicule WHERE code='AUTOMOBILE'), 'SUV', '3008'),
((SELECT id FROM marques WHERE nom='Renault'), (SELECT id FROM categories_vehicule WHERE code='AUTOMOBILE'), 'Berline', 'Megane'),
((SELECT id FROM marques WHERE nom='Renault'), (SELECT id FROM categories_vehicule WHERE code='AUTOMOBILE'), 'SUV', 'Captur'),
((SELECT id FROM marques WHERE nom='Ford'), (SELECT id FROM categories_vehicule WHERE code='AUTOMOBILE'), 'Berline', 'Focus'),
((SELECT id FROM marques WHERE nom='Ford'), (SELECT id FROM categories_vehicule WHERE code='AUTOMOBILE'), 'SUV', 'Kuga');

-- Camions légers
INSERT INTO modeles (marque_id, categorie_id, type_vehicule, modele) VALUES
((SELECT id FROM marques WHERE nom='Peugeot'), (SELECT id FROM categories_vehicule WHERE code='CAMION_LEGER'), 'Fourgon', 'Boxer'),
((SELECT id FROM marques WHERE nom='Peugeot'), (SELECT id FROM categories_vehicule WHERE code='CAMION_LEGER'), 'Utilitaire', 'Partner'),
((SELECT id FROM marques WHERE nom='Renault'), (SELECT id FROM categories_vehicule WHERE code='CAMION_LEGER'), 'Fourgon', 'Master'),
((SELECT id FROM marques WHERE nom='Renault'), (SELECT id FROM categories_vehicule WHERE code='CAMION_LEGER'), 'Utilitaire', 'Kangoo'),
((SELECT id FROM marques WHERE nom='Mercedes'), (SELECT id FROM categories_vehicule WHERE code='CAMION_LEGER'), 'Fourgon', 'Sprinter'),
((SELECT id FROM marques WHERE nom='Mercedes'), (SELECT id FROM categories_vehicule WHERE code='CAMION_LEGER'), 'Utilitaire', 'Vito');

-- Insérer des propriétaires exemples
INSERT INTO proprietaires (nom, prenom, adresse) VALUES
('Dupont', 'Jean', '15 Rue de la Paix, 75001 Paris'),
('Martin', 'Marie', '28 Avenue des Champs, 69002 Lyon'),
('Bernard', 'Pierre', '42 Boulevard Victor Hugo, 33000 Bordeaux'),
('Dubois', 'Sophie', '7 Place de la République, 59000 Lille'),
('Thomas', 'Luc', '19 Rue du Commerce, 13001 Marseille');

-- Insérer quelques cartes grises exemples
INSERT INTO cartes_grises (
    numero_carte_grise, numero_immatriculation, date_premiere_immat, proprietaire_id,
    est_conducteur, modele_id, numero_serie, poids_vide_kg, poids_max_kg,
    date_fin_validite, date_immat_actuelle, categorie_permis, cylindree_cm3,
    puissance_chevaux, puissance_cv, places_assises, emission_co2_g_km, classe_environnementale
) VALUES
('2020AA00001', 'AB123CD', '2020-03-15', 1, TRUE, 
 (SELECT id FROM modeles WHERE modele='308' LIMIT 1),
 'PGT2020M03000001', 1200, 1800, '2030-03-15', '2020-03-15', 'B',
 1560, 130, 7, 5, 110, 'Euro 6'),
 
('2021AB00001', 'BE456FG', '2021-06-20', 2, TRUE,
 (SELECT id FROM modeles WHERE modele='Megane' LIMIT 1),
 'REN2021M06000001', 1150, 1750, '2031-06-20', '2021-06-20', 'B',
 1500, 115, 6, 5, 105, 'Euro 6'),
 
('2022AC00001', 'CD789HI', '2022-01-10', 3, TRUE,
 (SELECT id FROM modeles WHERE modele='CB500F' LIMIT 1),
 'HND2022M01000001', 190, 400, '2032-01-10', '2022-01-10', 'A2',
 471, 47, 3, 2, 85, 'Euro 5'),
 
('2023AD00001', 'EF012JK', '2023-09-05', 4, TRUE,
 (SELECT id FROM modeles WHERE modele='Boxer' LIMIT 1),
 'PGT2023M09000001', 2800, 4500, '2033-09-05', '2023-09-05', 'C',
 2200, 140, 9, 3, 180, 'Euro 6');

-- Insérer des contrôles techniques pour les véhicules de 2021 et 2022
INSERT INTO controles_techniques (carte_grise_id, date_controle, numero_controle, resultat) VALUES
((SELECT id FROM cartes_grises WHERE numero_carte_grise='2021AB00001'), '2025-06-20', 1, 'Favorable'),
((SELECT id FROM cartes_grises WHERE numero_carte_grise='2022AC00001'), '2026-01-10', 1, 'Favorable');
