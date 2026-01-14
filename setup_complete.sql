
-- =========================
-- Drop and Create Database
-- =========================
DROP DATABASE IF EXISTS carte_grise_db;
CREATE DATABASE carte_grise_db;
USE carte_grise_db;

-- =========================
-- Drop existing tables if they exist (in correct order due to foreign keys)
-- =========================
DROP TABLE IF EXISTS cartes_grises;
DROP TABLE IF EXISTS modeles;
DROP TABLE IF EXISTS marques;
DROP TABLE IF EXISTS categories_vehicule;
DROP TABLE IF EXISTS proprietaires;

-- =========================
-- Categories de vehicule
-- =========================
CREATE TABLE categories_vehicule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Marques
-- =========================
CREATE TABLE marques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    numero_fabricant VARCHAR(10) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Modeles
-- =========================
CREATE TABLE modeles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modele VARCHAR(100) NOT NULL,
    marque_id INT NOT NULL,
    categorie_id INT NOT NULL,
    type_vehicule VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (marque_id) REFERENCES marques(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (categorie_id) REFERENCES categories_vehicule(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_modele_marque (marque_id),
    INDEX idx_modele_categorie (categorie_id),
    INDEX idx_modele_nom (modele)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Proprietaires
-- =========================
CREATE TABLE proprietaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    adresse VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nom_proprietaire (nom),
    INDEX idx_prenom_proprietaire (prenom)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Cartes grises
-- =========================
CREATE TABLE cartes_grises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_carte_grise VARCHAR(20) NOT NULL UNIQUE,
    numero_immatriculation VARCHAR(9) NOT NULL UNIQUE,
    date_premiere_immat DATE NOT NULL,
    date_immat_actuelle DATE NOT NULL,
    proprietaire_id INT NOT NULL,
    est_conducteur BOOLEAN DEFAULT TRUE,
    modele_id INT NOT NULL,
    numero_serie VARCHAR(30) NOT NULL UNIQUE,
    poids_vide_kg INT NOT NULL,
    poids_max_kg INT NOT NULL,
    categorie_permis VARCHAR(5) NOT NULL,
    carburant_energie VARCHAR(50) NOT NULL,
    cylindree_cm3 INT NOT NULL,
    puissance_chevaux INT NOT NULL,
    puissance_administrative_cv INT,
    places_assises INT NOT NULL,
    places_debout INT DEFAULT 0,
    emission_co2_g_km INT,
    classe_environnementale VARCHAR(20),
    niveau_sonore_db INT,
    vitesse_max_moteur_rpm INT,
    couleur_principale VARCHAR(50),
    date_validite_certificat DATE,
    date_prochain_controle DATE,
    date_fin_validite DATE,
    date_premier_controle DATE,
    date_controle_2 DATE,
    date_controle_3 DATE,
    date_controle_4 DATE,
    date_controle_5 DATE,
    date_controle_6 DATE,
    date_controle_7 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proprietaire_id) REFERENCES proprietaires(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (modele_id) REFERENCES modeles(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_immat (numero_immatriculation),
    INDEX idx_numero_carte (numero_carte_grise),
    INDEX idx_carte_proprietaire (proprietaire_id),
    INDEX idx_carte_modele (modele_id),
    INDEX idx_date_immat (date_immat_actuelle),
    CHECK (poids_vide_kg > 0),
    CHECK (poids_max_kg > poids_vide_kg),
    CHECK (cylindree_cm3 > 0),
    CHECK (puissance_chevaux > 0),
    CHECK (places_assises > 0),
    CHECK (emission_co2_g_km >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================
-- Insert initial categories
-- =========================
INSERT INTO categories_vehicule (nom) VALUES 
('Deux roues'),
('Automobile'),
('Camion léger');

-- =========================
-- Insert initial marques with manufacturer numbers
-- =========================
INSERT INTO marques (nom, numero_fabricant) VALUES 
('Honda', 'HON'),
('Peugeot', 'PEU'),
('Renault', 'REN'),
('Mercedes-Benz', 'MER'),
('Iveco', 'IVE'),
('Ford', 'FOR');

-- =========================
-- Insert initial modeles
-- =========================

-- Honda models
INSERT INTO modeles (modele, marque_id, categorie_id, type_vehicule) VALUES 
('CB500F', 1, 1, 'Deux roues - A2'),
('CBR1000RR', 1, 1, 'Deux roues - A'),
('Civic', 1, 2, 'Automobile - B'),
('CR-V', 1, 2, 'Automobile - B'),
('NT400', 1, 3, 'Camion léger - C'),
('Cabstar 35', 1, 3, 'Camion léger - C');

-- Peugeot models
INSERT INTO modeles (modele, marque_id, categorie_id, type_vehicule) VALUES 
('Kisbee 50', 2, 1, 'Deux roues - A1'),
('Metropolis', 2, 1, 'Deux roues - A'),
('208', 2, 2, 'Automobile - B'),
('5008', 2, 2, 'Automobile - B'),
('Boxer 440', 2, 3, 'Camion léger - C'),
('Expert L3', 2, 3, 'Camion léger - C');

-- Renault models
INSERT INTO modeles (modele, marque_id, categorie_id, type_vehicule) VALUES 
('Full 125', 3, 1, 'Deux roues - A1'),
('Sport 400', 3, 1, 'Deux roues - A2'),
('Clio', 3, 2, 'Automobile - B'),
('Austral', 3, 2, 'Automobile - B'),
('Master 3.5t', 3, 3, 'Camion léger - C'),
('Maxity', 3, 3, 'Camion léger - C');

-- Mercedes-Benz models
INSERT INTO modeles (modele, marque_id, categorie_id, type_vehicule) VALUES 
('Citan Scooter', 4, 1, 'Deux roues - A1'),
('Vision GT', 4, 1, 'Deux roues - A'),
('Classe A', 4, 2, 'Automobile - B'),
('GLC', 4, 2, 'Automobile - B'),
('Sprinter 5t', 4, 3, 'Camion léger - C'),
('Vario', 4, 3, 'Camion léger - C');

-- Iveco models
INSERT INTO modeles (modele, marque_id, categorie_id, type_vehicule) VALUES 
('Daily Moto', 5, 1, 'Deux roues - A2'),
('Turbo Bike', 5, 1, 'Deux roues - A'),
('Massif', 5, 2, 'Automobile - B'),
('Campagnola', 5, 2, 'Automobile - B'),
('Daily 35C', 5, 3, 'Camion léger - C'),
('Daily 50C', 5, 3, 'Camion léger - C');

-- Ford models
INSERT INTO modeles (modele, marque_id, categorie_id, type_vehicule) VALUES 
('Street 125', 6, 1, 'Deux roues - A1'),
('Ranger Bike', 6, 1, 'Deux roues - A2'),
('Fiesta', 6, 2, 'Automobile - B'),
('Focus', 6, 2, 'Automobile - B'),
('Transit 350', 6, 3, 'Camion léger - C'),
('Transit 470', 6, 3, 'Camion léger - C');

-- =========================
-- Insert proprietaires (MUST be inserted BEFORE cartes_grises)
-- =========================
INSERT INTO proprietaires (nom, prenom, adresse) VALUES 
('Dupont', 'Jean', '12 Rue de Paris, 75001 Paris'),
('Martin', 'Sophie', '45 Avenue des Champs, 69000 Lyon'),
('Bernard', 'Pierre', '8 Boulevard Victor Hugo, 13001 Marseille'),
('Dubois', 'Marie', '23 Rue de la République, 33000 Bordeaux'),
('Thomas', 'Luc', '67 Avenue de la Liberté, 31000 Toulouse'),
('Robert', 'Claire', '34 Rue Nationale, 59000 Lille');

-- =========================
-- Insert cartes grises
-- =========================
INSERT INTO cartes_grises (
    numero_carte_grise, numero_immatriculation, date_premiere_immat, date_immat_actuelle, 
    proprietaire_id, est_conducteur, modele_id, numero_serie, poids_vide_kg, poids_max_kg, 
    categorie_permis, carburant_energie, cylindree_cm3, puissance_chevaux, puissance_administrative_cv, 
    places_assises, places_debout, emission_co2_g_km, classe_environnementale, 
    niveau_sonore_db, vitesse_max_moteur_rpm, couleur_principale, date_fin_validite, 
    date_premier_controle, date_validite_certificat, date_prochain_controle
) VALUES
-- Honda Civic (Automobile - B) - ID Modele: 3
('2026AA00001', 'AA100AA', '2020-05-12', '2020-05-12', 1, TRUE, 3, 'HON2020M05000001', 1300, 1800, 'B', 'Essence', 1498, 182, 12, 5, 0, 128, 'Euro 6d', 72, 6200, 'Blanc', '2030-05-12', '2024-05-12', '2030-05-12', '2024-05-12'),
-- Honda CB500F (Deux roues - A2) - ID Modele: 1
('2026AA00002', 'AA100AB', '2021-06-15', '2021-06-15', 2, TRUE, 1, 'HON2021M06000001', 190, 370, 'A2', 'Essence', 471, 48, 35, 2, 0, 80, 'Euro 5', 95, 8500, 'Rouge', '2031-06-15', '2024-06-15', '2031-06-15', '2024-06-15'),
-- Peugeot 208 (Automobile - B) - ID Modele: 9
('2026AA00003', 'AA100AC', '2022-03-20', '2022-03-20', 3, TRUE, 9, 'PEU2022M03000001', 1050, 1550, 'B', 'Essence', 1199, 100, 8, 5, 0, 102, 'Euro 6d', 70, 5800, 'Bleu', '2032-03-20', '2025-03-20', '2032-03-20', '2026-03-20'),
-- Peugeot Boxer 440 (Camion léger - C) - ID Modele: 11
('2026AA00004', 'AA100AD', '2021-11-05', '2021-11-05', 4, TRUE, 11, 'PEU2021M11000001', 2100, 4400, 'C', 'Diesel', 2179, 140, 8, 3, 0, 230, 'Euro 6d', 74, 3500, 'Blanc', '2031-11-05', '2024-11-05', '2031-11-05', '2025-11-05'),
-- Renault Clio (Automobile - B) - ID Modele: 15
('2026AA00005', 'AA100AE', '2023-01-10', '2023-01-10', 5, TRUE, 15, 'REN2023M01000001', 1100, 1600, 'B', 'Essence', 999, 90, 6, 5, 0, 110, 'Euro 6d', 68, 5500, 'Gris', '2033-01-10', '2026-01-10', '2033-01-10', '2027-01-10'),
-- Renault Master (Camion léger - C) - ID Modele: 17
('2026AA00006', 'AA100AF', '2020-08-22', '2020-08-22', 6, TRUE, 17, 'REN2020M08000001', 2200, 3500, 'C', 'Diesel', 2299, 135, 8, 3, 0, 240, 'Euro 6d', 75, 3800, 'Jaune', '2030-08-22', '2024-08-22', '2030-08-22', '2025-08-22'),
-- Mercedes Classe A (Automobile - B) - ID Modele: 21
('2026AA00007', 'AA100AG', '2024-04-15', '2024-04-15', 1, TRUE, 21, 'MER2024M04000001', 1400, 1950, 'B', 'Essence', 1332, 140, 10, 5, 0, 130, 'Euro 6d', 69, 6000, 'Noir', '2034-04-15', '2027-04-15', '2034-04-15', '2028-04-15'),
-- Mercedes Sprinter 5t (Camion léger - C) - ID Modele: 23
('2026AA00008', 'AA100AH', '2021-02-28', '2021-02-28', 2, TRUE, 23, 'MER2021M02000001', 2600, 5000, 'C', 'Diesel', 2143, 163, 9, 3, 0, 215, 'Euro 6d', 73, 3600, 'Argent', '2031-02-28', '2024-02-28', '2031-02-28', '2025-02-28'),
-- Iveco Daily 35C (Camion léger - C) - ID Modele: 29
('2026AA00009', 'AA100AI', '2022-10-12', '2022-10-12', 3, TRUE, 29, 'IVE2022M10000001', 2200, 3500, 'C', 'Diesel', 2998, 160, 10, 3, 0, 225, 'Euro 6d', 76, 4000, 'Blanc', '2032-10-12', '2025-10-12', '2032-10-12', '2026-10-12'),
-- Iveco Turbo Bike (Deux roues - A) - ID Modele: 26
('2026AA00010', 'AA100AJ', '2023-05-30', '2023-05-30', 4, TRUE, 26, 'IVE2023M05000001', 250, 450, 'A', 'Essence', 998, 120, 80, 2, 0, 110, 'Euro 5', 98, 9000, 'Orange', '2033-05-30', '2026-05-30', '2033-05-30', '2027-05-30'),
-- Ford Fiesta (Automobile - B) - ID Modele: 33
('2026AA00011', 'AA100AK', '2020-12-01', '2020-12-01', 5, TRUE, 33, 'FOR2020M12000001', 1150, 1650, 'B', 'Essence', 999, 95, 7, 5, 0, 115, 'Euro 6d', 67, 5400, 'Vert', '2030-12-01', '2023-12-01', '2030-12-01', '2024-12-01'),
-- Ford Transit 470 (Camion léger - C) - ID Modele: 36
('2026AA00012', 'AA100AL', '2021-07-18', '2021-07-18', 6, TRUE, 36, 'FOR2021M07000001', 2800, 4700, 'C', 'Diesel', 1995, 170, 11, 3, 0, 245, 'Euro 6d', 77, 4200, 'Bleu', '2031-07-18', '2024-07-18', '2031-07-18', '2025-07-18');

