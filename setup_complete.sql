-- Complete database setup for Carte Grise application
-- Creates database and all tables with initial data

-- =========================
-- Create Database
-- =========================
CREATE DATABASE IF NOT EXISTS carte_grise_db;
USE carte_grise_db;

-- =========================
-- Drop existing tables if they exist (in correct order due to foreign keys)
-- =========================
DROP TABLE IF EXISTS cartes_grises;
DROP TABLE IF EXISTS modeles;
DROP TABLE IF EXISTS marques;
DROP TABLE IF EXISTS categories_vehicule;
DROP TABLE IF EXISTS proprietaires;
DROP TABLE IF EXISTS controle_technique;
DROP TABLE IF EXISTS vehicule;
DROP TABLE IF EXISTS carte_grise;
DROP TABLE IF EXISTS modele;
DROP TABLE IF EXISTS marque;
DROP TABLE IF EXISTS categorie_vehicule;
DROP TABLE IF EXISTS proprietaire;

-- =========================
-- Categories de vehicule
-- =========================
CREATE TABLE categories_vehicule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE
);

-- =========================
-- Marques
-- =========================
CREATE TABLE marques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    numero_fabricant VARCHAR(10) NOT NULL UNIQUE
);

-- =========================
-- Modeles
-- =========================
CREATE TABLE modeles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modele VARCHAR(100) NOT NULL,
    marque_id INT NOT NULL,
    categorie_id INT NOT NULL,
    type_vehicule VARCHAR(50) NOT NULL,
    FOREIGN KEY (marque_id) REFERENCES marques(id),
    FOREIGN KEY (categorie_id) REFERENCES categories_vehicule(id)
);

-- =========================
-- Proprietaires
-- =========================
CREATE TABLE proprietaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    adresse VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    poids_vide_kg INT,
    poids_max_kg INT,
    categorie_permis VARCHAR(5),
    cylindree_cm3 INT,
    puissance_chevaux INT,
    places_assises INT,
    emission_co2_g_km INT,
    classe_environnementale VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proprietaire_id) REFERENCES proprietaires(id),
    FOREIGN KEY (modele_id) REFERENCES modeles(id)
);

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

INSERT INTO cartes_grises (numero_carte_grise, numero_immatriculation, date_premiere_immat, date_immat_actuelle, proprietaire_id, est_conducteur, modele_id, numero_serie, poids_vide_kg, poids_max_kg, categorie_permis, cylindree_cm3, puissance_chevaux, places_assises, emission_co2_g_km) VALUES
-- Honda Civic (Automobile - B) - ID Modele: 3
('2026AA00001', 'AB 100 CD', '2020-05-12', '2020-05-12', 1, TRUE, 3, 'HON2020M05000001', 1300, 1800, 'B', 1498, 182, 5, 128),
-- Honda CB500F (Deux roues - A2) - ID Modele: 1
('2026AA00002', 'AB 101 CD', '2021-06-15', '2021-06-15', 2, TRUE, 1, 'HON2021M06000001', 190, 370, 'A2', 471, 48, 2, 80),
-- Peugeot 208 (Automobile - B) - ID Modele: 9
('2026AA00003', 'PE 200 UG', '2022-03-20', '2022-03-20', 3, TRUE, 9, 'PEU2022M03000001', 1050, 1550, 'B', 1199, 100, 5, 102),
-- Peugeot Boxer 440 (Camion léger - C) - ID Modele: 11
('2026AA00004', 'PE 201 UG', '2021-11-05', '2021-11-05', 4, TRUE, 11, 'PEU2021M11000001', 2100, 4400, 'C', 2179, 140, 3, 230),
-- Renault Clio (Automobile - B) - ID Modele: 15
('2026AB00005', 'RE 300 NA', '2023-01-10', '2023-01-10', 5, TRUE, 15, 'REN2023M01000001', 1100, 1600, 'B', 999, 90, 5, 110),
-- Renault Master (Camion léger - C) - ID Modele: 17
('2026AB00006', 'RE 301 NA', '2020-08-22', '2020-08-22', 6, TRUE, 17, 'REN2020M08000001', 2200, 3500, 'C', 2299, 135, 3, 240),
-- Mercedes Classe A (Automobile - B) - ID Modele: 21
('2026AC00007', 'ME 400 RZ', '2024-04-15', '2024-04-15', 1, TRUE, 21, 'MER2024M04000001', 1400, 1950, 'B', 1332, 140, 5, 130),
-- Mercedes Sprinter 5t (Camion léger - C) - ID Modele: 23
('2026AC00008', 'ME 401 RZ', '2021-02-28', '2021-02-28', 2, TRUE, 23, 'MER2021M02000001', 2600, 5000, 'C', 2143, 163, 3, 215),
-- Iveco Daily 35C (Camion léger - C) - ID Modele: 29
('2026AD00009', 'IV 500 CO', '2022-10-12', '2022-10-12', 3, TRUE, 29, 'IVE2022M10000001', 2200, 3500, 'C', 2998, 160, 3, 225),
-- Iveco Turbo Bike (Deux roues - A) - ID Modele: 26
('2026AD00010', 'IV 501 CO', '2023-05-30', '2023-05-30', 4, TRUE, 26, 'IVE2023M05000001', 250, 450, 'A', 998, 120, 2, 110),
-- Ford Fiesta (Automobile - B) - ID Modele: 33
('2026AE00011', 'FO 600 RD', '2020-12-01', '2020-12-01', 5, TRUE, 33, 'FOR2020M12000001', 1150, 1650, 'B', 999, 95, 5, 115),
-- Ford Transit 470 (Camion léger - C) - ID Modele: 36
('2026AE00012', 'FO 601 RD', '2021-07-18', '2021-07-18', 6, TRUE, 36, 'FOR2021M07000001', 2800, 4700, 'C', 1995, 170, 3, 245);



-- =========================
-- Create indexes for performance
-- =========================
CREATE INDEX idx_nom_proprietaire ON proprietaires(nom);
CREATE INDEX idx_immat ON cartes_grises(numero_immatriculation);
CREATE INDEX idx_numero_carte ON cartes_grises(numero_carte_grise);
CREATE INDEX idx_modele_marque ON modeles(marque_id);
