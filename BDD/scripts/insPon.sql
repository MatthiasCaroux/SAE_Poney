-- Insertion des données dans la table Moniteur
INSERT INTO `Moniteur` (`Prenom`, `nom`) VALUES
('Jean', 'Dupont'),
('Marie', 'Durand'),
('Pierre', 'Martin');

-- Insertion des données dans la table Poney
INSERT INTO `Poney` (`nomPoney`, `charge_max`) VALUES
('Bella', 50.00),
('Charlie', 55.00),
('Daisy', 60.00),
('Max', 65.00),
('Luna', 55.00),
('Rocky', 70.00),
('Misty', 50.00),
('Penny', 45.00),
('Rex', 75.00),
('Coco', 60.00),
('Sasha', 65.00);

-- Insertion des données dans la table Adherent
INSERT INTO `Adherent` (`poids`, `nom`, `cotisation`, `Telephone`, `prenom`) VALUES
(45.50, 'AuPays', TRUE, '0601020304', 'Alice'),
(52.00, 'Lenon', TRUE, '0605060708', 'Bob'),
(48.00, 'Charlotte', TRUE, '0608091011', 'Clara'),
(60.00, 'Dupont', TRUE, '0612345678', 'David'),
(55.50, 'Durand', TRUE, '0612341234', 'Eve'),
(62.00, 'Martin', TRUE, '0609876543', 'Félix'),
(57.00, 'Benoit', TRUE, '0612345679', 'Géraldine'),
(50.50, 'Lemoine', TRUE, '0601112233', 'Hélène'),
(49.00, 'Caron', TRUE, '0622334455', 'Isabelle'),
(53.00, 'Robert', TRUE, '0633445566', 'Julien'),
(58.00, 'Meunier', TRUE, '0644556677', 'Kévin'),
(61.00, 'Moulin', TRUE, '0655667788', 'Laura'),
(59.00, 'Dufresne', TRUE, '0666778899', 'Mélissa'),
(56.00, 'Leclerc', TRUE, '0677889900', 'Nathalie'),
(54.00, 'Bernard', TRUE, '0688990011', 'Olivier');


-- Insertion des données dans la table CoursProgramme
INSERT INTO `CoursProgramme` (`Duree`, `DateJour`, `Semaine`, `Heure`, `Prix`, `Niveau`, `NbPersonne`) VALUES
(2, '2023-11-15', 46, '10:00:00', 50.00, 'Débutant', 8),
(1, '2023-11-16', 46, '14:00:00', 75.00, 'Intermédiaire', 6),
(2, '2023-11-17', 46, '16:00:00', 40.00, 'Avancé', 4),
(2, '2025-01-07', 2, '10:00:00', 50.00, 'Débutant', 8),
(1, '2025-01-08', 2, '14:00:00', 75.00, 'Intermédiaire', 6),
(2, '2025-01-09', 2, '16:00:00', 40.00, 'Avancé', 4),
(2, '2025-01-14', 3, '10:00:00', 50.00, 'Débutant', 8);
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

INSERT INTO User (username, password, nom, prenom, role) 
VALUES ('anotheruser', 'anotherpass', 'Another', 'User', 'adherent');


