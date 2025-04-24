CREATE TABLE Annonce (
    id_annonce SERIAL PRIMARY KEY,
    Marque VARCHAR(100) NOT NULL,                         
    Modele VARCHAR(100) NOT NULL,                         
    Annee SMALLINT CHECK (Annee > 1900) NOT NULL,         
    Prix NUMERIC CHECK (Prix > 0) NOT NULL,               
    Kilometrage INTEGER CHECK (Kilometrage >= 0),
    Ville VARCHAR(100),                          
    type_carrosserie VARCHAR(100),               
    couleur_exterieure VARCHAR(255),             
    couleur_interieure VARCHAR(255),             
    transmission VARCHAR(100),                   
    moteur VARCHAR(100),                         
    carburant VARCHAR(50),                       
    nombre_porte INTEGER CHECK (nombre_porte >= 0),
    nombre_place INTEGER CHECK (nombre_place >= 0),
    vendue BOOLEAN DEFAULT FALSE,
    date_raffraichie TIMESTAMP,
    ancien_prix NUMERIC,
    plateforme VARCHAR,
    equipements TEXT,
    lien_annonce TEXT,                           
    url_image TEXT 
);

CREATE TABLE Modele (
    id_modele SERIAL PRIMARY KEY,
    marque VARCHAR,
    modele VARCHAR,
    annee VARCHAR(255),
    sous_modele VARCHAR(100),
    version_ VARCHAR(255),
    prix NUMERIC,
    consommation_modele VARCHAR(255),
    moteur_modele VARCHAR(255),
    puissance_modele INTEGER,
    transmission_modele VARCHAR(255),
    carrosserie_modele VARCHAR(100),
    nombre_porte INTEGER CHECK (nombre_porte >= 0),
    nombre_place INTEGER CHECK (nombre_place >= 0),
    lien_modele TEXT
);

ALTER TABLE "annonce"
ADD CONSTRAINT unique_annonce_entry
UNIQUE (marque, modele, annee, kilometrage, prix, ville, plateforme);

ALTER TABLE "modele"
ADD CONSTRAINT unique_modele_entry
UNIQUE (marque, modele, annee, sous_modele,version_, prix );