# 🚀 Guide de Démarrage Rapide - TimeWeaver Full Stack

## ✅ L'application est en cours de démarrage!

### 📋 Services en cours de lancement:

1. **Discovery Service (Eureka)** - Port 8761 ✓
2. **User Management Service** - Port 8081 (en attente...)
3. **AI Prediction Service** - Port 8082 (en attente...)
4. **Notification Service** - Port 8083 (en attente...)
5. **Time Tracking Service** - Port 8084 (en attente...)
6. **API Gateway** - Port 8080 (en attente...)
7. **Frontend Angular** - Port 4200 (en attente...)

---

## ⏱️ Temps d'attente estimé:

- **Services Backend**: ~2-3 minutes
- **Frontend Angular**: ~1 minute supplémentaire
- **Total**: ~3-4 minutes

---

## 🌐 URLs d'Accès (une fois démarrés):

### Application Principale
```
http://localhost:4200
```
**C'est votre application web avec le nouveau design premium!**

### Services Backend
```
API Gateway:        http://localhost:8080
Discovery (Eureka): http://localhost:8761
```

### Bases de Données H2
```
User Management:    http://localhost:8081/h2-console
Time Tracking:      http://localhost:8084/h2-console
```

**Paramètres de connexion H2:**
- JDBC URL (User): `jdbc:h2:file:./data/userdb`
- JDBC URL (Tracking): `jdbc:h2:file:./data/timetrackingdb`
- Username: `sa`
- Password: *(laisser vide)*

---

## 🎨 Fonctionnalités du Nouveau Design:

✨ **Thème Clair/Sombre**
- Cliquez sur le bouton 🌙/☀️ dans le header pour basculer

💎 **Effets Glassmorphisme**
- Cartes avec effet de verre dépoli
- Arrière-plans animés avec gradients

🎯 **Navigation Moderne**
- "Créer" - Créer une nouvelle tâche
- "Liste" - Voir toutes les tâches

📊 **Formulaires Améliorés**
- Emojis pour chaque champ
- Animations fluides
- Validation en temps réel

---

## 🔍 Vérification du Démarrage:

### Méthode 1: Vérifier les ports
```powershell
# Dans PowerShell
Test-NetConnection localhost -Port 8761  # Eureka
Test-NetConnection localhost -Port 8081  # User Management
Test-NetConnection localhost -Port 8084  # Time Tracking
Test-NetConnection localhost -Port 4200  # Frontend
```

### Méthode 2: Vérifier via navigateur
Ouvrez ces URLs et vérifiez qu'elles répondent:
- http://localhost:8761 (Eureka Dashboard)
- http://localhost:4200 (Application Frontend)

---

## 🛠️ Dépannage:

### Problème: Un service ne démarre pas
**Solution:**
1. Vérifiez les fenêtres PowerShell ouvertes
2. Regardez les logs d'erreur dans chaque fenêtre
3. Vérifiez que Java et Maven sont installés:
   ```powershell
   java -version
   mvn -version
   ```

### Problème: Port déjà utilisé
**Solution:**
1. Trouvez le processus qui utilise le port:
   ```powershell
   netstat -ano | findstr :8081
   ```
2. Arrêtez le processus ou changez le port dans `application.yml`

### Problème: Frontend ne compile pas
**Solution:**
1. Vérifiez que Node.js est installé:
   ```powershell
   node -version
   npm -version
   ```
2. Réinstallez les dépendances:
   ```powershell
   cd timeweaver-web
   npm install
   ```

---

## 🎯 Prochaines Étapes:

1. **Attendez 3-4 minutes** que tous les services démarrent
2. **Ouvrez votre navigateur** à http://localhost:4200
3. **Testez le nouveau design:**
   - Basculez entre thème clair/sombre
   - Créez une nouvelle tâche
   - Consultez la liste des tâches
4. **Explorez les bases de données** via H2 Console

---

## 📝 Commandes Utiles:

### Arrêter tous les services
Fermez toutes les fenêtres PowerShell qui ont été ouvertes par le script.

### Redémarrer l'application
```powershell
.\start-app.ps1
```

### Voir les logs d'un service
Les logs s'affichent dans chaque fenêtre PowerShell du service.

---

## 🎉 Profitez de TimeWeaver!

Votre application full stack moderne est maintenant en cours de démarrage avec:
- ✅ Architecture microservices
- ✅ Design premium avec glassmorphisme
- ✅ Thèmes clair/sombre
- ✅ Animations fluides
- ✅ Base de données H2 intégrée

**Bon développement! 🚀**
