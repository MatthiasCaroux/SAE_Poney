-- Suppression des tables si elles existent déjà pour éviter les conflits
DROP TABLE IF EXISTS `Anime`;
DROP TABLE IF EXISTS `Reserver`;
DROP TABLE IF EXISTS `CoursRealise`;
DROP TABLE IF EXISTS `CoursProgramme`;
DROP TABLE IF EXISTS `Adherent`;
DROP TABLE IF EXISTS `Poney`;
DROP TABLE IF EXISTS `Moniteur`;

-- Création de la table Moniteur
CREATE TABLE `Moniteur` (
    `idMoniteur` INTEGER AUTO_INCREMENT,
    `Prenom` VARCHAR(50),
    `nom` VARCHAR(50),
    PRIMARY KEY(`idMoniteur`)
);

-- Création de la table Poney
CREATE TABLE `Poney` (
    `idPoney` INTEGER AUTO_INCREMENT,
    `nomPoney` VARCHAR(50),
    `charge_max` DECIMAL(5,2),
    PRIMARY KEY(`idPoney`)
);

-- Création de la table Adherent
CREATE TABLE `Adherent` (
    `idAdherent` INTEGER AUTO_INCREMENT,
    `poids` DECIMAL(5,2),
    `nom` VARCHAR(50),
    `cotisation` BOOLEAN,
    `Telephone` VARCHAR(20),
    PRIMARY KEY(`idAdherent`)
);

-- Création de la table CoursProgramme
CREATE TABLE `CoursProgramme` (
    `idCours` INTEGER AUTO_INCREMENT,
    `Duree` INTEGER,
    `DateJour` DATE,
    `Semaine` INTEGER,
    `Heure` TIME,
    `Prix` DECIMAL(10,2),
    `Niveau` VARCHAR(20),
    `NbPersonne` INTEGER,
    PRIMARY KEY(`idCours`)
);

-- Création de la table CoursRealise avec la clé étrangère vers CoursProgramme
CREATE TABLE `CoursRealise` (
    `idCoursRealise` INTEGER AUTO_INCREMENT,
    `DateJour` DATE NOT NULL,
    `Semaine` INTEGER,
    `Mois` INTEGER,
    `idCours` INTEGER,
    PRIMARY KEY(`idCoursRealise`),
    FOREIGN KEY(`idCours`) REFERENCES `CoursProgramme`(`idCours`) ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Création de la table Reserver avec les clés étrangères
CREATE TABLE `Reserver` (
    `idReserver` INTEGER AUTO_INCREMENT,
    `idCoursRealise` INTEGER,
    `idAdherent` INTEGER,
    `idPoney` INTEGER,
    PRIMARY KEY(`idReserver`),
    FOREIGN KEY(`idCoursRealise`) REFERENCES `CoursRealise`(`idCoursRealise`) ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY(`idAdherent`) REFERENCES `Adherent`(`idAdherent`) ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY(`idPoney`) REFERENCES `Poney`(`idPoney`) ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Création de la table Anime avec les clés étrangères
CREATE TABLE `Anime` (
    `idMoniteur` INTEGER NOT NULL,
    `idCours` INTEGER NOT NULL,
    PRIMARY KEY(`idMoniteur`, `idCours`),
    FOREIGN KEY(`idMoniteur`) REFERENCES `Moniteur`(`idMoniteur`) ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY(`idCours`) REFERENCES `CoursRealise`(`idCoursRealise`) ON UPDATE NO ACTION ON DELETE NO ACTION
);

-- Insertion des données dans la table Moniteur
INSERT INTO `Moniteur` (`Prenom`, `nom`) VALUES
('Jean', 'Dupont'),
('Marie', 'Durand'),
('Pierre', 'Martin');

-- Insertion des données dans la table Poney
INSERT INTO `Poney` (`nomPoney`, `charge_max`) VALUES
('Bella', 50.00),
('Charlie', 55.00),
('Daisy', 60.00);

-- Insertion des données dans la table Adherent
INSERT INTO `Adherent` (`poids`, `nom`, `cotisation`, `Telephone`) VALUES
(45.50, 'Alice', TRUE, '0601020304'),
(52.00, 'Bob', FALSE, '0605060708'),
(48.00, 'Clara', TRUE, '0608091011');

-- Insertion des données dans la table CoursProgramme
INSERT INTO `CoursProgramme` (`Duree`, `DateJour`, `Semaine`, `Heure`, `Prix`, `Niveau`, `NbPersonne`) VALUES
(2, '2023-11-15', 46, '10:00:00', 50.00, 'Débutant', 8),
(3, '2023-11-16', 46, '14:00:00', 75.00, 'Intermédiaire', 6),
(1, '2023-11-17', 46, '16:00:00', 40.00, 'Avancé', 4);

-- Insertion des données dans la table CoursRealise
INSERT INTO `CoursRealise` (`DateJour`, `Semaine`, `Mois`, `idCours`) VALUES
('2023-11-15', 46, 11, 1),
('2023-11-16', 46, 11, 2),
('2023-11-17', 46, 11, 3);

-- Insertion des données dans la table Reserver
INSERT INTO `Reserver` (`idCoursRealise`, `idAdherent`, `idPoney`) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 1, 3),
(2, 3, 1),
(3, 2, 2),
(3, 3, 3);

-- Insertion des données dans la table Anime
INSERT INTO `Anime` (`idMoniteur`, `idCours`) VALUES
(1, 1),
(2, 2),
(3, 3);
