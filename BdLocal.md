## Documentation d'installation et de configuration de la base de données pour le projet (Utilisation Locale)

### **Important**
- **Ce document est destiné aux utilisateurs qui souhaitent exécuter le projet en local sur leur machine personnelle.**
- **Si vous êtes à l'IUT, cette configuration n'est pas nécessaire.** Le projet est déjà configuré pour fonctionner avec la base de données hébergée sur le serveur de l'université.

---

### Étape 1 : Installer MySQL/MariaDB
1. **Installer MySQL/MariaDB sur votre machine** :
   - Sous Linux (Debian/Ubuntu) :
     ```bash
     sudo apt update
     sudo apt install mariadb-server
     ```

2. **Démarrer le service MySQL** :
   ```bash
   sudo service mysql start
   ```

---

### Étape 2 : Configurer l'utilisateur `root` avec un mot de passe
1. **Connectez-vous à MySQL en tant qu'administrateur** :
   ```bash
   sudo mysql -u root
   ```

2. **Définir un mot de passe pour l'utilisateur `root`** :
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'matthias1';
   FLUSH PRIVILEGES;
   ```

3. **Quittez MySQL** :
   ```sql
   EXIT;
   ```

4. **Tester la connexion avec le nouveau mot de passe** :
   ```bash
   mysql -u root -p
   ```
   Saisissez `matthias1` comme mot de passe.

---

### Étape 3 : Créer la base de données locale
1. **Connectez-vous à MySQL avec l'utilisateur `root`** :
   ```bash
   mysql -u root -p
   ```

2. **Créer la base de données `sae_poney`** :
   ```sql
   CREATE DATABASE sae_poney;
   ```

3. **Vérifiez que la base de données a été créée** :
   ```sql
   SHOW DATABASES;
   ```

---

### Étape 4 : Importer les données dans la base
1. **Accédez au dossier contenant les scripts SQL** :
   ```bash
   cd BDD/script
   ```

2. **Importer les scripts dans la base `sae_poney`** :
   ```bash
   mysql -u root -p sae_poney < crePon.sql
   mysql -u root -p sae_poney < insPon.sql
   ```

3. **Vérifiez que les tables ont été créées avec succès** :
   ```bash
   mysql -u root -p
   USE sae_poney;
   SHOW TABLES;
   ```

---

### Étape 5 : Configurer Flask pour une utilisation locale
1. Ouvrez le fichier Flask où la configuration de la base de données est définie.
2. Assurez-vous que la configuration suivante est utilisée pour la base locale :
   ```python
   app.config['MYSQL_HOST'] = 'localhost'
   app.config['MYSQL_USER'] = 'root'
   app.config['MYSQL_PASSWORD'] = 'matthias1'
   app.config['MYSQL_DB'] = 'sae_poney'
   app.config['SECRET_KEY'] = 'secret'
   ```

---

### Étape 6 : Lancer le projet
1. Activez l'environnement virtuel Python :
   ```bash
   source venv/bin/activate
   ```

2. Installez les dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancez l'application Flask :
   ```bash
   flask run --debug
   ```

4. Accédez à l'application dans votre navigateur :
   ```
   http://127.0.0.1:5000
   ```

---

### Rappel important
- **Utilisation locale :** Cette configuration est exclusivement destinée à ceux qui exécutent le projet sur leur propre machine.
- **À l'IUT :** Cette configuration n'est pas nécessaire, car le projet est déjà configuré pour fonctionner avec la base de données du serveur de l'université.