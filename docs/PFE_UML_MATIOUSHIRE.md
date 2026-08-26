# MatiousHire — Modélisation UML (PFE 2026)
## Diagrammes pour soutenance jury — Matious Digital × EMSI

> **Usage :** fichiers `.puml` prêts dans [`uml/`](uml/) — voir [`uml/README.md`](uml/README.md) pour export PNG / StarUML / draw.io.

---

## 1. Vue d'ensemble des diagrammes

### Architecture (PlantUML — dossier `uml/`)

| Fichier | Diagramme | Slide PFE |
|---------|-----------|-----------|
| `00_architecture_overview.puml` | Vue d'ensemble système | Slide 19 |
| `09_architecture_layers.puml` | **Architecture 6 couches** | Slide 19 |
| `10_architecture_context.puml` | Contexte (acteurs + Matious Digital) | Slide 4/19 |
| `11_architecture_packages.puml` | Packages backend/frontend | Annexe |
| `12_architecture_ia_module.puml` | Module IA interne | Slide 20 |
| `13_architecture_data_flow.puml` | Flux de données | Slide 20 |
| `14_architecture_frontend.puml` | Architecture Next.js | Slide 6 |
| `06_components.puml` | Composants (simplifié) | Slide 19 |
| `07_deployment.puml` | Déploiement | Slide 25 |

### UML métier & séquences

| Diagramme UML | Objectif jury | Slide PFE |
|---------------|-------------|-----------|
| **Cas d'utilisation** | Acteurs + fonctionnalités | Slide 22 |
| **Classes** | Modèle de données métier | Slide 21 |
| **Séquence — Recommandation IA** | Flux matching ML/NLP | Slide 20 / démo |
| **Séquence — Upload CV** | Flux couche données | Slide 33 |
| **Séquence — Classement recruteur** | Pipeline RH | Slide 31 |
| **Activité — Pipeline IA** | Scoring 6 critères | Slide 20 |

---

## 2. Diagramme de cas d'utilisation

### 2.1 Description textuelle

**Acteurs principaux :**
- **Étudiant** — profil académique, stages observation/opérationnel
- **Candidat** — profil professionnel, stage fonctionnel 4–6 mois
- **Recruteur** — gestion offres et pipeline candidats
- **Administrateur** — supervision plateforme
- **Système IA** — acteur secondaire (matching, LLM, extraction CV)

**Packages fonctionnels :**
1. Authentification  
2. Gestion profil & CV  
3. Offres & candidatures  
4. Matching & recommandations IA  
5. Entretiens & notifications  
6. Administration & audit  

### 2.2 Diagramme (Mermaid)

```mermaid
flowchart TB
    subgraph Auth["Package Authentification"]
        UC1[S'inscrire]
        UC2[Se connecter]
    end

    subgraph Profil["Package Profil & CV"]
        UC3[Gérer profil]
        UC4[Uploader CV]
        UC5[Consulter texte extrait]
    end

    subgraph Offres["Package Offres"]
        UC6[Consulter offres]
        UC7[Publier offre]
        UC8[Postuler]
        UC9[Sauvegarder offre]
    end

    subgraph IA["Package Matching IA"]
        UC10[Obtenir recommandations]
        UC11[Calculer score compatibilité]
        UC12[Classer candidats]
        UC13[Consulter explication LLM]
    end

    subgraph Entretiens["Package Entretiens"]
        UC14[Planifier entretien]
        UC15[Gérer disponibilités]
        UC16[Confirmer / Refuser entretien]
    end

    subgraph AdminPkg["Package Administration"]
        UC17[Consulter dashboard]
        UC18[Gérer utilisateurs]
        UC19[Consulter audit logs]
    end

    Etudiant((Étudiant))
    Candidat((Candidat))
    Recruteur((Recruteur))
    Admin((Administrateur))
    SysIA((Système IA))

    Etudiant --> UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC8 & UC9 & UC10 & UC13 & UC15 & UC16
    Candidat --> UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC8 & UC9 & UC10 & UC13 & UC15 & UC16
    Recruteur --> UC2 & UC7 & UC12 & UC14 & UC16
    Admin --> UC2 & UC17 & UC18 & UC19

    UC4 -.-> SysIA
    UC10 -.-> SysIA
    UC11 -.-> SysIA
    UC12 -.-> SysIA
    UC13 -.-> SysIA
```

