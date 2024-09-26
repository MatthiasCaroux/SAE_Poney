CREATE TABLE `Moniteur` (
	`idMoniteur` INTEGER AUTO_INCREMENT,
	`Prenom` VARCHAR(50),
	`nom` VARCHAR(50),
	PRIMARY KEY(`idMoniteur`)
);


CREATE TABLE `Poney` (
	`idPoney` INTEGER AUTO_INCREMENT,
	`nomPoney` VARCHAR(50),
	`charge_max` DECIMAL(5,2),
	PRIMARY KEY(`idPoney`)
);


CREATE TABLE `Adherent` (
	`idAdherent` INTEGER AUTO_INCREMENT,
	`poids` DECIMAL(5,2),
	`nom` VARCHAR(50),
	`cotisation` BOOLEAN,
	`Telephone` VARCHAR(20),
	PRIMARY KEY(`idAdherent`)
);


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


CREATE TABLE `CoursRealise` (
	`idCoursRealise` INTEGER AUTO_INCREMENT,
	`DateJour` DATE NOT NULL,
	`Semaine` INTEGER,
	`Mois` INTEGER,
	`idCours` INTEGER,
	PRIMARY KEY(`idCoursRealise`)
);


CREATE TABLE `Reserver` (
	`idCoursRealise` INTEGER AUTO_INCREMENT,
	`idAdherent` INTEGER,
	`idPoney` INTEGER,
	`idReserver` INTEGER,
	PRIMARY KEY(`idCoursRealise`, `idAdherent`, `idPoney`, `idReserver`)
);


CREATE TABLE `Anime` (
	`idMoniteur` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`idCours` INTEGER NOT NULL AUTO_INCREMENT,
	PRIMARY KEY(`idMoniteur`, `idCours`)
);


ALTER TABLE `CoursRealise`
ADD FOREIGN KEY(`idCours`) REFERENCES `CoursProgramme`(`idCours`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Reserver`
ADD FOREIGN KEY(`idAdherent`) REFERENCES `Adherent`(`idAdherent`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Reserver`
ADD FOREIGN KEY(`idPoney`) REFERENCES `Poney`(`idPoney`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Reserver`
ADD FOREIGN KEY(`idCoursRealise`) REFERENCES `CoursRealise`(`idCoursRealise`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Moniteur`
ADD FOREIGN KEY(`idMoniteur`) REFERENCES `Anime`(`idMoniteur`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `Anime`
ADD FOREIGN KEY(`idCours`) REFERENCES `CoursRealise`(`idCoursRealise`)
ON UPDATE NO ACTION ON DELETE NO ACTION;