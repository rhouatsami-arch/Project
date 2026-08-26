# MatiousHire — Diagrammes de classes PlantUML

Organisation alignee sur le code source (`app/models/`, `app/modules/`).

Export : [plantuml.com/plantuml/uml](https://www.plantuml.com/plantuml/uml/)

---

## Diagramme resume jury (PowerPoint slide 21)

| Fichier | Contenu |
|---------|---------|
| **`02_classes_resume_presentation.puml`** | **Vue synthese 3 colonnes : Domaine + Services + IA** |

Ideal pour la soutenance : une seule figure lisible, methodes essentielles seulement, legende incluse.

---

## Diagrammes de classes avec methodes (annexe technique)

| Fichier | Contenu |
|---------|---------|
| **`02_classes_methods.puml`** | **Complet : 8 packages, toutes methodes services + routers** |
| `02_classes_methods_domain.puml` | Entites + operations metier par acteur |

### Inventaire methodes (par couche)

| Couche | Classes | Nb methodes approx. |
|--------|---------|---------------------|
| Auth | AuthService | 7 |
| Users | UserService | 6 |
| Offers | OfferService | 6 |
| CV | CvService + utils | 7 |
| Matching | MatchingService, Pipeline, Formula, NLP | 35+ |
| LLM | LlmService, LlmExplanation | 10 |
| Platform | MeetingService, Notification, Audit | 20+ |
| API Routers | 9 controleurs FastAPI | 60+ |

---

| Fichier | Contenu | Usage jury |
|---------|---------|------------|
| **`02_classes_resume_presentation.puml`** | **Resume global 1 slide** | **Slide 21 - PRINCIPAL** |
| `02_classes_domain.puml` | Entites PostgreSQL detaillees (5 packages) | Annexe |
| `02_classes_services.puml` | Services Python (Matching, CV, LLM) | Annexe |
| `02_classes_global.puml` | Vue intermediaire domaine + services | Annexe |
| `02_classes.puml` | Vue compacte domaine seul | Apercu |

---

## Structure du diagramme domaine (02_classes_domain.puml)

```
Enumerations metier
  JobStatus, ApplicationStatus, InternshipDurationType
  MeetingStatus, NotificationType, AccountKind

Utilisateurs et comptes
  Applicant (abstract)
    <|-- Student
    <|-- Candidate
  Recruiter, Admin

Recrutement
  Job, Application, SavedJob

Plateforme RH
  InterviewSlot, CandidateAvailability, Meeting, Notification

Tracabilite et IA
  RecommendationHistory, AuditLog
```

---

## Structure du diagramme services (02_classes_services.puml)

```
DTO Matching
  ApplicantProfile, JobProfile, ScoreBreakdown, MatchResult

Module Matching IA
  MatchingService, MatchingPipeline, MatchingScoreService, ScoreFormula

Module CV
  CvService, CvStorage, CvExtraction, CvSkills

Module LLM et Platform
  LlmExplanation, AuditModule, OfferService, UserService

Schemas API REST
  CandidateSchema, StudentSchema, JobRecommendationOut
```

---

## Correspondance code source

| Classe UML | Fichier Python |
|------------|----------------|
| Applicant / Student / Candidate | `app/models/recruitment.py` → Student |
| Recruiter, Job, Application | `app/models/recruitment.py` |
| Admin, Meeting, AuditLog | `app/models/platform.py` |
| MatchingService | `app/modules/matching/service.py` |
| MatchingPipeline | `app/modules/matching/pipeline.py` |
| ScoreFormula | `app/modules/matching/score_formula.py` |
| CvService | `app/modules/cv/service.py` |
| Candidate (schema API) | `app/schemas/candidate.py` |

---

## Regles syntaxe PlantUML (eviter les erreurs)

1. Enums : une valeur par ligne, **sans point-virgule**
2. Pas de `enum X { a; b }` sur une ligne
3. Pas de markdown `**` dans title ou notes
4. Pas de `=` dans les attributs de classe
5. Accents : eviter dans les labels (utiliser "recoit" pas "reçoit")
6. Classes multi-attributs : une ligne par attribut

---

## Export PNG

1. Ouvrir [plantuml.com](https://www.plantuml.com/plantuml/uml/)
2. Coller le contenu de `02_classes_resume_presentation.puml` (slide jury)
   ou `02_classes_domain.puml` (detail entites)
3. Verifier le rendu (pas de Syntax Error)
4. Telecharger PNG pour PowerPoint

---

*MatiousHire PFE 2026 — Matious Digital x EMSI*
