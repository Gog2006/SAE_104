USE carte_grise_db;

-- =========================
-- Propriétaire
-- =========================
CREATE TABLE proprietaire (
    id_proprietaire INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    adresse VARCHAR(255) NOT NULL
);

-- =========================
-- Catégorie de véhicule (D2)
-- =========================
CREATE TABLE categorie_vehicule (
    id_categorie INT AUTO_INCREMENT PRIMARY KEY,
    libelle ENUM('Deux roues', 'Automobile', 'Camion léger') NOT NULL
);

-- =========================
-- Marque (D1)
-- =========================
CREATE TABLE marque (
    id_marque INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

-- =========================
-- Modèle (D2.1)
-- =========================
CREATE TABLE modele (
    id_modele INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    id_marque INT NOT NULL,
    id_categorie INT NOT NULL,
    FOREIGN KEY (id_marque) REFERENCES marque(id_marque),
    FOREIGN KEY (id_categorie) REFERENCES categorie_vehicule(id_categorie)
);

-- =========================
-- Véhicule
-- =========================
CREATE TABLE vehicule (
    id_vehicule INT AUTO_INCREMENT PRIMARY KEY,
    immatriculation VARCHAR(9) NOT NULL UNIQUE, -- A
    date_premiere_immat DATE NOT NULL,          -- B
    numero_serie VARCHAR(30) NOT NULL UNIQUE,   -- E

    poids_vide INT NOT NULL,                     -- F1
    poids_charge INT NOT NULL,                   -- F2

    cylindree INT NOT NULL,                      -- P1
    puissance_ch INT NOT NULL,                   -- P2
    puissance_cv INT NOT NULL,                   -- P3

    places_assises INT NOT NULL,                 -- S1
    places_debout INT DEFAULT 0,                 -- S2

    bruit_db INT NOT NULL,                       -- U1
    regime_moteur INT NOT NULL,                  -- U2

    emission_co2 INT NOT NULL,                   -- V1
    classe_env ENUM('EURO 3','EURO 4','EURO 5','EURO 6') NOT NULL, -- V2

    id_modele INT NOT NULL,
    FOREIGN KEY (id_modele) REFERENCES modele(id_modele)
);

-- =========================
-- Carte grise
-- =========================
CREATE TABLE carte_grise (
    numero_carte_grise VARCHAR(20) PRIMARY KEY, -- 0
    date_delivrance DATE NOT NULL,               -- I
    date_fin_validite DATE NOT NULL,             -- H

    conducteur_proprietaire BOOLEAN NOT NULL,    -- C4

    categorie_permis ENUM('A1','A2','A','B','C') NOT NULL, -- J

    id_proprietaire INT NOT NULL,
    id_vehicule INT NOT NULL,

    FOREIGN KEY (id_proprietaire) REFERENCES proprietaire(id_proprietaire),
    FOREIGN KEY (id_vehicule) REFERENCES vehicule(id_vehicule)
);

-- =========================
-- Contrôle technique
-- =========================
CREATE TABLE controle_technique (
    id_controle INT AUTO_INCREMENT PRIMARY KEY,
    date_controle DATE NOT NULL,                 -- X1, X1.1, ...
    id_vehicule INT NOT NULL,
    FOREIGN KEY (id_vehicule) REFERENCES vehicule(id_vehicule)
        ON DELETE CASCADE
);

-- =========================
-- Index utiles
-- =========================
CREATE INDEX idx_nom_proprietaire ON proprietaire(nom);
CREATE INDEX idx_immat ON vehicule(immatriculation);
CREATE INDEX idx_date_cg ON carte_grise(date_delivrance);

