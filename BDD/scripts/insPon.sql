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
INSERT INTO `Adherent` (`poids`, `nom`, `cotisation`, `Telephone`, `prenom`) VALUES
(45.50, 'AuPays', TRUE, '0601020304', 'Alice'),
(52.00, 'Lenon', TRUE, '0605060708', 'Bob'),
(48.00, 'Charlotte', TRUE, '0608091011', 'Clara');

-- Insertion des données dans la table CoursProgramme
INSERT INTO `CoursProgramme` (`Duree`, `DateJour`, `Semaine`, `Heure`, `Prix`, `Niveau`, `NbPersonne`) VALUES
(2, '2023-11-15', 46, '10:00:00', 50.00, 'Débutant', 8),
(1, '2023-11-16', 46, '14:00:00', 75.00, 'Intermédiaire', 6),
(2, '2023-11-17', 46, '16:00:00', 40.00, 'Avancé', 4),
(2, '2025-01-07', 2, '10:00:00', 50.00, 'Débutant', 8),
(1, '2025-01-08', 2, '14:00:00', 75.00, 'Intermédiaire', 6),
(2, '2025-01-09', 2, '16:00:00', 40.00, 'Avancé', 4);
--  Pour vérifier le trigger moniteur verif_cours (4, '2023-11-15', 46, '10:00:00', 50.00, 'Débutant', 8);

-- Insertion des données dans la table CoursRealise
INSERT INTO `CoursRealise` (`DateJour`, `Semaine`, `Mois`, `idCours`) VALUES
('2023-11-15', 46, 11, 1),
('2023-11-16', 46, 11, 2),
('2023-11-17', 46, 11, 3);
--  pour vérifier le trigger moniteur verif_cours('2023-11-15', 46, 11, 4);

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


INSERT INTO User (username, password, nom, prenom, role) 
VALUES ('admin', 'admin', 'admin', 'admin', 'admin');