### 2.3 PlantUML (pour export figure)

```plantuml
@startuml MatiousHire_UseCase
left to right direction
skinparam packageStyle rectangle

actor "Étudiant" as ET
actor "Candidat" as CA
actor "Recruteur" as RE
actor "Administrateur" as AD
actor "Système IA" as IA <<system>>

rectangle "MatiousHire" {
  package "Authentification" {
    usecase "S'inscrire" as UC1
    usecase "Se connecter" as UC2
  }
  package "Profil & CV" {
    usecase "Gérer profil" as UC3
    usecase "Uploader CV" as UC4
    usecase "Consulter CV extrait" as UC5
  }
  package "Offres & candidatures" {
    usecase "Consulter offres" as UC6
    usecase "Publier offre" as UC7
    usecase "Postuler" as UC8
    usecase "Sauvegarder offre" as UC9
  }
  package "Matching IA" {
    usecase "Recommandations IA" as UC10
    usecase "Calculer score" as UC11
    usecase "Classer candidats" as UC12
    usecase "Explication LLM" as UC13
  }
  package "Entretiens" {
    usecase "Planifier entretien" as UC14
    usecase "Gérer disponibilités" as UC15
    usecase "Confirmer/Refuser" as UC16
  }
  package "Administration" {
    usecase "Dashboard admin" as UC17
    usecase "Gérer utilisateurs" as UC18
    usecase "Audit logs" as UC19
  }
}

ET --> UC1
ET --> UC3
ET --> UC4
ET --> UC6
ET --> UC8
ET --> UC10
CA --> UC1
CA --> UC3
CA --> UC4
CA --> UC8
CA --> UC10
RE --> UC7
RE --> UC12
RE --> UC14
AD --> UC17
AD --> UC18
AD --> UC19

UC4 ..> IA : <<include>>
UC10 ..> UC11 : <<include>>
UC10 ..> IA
UC12 ..> UC11 : <<include>>
UC13 ..> IA

@enduml
```

### 2.4 Table des cas d'utilisation (fiche jury)

| ID | Cas d'utilisation | Acteur | Précondition | Postcondition |
|----|-------------------|--------|--------------|---------------|
| UC01 | S'inscrire | Étudiant/Candidat/Recruteur | Email non utilisé | Compte créé + audit log |
| UC04 | Uploader CV | Étudiant/Candidat | Connecté | Fichier stocké + texte extrait |
| UC08 | Postuler | Étudiant/Candidat | Profil complet | Application créée |
| UC10 | Recommandations IA | Étudiant/Candidat | Profil + offres ouvertes | Liste triée par score + historique |
| UC12 | Classer candidats | Recruteur | Offre + candidatures | Pipeline trié + match_score |
| UC13 | Explication LLM | Étudiant/Candidat | Job_id valide | Texte explicatif affiché |
| UC19 | Audit logs | Admin | Connecté admin | Liste filtrée des actions |

---

## 3. Diagramme de classes

### 3.1 Description

Modèle **domaine métier** aligné sur SQLAlchemy (`app/models/`).  
`Student` porte les profils **étudiant** et **candidat** via `account_kind`.

### 3.2 Diagramme (Mermaid)

