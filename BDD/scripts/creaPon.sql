-- Création de la table Moniteur
CREATE TABLE Moniteur (
    idMoniteur INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL
);



-- Création de la table Poney
CREATE TABLE `Poney` (
    `idPoney` INTEGER AUTO_INCREMENT,
    `nomPoney` VARCHAR(50),
    `charge_max` DECIMAL(5,2),
    PRIMARY KEY(`idPoney`)
);

-- Création de la table Adherent
CREATE TABLE Adherent (
    idAdherent INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    telephone VARCHAR(10),
    poids INT,
    cotisation BOOLEAN
);


-- Création de la table CoursProgramme
CREATE TABLE CoursProgramme (
    idCours INT AUTO_INCREMENT PRIMARY KEY,
    Duree INT CHECK (Duree <= 2),
    DateJour DATE NOT NULL,
    Semaine INT NOT NULL,
    Heure TIME NOT NULL,
    Prix DECIMAL(10,2) NOT NULL,
    Niveau VARCHAR(20) NOT NULL,
    NbPersonne INT CHECK (NbPersonne <= 10)
);


-- Création de la table CoursRealise avec la clé étrangère vers CoursProgramme
CREATE TABLE CoursRealise (
    idCoursRealise INT AUTO_INCREMENT PRIMARY KEY,
    DateJour DATE NOT NULL,
    Semaine INT NOT NULL,
    Mois INT NOT NULL,
    idCours INT NOT NULL,
    FOREIGN KEY (idCours) REFERENCES CoursProgramme(idCours)
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

CREATE TABLE User (
    idConnexion INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    role ENUM('adherent', 'moniteur', 'admin') NOT NULL
);


-- Permet de verifier que l'on peut faire une reservation

DELIMITER |

CREATE TRIGGER `before_insert_reserver`
BEFORE INSERT ON `Reserver`
FOR EACH ROW
BEGIN
    DECLARE adherent_poids DECIMAL(5,2);
    DECLARE poney_charge_max DECIMAL(5,2);
    DECLARE cotisation_valide BOOLEAN;

    SELECT poids, cotisation INTO adherent_poids, cotisation_valide FROM Adherent WHERE idAdherent = NEW.idAdherent;

    IF cotisation_valide = FALSE THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cotisation de l\'adhérent n\'est pas à jour.';
    END IF;

    SELECT charge_max INTO poney_charge_max FROM Poney WHERE idPoney = NEW.idPoney;

    IF adherent_poids > poney_charge_max THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le poids de l\'adhérent dépasse la charge maximale du poney.';
    END IF;

END |

DELIMITER ;

DELIMITER |

CREATE TRIGGER verif_moniteur_cours
BEFORE INSERT ON Anime
FOR EACH ROW
BEGIN
    DECLARE heureDebutCoursNew TIME;
    DECLARE heureFinCoursNew TIME;
    DECLARE moniteurConflit INTEGER;

    SELECT Heure, ADDTIME(Heure, SEC_TO_TIME(Duree * 3600)) INTO heureDebutCoursNew, heureFinCoursNew
    FROM CoursProgramme
    WHERE idCours = NEW.idCours;

    SELECT COUNT(*)
    INTO moniteurConflit
    FROM CoursProgramme cp
    JOIN CoursRealise cr ON cr.idCours = cp.idCours
    JOIN Anime a ON a.idCours = cr.idCoursRealise
    WHERE a.idMoniteur = NEW.idMoniteur
    AND cr.DateJour = (SELECT DateJour FROM CoursRealise WHERE idCoursRealise = NEW.idCours)
    AND (
        (heureDebutCoursNew BETWEEN cp.Heure AND ADDTIME(cp.Heure, SEC_TO_TIME(cp.Duree * 3600)))
        OR
        (heureFinCoursNew BETWEEN cp.Heure AND ADDTIME(cp.Heure, SEC_TO_TIME(cp.Duree * 3600)))
        OR
        (cp.Heure BETWEEN heureDebutCoursNew AND heureFinCoursNew)
    );

    IF moniteurConflit > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Un moniteur ne peut pas faire plusieurs cours en même temps.';
    END IF;

END|

DELIMITER ;

DELIMITER |

CREATE TRIGGER cours_plein
BEFORE INSERT ON Reserver
FOR EACH ROW
BEGIN
    DECLARE nbPersonneInscrite INTEGER;
    DECLARE nbPersonneTotale INTEGER;
    SELECT COUNT(idAdherent) INTO nbPersonneInscrite
    FROM Reserver NATURAL join CoursRealise
    WHERE idCoursRealise = NEW.idCoursRealise;
    
    SELECT NbPersonne INTO nbPersonneTotale
    FROM CoursProgramme
    WHERE idCours = NEW.idCoursRealise;

    IF nbPersonneInscrite >= nbPersonneTotale THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Le nombre d''adhérents inscrits est supérieur ou égal au nombre total de places disponibles.';
    END IF;
END |

DELIMITER ;

DELIMITER |

CREATE TRIGGER Poids_Trop_Lourd
BEFORE INSERT ON Reserver
FOR EACH ROW
BEGIN
    DECLARE poidsAdherent DECIMAL(5,2);
    DECLARE chargeMaxPoney DECIMAL(5,2);
    SELECT poids, charge_max INTO poidsAdherent, chargeMaxPoney 
    FROM Adherent NATURAL join Reserver NATURAL JOIN Poney WHERE idAdherent = NEW.idAdherent;

    IF poidsAdherent > chargeMaxPoney THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Le poids de l''adhérent dépasse la charge maximale du poney.';
    END IF;
END |
DELIMITER ;

DELIMITER |

DELIMITER |

CREATE TRIGGER Poney_repose
BEFORE INSERT ON Reserver
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;

    SELECT COUNT(*)
    INTO conflict_count
    FROM Reserver r
    JOIN CoursProgramme cr ON r.idCours = cr.idCours
    WHERE r.idPoney = NEW.idPoney
    AND cr.DateJour = (SELECT DateJour FROM CoursProgramme WHERE idCours = NEW.idCours)
    AND (
        TIMESTAMPADD(HOUR, 1, cr.Heure) > (SELECT Heure FROM CoursRealise WHERE idCoursRealise = NEW.idCoursRealise)
        OR TIMESTAMPADD(HOUR, -1, cr.Heure) < (SELECT Heure FROM CoursRealise WHERE idCoursRealise = NEW.idCoursRealise)
    );

    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Le poney est déjà réservé dans l\'heure précédente ou suivante.';
    END IF;
END |

DELIMITER ;


DELIMITER |

CREATE TRIGGER Cotisation_Pas_Payer
BEFORE INSERT ON Reserver
FOR EACH ROW
BEGIN
    DECLARE cotis BOOLEAN;

    SELECT cotisation INTO cotis
    FROM Adherent
    WHERE idAdherent = NEW.idAdherent;

    IF cotis = FALSE THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'L''adhérent n''a pas payé sa cotisation.';
    END IF;
END |

DELIMITER ;

