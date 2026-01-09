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

-- =========================
-- Create indexes for performance
-- =========================
CREATE INDEX idx_nom_proprietaire ON proprietaires(nom);
CREATE INDEX idx_immat ON cartes_grises(numero_immatriculation);
CREATE INDEX idx_numero_carte ON cartes_grises(numero_carte_grise);
CREATE INDEX idx_modele_marque ON modeles(marque_id);