```mermaid
classDiagram
    class Student {
        +UUID id
        +String email
        +String hashed_password
        +String first_name
        +String last_name
        +String technical_skills
        +String cv_filename
        +String cv_path
        +Text cv_extracted_text
        +DateTime cv_extracted_at
        +String account_kind
        +DateTime created_at
    }

    class Recruiter {
        +UUID id
        +String email
        +String company_name
        +String first_name
        +String last_name
    }

    class Admin {
        +UUID id
        +String email
        +String first_name
        +String last_name
    }

    class Job {
        +Integer id
        +UUID recruiter_id
        +String title
        +Text description
        +String required_skills
        +String location
        +Enum status
    }

    class Application {
        +Integer id
        +UUID student_id
        +Integer job_id
        +Enum status
        +Integer match_score
        +Text cover_letter
    }

    class SavedJob {
        +Integer id
        +UUID student_id
        +Integer job_id
    }

    class Meeting {
        +Integer id
        +Integer application_id
        +UUID recruiter_id
        +UUID student_id
        +DateTime scheduled_at
        +String status
    }

    class RecommendationHistory {
        +Integer id
        +UUID student_id
        +Integer job_id
        +Integer compatibility_score
        +Text explanation
        +DateTime created_at
    }

    class AuditLog {
        +Integer id
        +String actor_email
        +String actor_role
        +String action
        +String resource
        +Text details
        +DateTime created_at
    }

    class Notification {
        +Integer id
        +String user_email
        +Enum type
        +String title
        +Boolean is_read
    }

    Recruiter "1" --> "*" Job : publie
    Student "1" --> "*" Application : soumet
    Job "1" --> "*" Application : reçoit
    Student "1" --> "*" SavedJob : sauvegarde
    Job "1" --> "*" SavedJob : est sauvegardée
    Student "1" --> "*" RecommendationHistory : reçoit
    Job "1" --> "*" RecommendationHistory : concernée
    Application "1" --> "0..1" Meeting : planifie
    Student "1" --> "*" Meeting : participe
    Recruiter "1" --> "*" Meeting : organise
```

### 3.3 PlantUML — diagramme de classes complet

```plantuml
@startuml MatiousHire_Classes
skinparam classAttributeIconSize 0

enum JobStatus { open; closed }
enum ApplicationStatus { applied; shortlisted; interview_invited; rejected; hired }
enum NotificationType { recommendation; interview; system }

class Student {
  - id : UUID
  - email : String
  - hashed_password : String
  - first_name : String
  - last_name : String
  - technical_skills : Text
  - cv_filename : String
  - cv_path : String
  - cv_extracted_text : Text
  - cv_extracted_at : DateTime
  - account_kind : String
  --
  + updateProfile()
  + uploadCv()
}

class Recruiter {
  - id : UUID
  - email : String
  - company_name : String
  --
  + publishJob()
  + rankCandidates()
}

class Admin {
  - id : UUID
  - email : String
  --
  + manageUsers()
  + viewAuditLogs()
}

class Job {
  - id : Integer
  - title : String
  - description : Text
  - required_skills : Text
  - location : String
  - status : JobStatus
}

class Application {
  - id : Integer
  - status : ApplicationStatus
  - match_score : Integer
  - cover_letter : Text
}

class SavedJob { - id : Integer }
class Meeting { - id : Integer; - scheduled_at : DateTime; - status : String }
class RecommendationHistory { - compatibility_score : Integer; - explanation : Text }
class AuditLog { - action : String; - actor_email : String }
class Notification { - type : NotificationType; - is_read : Boolean }

Recruiter "1" -- "0..*" Job
Student "1" -- "0..*" Application
Job "1" -- "0..*" Application
Student "1" -- "0..*" SavedJob
Job "1" -- "0..*" SavedJob
Student "1" -- "0..*" RecommendationHistory
Job "1" -- "0..*" RecommendationHistory
Application "1" -- "0..1" Meeting
Student "1" -- "0..*" Meeting
Recruiter "1" -- "0..*" Meeting

@enduml
```

### 3.4 Classes services (couche métier — annexe technique)

| Classe | Package | Responsabilité |
|--------|---------|----------------|
| `MatchingService` | `matching/service.py` | recommend_jobs, rank_applications |
| `MatchingPipeline` | `matching/pipeline.py` | Orchestration 6 étapes IA |
| `CvService` | `cv/service.py` | Upload, extraction, suppression CV |
| `AuditService` | `platform/service.py` | Persistance audit_logs |
| `OfferService` | `offers/service.py` | CRUD offres |

---

## 4. Diagrammes de séquence

### 4.1 Séquence — Recommandation d'offres IA (UC10)

**Scénario principal :** le candidat consulte ses top matches.

```mermaid
sequenceDiagram
    actor C as Candidat
    participant UI as Next.js
    participant API as FastAPI
    participant MS as MatchingService
    participant MP as MatchingPipeline
    participant MSS as calculate_matching_score
    participant DB as PostgreSQL

    C->>UI: Consulter recommandations
    UI->>API: GET /matching/candidates/me/recommendations
    API->>API: Vérifier JWT (rôle candidate)
    API->>DB: SELECT jobs WHERE status=open
    loop Pour chaque offre
        API->>MS: recommend_jobs(student)
        MS->>MS: profile_from_student / profile_from_job
        MS->>MP: run(profile, job)
        MP->>MSS: calculate_matching_score()
        MSS-->>MP: final_score, explanation_data
        MP-->>MS: MatchResult
    end
    MS->>MS: Tri décroissant par score
    MS->>DB: INSERT recommendation_history
    API-->>UI: JSON JobRecommendationOut[]
    UI-->>C: Afficher top matches + scores
```

