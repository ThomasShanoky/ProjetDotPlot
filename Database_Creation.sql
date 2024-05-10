-- Creation de la base de donnees 

-- DROP TABLE Blast;
-- DROP TABLE Procaryotes;


CREATE TABLE IF NOT EXISTS Procaryotes(
    espece    TEXT UNIQUE,
    assembly  TEXT PRIMARY KEY,
    ftplink   TEXT,
    proteome  TEXT,
    cdsearch  TEXT
);


CREATE TABLE IF NOT EXISTS Blast(
    espece1   TEXT,
    espece2   TEXT,
    blastfile TEXT PRIMARY KEY,
    FOREIGN KEY(espece1) REFERENCES Procaryotes(espece),
    FOREIGN KEY(espece2) REFERENCES Procaryotes(espece)
);

