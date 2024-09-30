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
    `Telephone` VARCHAR(20) CHECK (Telephone REGEXP '^[0-9]{10}$'),
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
    `NbPersonne` INTEGER CHECK (`NbPersonne` <= 10),
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


-- Permet de verifier que l'on peut faire une reservation

DELIMITER $$

CREATE TRIGGER `before_insert_reserver`
BEFORE INSERT ON `Reserver`
FOR EACH ROW
BEGIN
    DECLARE adherent_poids DECIMAL(5,2);
    DECLARE poney_charge_max DECIMAL(5,2);
    DECLARE cotisation_valide BOOLEAN;

    -- Récupération du poids de l'adhérent
    SELECT poids, cotisation INTO adherent_poids, cotisation_valide FROM Adherent WHERE idAdherent = NEW.idAdherent;

    -- Vérification de la cotisation
    IF cotisation_valide = FALSE THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cotisation de l\'adhérent n\'est pas à jour.';
    END IF;

    -- Récupération de la charge maximale du poney
    SELECT charge_max INTO poney_charge_max FROM Poney WHERE idPoney = NEW.idPoney;

    -- Vérification du poids de l'adhérent par rapport à la charge maximale du poney
    IF adherent_poids > poney_charge_max THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le poids de l\'adhérent dépasse la charge maximale du poney.';
    END IF;

END$$

DELIMITER ;