**PlantUML :**

```plantuml
@startuml Seq_Recommendation
actor Candidat
participant "Next.js" as UI
participant "FastAPI\n/matching" as API
participant "MatchingService" as MS
participant "MatchingPipeline" as MP
participant "score_formula" as SF
database "PostgreSQL" as DB

Candidat -> UI : Consulter recommandations
UI -> API : GET /candidates/me/recommendations
API -> API : decode JWT
API -> DB : jobs ouverts
loop chaque offre
  API -> MS : score_student_job()
  MS -> MP : run(profile, job)
  MP -> SF : calculate_matching_score()
  SF --> MP : score + breakdown
  MP --> MS : MatchResult
end
MS -> MS : sort by score DESC
MS -> DB : record_recommendations()
API --> UI : liste triée
UI --> Candidat : Top matches IA
@enduml
```

---

### 4.2 Séquence — Upload CV (UC04)

```mermaid
sequenceDiagram
    actor U as Étudiant/Candidat
    participant UI as Next.js
    participant API as FastAPI
    participant CV as CvService
    participant ST as storage.py
    participant EX as extraction.py
    participant DB as PostgreSQL
    participant FS as uploads/cvs/

    U->>UI: Upload fichier PDF
    UI->>API: POST /students/me/cv (multipart)
    API->>CV: upload(student, filename, bytes)
    CV->>ST: validate_cv_file()
    CV->>ST: save_cv_file(uuid, filename)
    ST->>FS: Écrire fichier
    CV->>EX: extract_raw_text()
    EX-->>CV: raw_text
    CV->>CV: extract_skills_from_text()
    CV->>DB: UPDATE student (cv_*, skills)
    API->>API: record_audit(UPLOAD_CV)
    API-->>UI: CvUploadResult
    UI-->>U: Confirmation + skills détectées
```

---

### 4.3 Séquence — Classement candidats recruteur (UC12)

```mermaid
sequenceDiagram
    actor R as Recruteur
    participant UI as Pipeline UI
    participant API as FastAPI
    participant MS as MatchingService
    participant DB as PostgreSQL

    R->>UI: Ouvrir pipeline job #N
    UI->>API: GET /matching/recruiters/jobs/N/ranking
    API->>DB: SELECT applications + students
    loop Chaque candidature
        API->>MS: rank_applications()
        MS->>MS: safe_score_student_job()
    end
    MS->>MS: Tri par compatibility_score DESC
    API->>DB: UPDATE application.match_score
    API->>API: record_audit(RANK_CANDIDATES)
    API-->>UI: CandidateRankingOut[]
    UI-->>R: Liste classée + breakdown IA
```

---

## 5. Diagramme de composants (architecture)

```mermaid
flowchart TB
    subgraph Presentation["Couche Présentation"]
        Pages["Pages Next.js\nstudent | candidate | recruiter | admin"]
        Components["Composants\nJobsPanel, LlmPanel, ProfilePanel"]
    end

    subgraph API["Couche API"]
        Routers["Routeurs REST\nauth, jobs, matching, llm, meetings, admin"]
        Auth["JWT Auth"]
        Errors["Error Handlers"]
    end

    subgraph Metier["Couche Métier"]
        Users["users/"]
        Offers["offers/"]
        CV["cv/"]
        Platform["platform/"]
    end

    subgraph IA["Couche IA"]
        Matching["matching/\npipeline, scorer, score_formula"]
        LLM["llm/\nexplanation"]
        NLP["nlp, embeddings"]
    end

    subgraph Data["Couche Données"]
        PG["PostgreSQL"]
        Files["uploads/cvs/"]
    end

    Pages --> Routers
    Routers --> Auth
    Routers --> Metier
    Routers --> IA
    Metier --> PG
    Metier --> Files
    IA --> PG
    Platform --> PG
```

**PlantUML composants :**

