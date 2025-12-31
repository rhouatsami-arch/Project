# 🗄️ Guide d'Accès aux Bases de Données H2

## 📋 Vue d'ensemble

Votre application TimeWeaver utilise des bases de données H2 pour chaque microservice. Voici comment y accéder.

## 🌐 Accès via Console Web H2

### **1. Time Tracking Service (Port 8084)**

**URL de la console:** http://localhost:8084/h2-console

**Paramètres de connexion:**
- **JDBC URL:** `jdbc:h2:file:./data/timetrackingdb`
- **Username:** `sa`
- **Password:** *(laisser vide)*
- **Driver Class:** `org.h2.Driver`

**Tables principales:**
- `TASK` - Toutes les tâches
- `TIME_ENTRY` - Entrées de temps
- `PREDICTION` - Prédictions AI

---

### **2. User Management Service (Port 8081)**

**URL de la console:** http://localhost:8081/h2-console

**Paramètres de connexion:**
- **JDBC URL:** `jdbc:h2:file:./data/userdb`
- **Username:** `sa`
- **Password:** *(laisser vide)*
- **Driver Class:** `org.h2.Driver`

**Tables principales:**
- `USERS` - Utilisateurs
- `ROLES` - Rôles
- `USER_ROLES` - Association utilisateurs-rôles

---

## 🚀 Démarrage des Services

Pour accéder aux bases de données, les services doivent être démarrés:

```powershell
# Démarrer tous les services avec Docker Compose
cd "c:\Users\User\Downloads\saad ouarch"
docker-compose up -d

# OU démarrer individuellement (sans Docker)
# Terminal 1 - Discovery Service
cd discovery-service
mvn spring-boot:run

# Terminal 2 - User Management Service
cd user-management-service
mvn spring-boot:run

# Terminal 3 - Time Tracking Service
cd time-tracking-service
mvn spring-boot:run
```

---

## 📊 Requêtes SQL Utiles

### **Voir toutes les tâches**
```sql
SELECT * FROM TASK ORDER BY CREATED_AT DESC;
```

### **Voir les utilisateurs**
```sql
SELECT * FROM USERS;
```

### **Statistiques des tâches par statut**
```sql
SELECT STATUS, COUNT(*) as COUNT 
FROM TASK 
GROUP BY STATUS;
```

### **Tâches avec leur temps prédit vs réel**
```sql
SELECT 
    TITLE,
    PREDICTED_MINUTES,
    ACTUAL_MINUTES,
    STATUS
FROM TASK
WHERE ACTUAL_MINUTES IS NOT NULL;
```

### **Voir les prédictions AI**
```sql
SELECT * FROM PREDICTION ORDER BY CREATED_AT DESC;
```

---

## 🔧 Accès Direct aux Fichiers de Base de Données

Les fichiers de base de données H2 sont stockés dans:

```
c:\Users\User\Downloads\saad ouarch\data\
├── timetrackingdb.mv.db  (Time Tracking DB)
├── userdb.mv.db          (User Management DB)
└── *.trace.db            (Fichiers de trace)
```

---

## 🛠️ Option Alternative: Outil DBeaver

Vous pouvez aussi utiliser **DBeaver** (gratuit) pour une interface plus riche:

1. **Télécharger:** https://dbeaver.io/download/
2. **Installer** DBeaver Community Edition
3. **Créer une connexion:**
   - Type: H2 Embedded
   - Path: `c:\Users\User\Downloads\saad ouarch\data\timetrackingdb`
   - Username: `sa`
   - Password: *(vide)*

---

## ⚠️ Notes Importantes

1. **Services doivent être démarrés** pour accéder via console web
2. **Un seul accès à la fois** - H2 en mode fichier ne supporte pas les connexions multiples simultanées
3. **Sauvegarde recommandée** avant modifications importantes
4. **Mode AUTO_SERVER** activé pour permettre plusieurs connexions

---

## 🔍 Vérification Rapide

Pour vérifier que tout fonctionne:

```powershell
# Vérifier que les services sont démarrés
curl http://localhost:8081/actuator/health  # User Management
curl http://localhost:8084/actuator/health  # Time Tracking

# Accéder aux consoles
start http://localhost:8081/h2-console
start http://localhost:8084/h2-console
```

---

## 📞 Ports des Services

| Service | Port | Console H2 |
|---------|------|------------|
| Discovery Service | 8761 | N/A |
| User Management | 8081 | http://localhost:8081/h2-console |
| AI Prediction | 8082 | N/A |
| Notification | 8083 | N/A |
| Time Tracking | 8084 | http://localhost:8084/h2-console |
| API Gateway | 8080 | N/A |

---

**Dernière mise à jour:** 2025-12-24