```plantuml
@startuml MatiousHire_Components
package "Frontend" {
  [Next.js App Router] as FE
}
package "Backend FastAPI" {
  [Routeurs REST] as RT
  [Auth JWT] as JWT
  package "Métier" {
    [users] as US
    [offers] as OF
    [cv] as CV
    [platform] as PL
  }
  package "IA" {
    [matching] as MA
    [llm] as LL
  }
}
database "PostgreSQL" as DB
folder "uploads/cvs" as FS

FE --> RT : HTTPS/JSON
RT --> JWT
RT --> US
RT --> OF
RT --> CV
RT --> MA
RT --> LL
RT --> PL
US --> DB
OF --> DB
CV --> DB
CV --> FS
MA --> DB
PL --> DB
@enduml
```

---

## 6. Diagramme de déploiement

```mermaid
flowchart LR
    subgraph Client["Poste client"]
        Browser["Navigateur\nChrome / Edge"]
    end

    subgraph Server["Serveur application"]
        Next["Next.js :3000"]
        FastAPI["FastAPI uvicorn :8000"]
    end

    subgraph Storage["Persistance"]
        PG["PostgreSQL :5432"]
        Disk["Disque\nuploads/cvs/"]
    end

    Browser -->|HTTP| Next
    Next -->|REST API| FastAPI
    FastAPI --> PG
    FastAPI --> Disk
```

| Nœud | Technologie | Port |
|------|-------------|------|
| Client | Navigateur web | — |
| Frontend | Next.js 15 | 3000 |
| Backend | FastAPI + uvicorn | 8000 |
| SGBD | PostgreSQL | 5432 |
| Fichiers | Système de fichiers local | — |

---

## 7. Diagramme d'activité — Pipeline matching IA

```mermaid
flowchart TD
    Start([Début]) --> Collect[Collecte profil + offre]
    Collect --> NLP[Prétraitement NLP]
    NLP --> Features[Extraction features\nskills, TF-IDF, synonymes]
    Features --> Score[Scoring 6 critères\n35% skills, 25% exp, 20% sém...]
    Score --> Penalty{Pénalités métier?}
    Penalty -->|Oui| ApplyPen[Appliquer facteur ×0.75...]
    Penalty -->|Non| LLM
    ApplyPen --> LLM[Génération explication LLM]
    LLM --> Rank[Classement décroissant]
    Rank --> End([Score 0-100 + explication])
```

---

## 8. Légende UML pour le jury

| Symbole | Signification |
|---------|---------------|
| `<<include>>` | Un cas d'utilisation en inclut un autre (ex. Recommandation inclut Calcul score) |
| `..>` | Dépendance vers acteur système (IA) |
| `1 -- 0..*` | Un recruteur publie plusieurs offres |
| `UUID` | Identifiant universel (students, recruiters) |
| Acteur secondaire | Système IA — automatise sans interaction humaine directe |

---

## 9. Slides PowerPoint — quelle figure où

| Slide | Diagramme UML |
|-------|---------------|
| 19 | **`00_architecture_overview`** + **`09_architecture_layers`** + `06_components` |
| 20 | **`12_architecture_ia_module`** + `08_activity_matching` ou `03_seq_recommendation` |
| 21 | **`02_classes_resume_presentation.puml`** (slide jury) · annexe : `02_classes_methods.puml` |
| 22 | **Cas d'utilisation** (`01_use_case.puml`) |
| 25 | **Diagramme de déploiement** (`07_deployment.puml`) |
| 31 | **Séquence classement recruteur** (`05_seq_ranking.puml`) |
| 33 | **Séquence upload CV** (`04_seq_upload_cv.puml`) |
| 6 | **Architecture frontend** (`14_architecture_frontend.puml`) |
| Annexe | `11_architecture_packages` · `13_architecture_data_flow` · `10_architecture_context` |

---

## 10. Phrase oral jury (diagrammes UML)

> *« La modélisation UML de MatiousHire identifie quatre acteurs métier et un acteur système IA. Le diagramme de classes reflète le schéma PostgreSQL avec neuf entités principales. Les diagrammes de séquence montrent que chaque recommandation passe par le pipeline ML/NLP avant persistance dans recommendation_history, garantissant traçabilité et explicabilité. »*

---

*MatiousHire — UML PFE 2026 — Matious Digital × EMSI*
