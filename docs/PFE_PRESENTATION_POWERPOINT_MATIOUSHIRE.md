# MatiousHire — Plan PowerPoint PFE 2026 (soutenance jury)
## Calqué sur la structure Imad Manni / Squad Swipe — adapté Matious Digital + EMSI

---

## CHARTE GRAPHIQUE (toutes les slides)

| Élément | Spécification |
|---------|---------------|
| **En-tête gauche** | Logo **MATIOUS** (bleu marine `#1a2744`) — remplace le logo PCA |
| **En-tête droit** | Logo **EMSI** (vert `#00873F`) |
| **Pied de page** | Fil d'Ariane : `Présentation générale \| Définition des fonctionnalités \| Etude conceptuelle \| Réalisation \| Conclusion` |
| **Année** | `2025 - 2026` (coin bas droit) |
| **Couleurs** | Bleu Matious (titres), Vert EMSI (accents), Gris clair (fond), Blanc (contenu) |
| **Police** | Montserrat / Calibri — titres en gras, corps 18–22 pt |

---

## SLIDE 1 — Page de garde

**[Logo MATIOUS — haut gauche]**  
**[Logo EMSI — haut droit]**

---

### Développement d'une plateforme de recrutement intelligent **MatiousHire**
#### basée sur le matching ML/NLP

**Projet de fin d'études**

En vue de l'obtention du titre :  
**INGÉNIEUR en informatique**  
Génie informatique — option : Génie logiciel

**Élaboré par :**  
[Votre Prénom NOM]

**Encadrants entreprise :**  
Matious Digital — [Nom encadrant technique]

**Encadrante pédagogique :**  
Pr. [Nom professeur EMSI]

**Année universitaire :** 2025/2026

**Devant les membres du jury :**  
Pr. _______________  
Pr. _______________  
Pr. _______________

**Projet :** MatiousHire  
**Organisme d'accueil :** Matious Digital — Casablanca, Maroc

---

## SLIDE 2 — Plan

**Plan**

| # | Partie |
|---|--------|
| **01** | Présentation générale du projet |
| **02** | Définition des fonctionnalités |
| **03** | Etude conceptuelle |
| **04** | Réalisation |
| **05** | Conclusion |

---

# PARTIE 01 — PRÉSENTATION GÉNÉRALE DU PROJET

---

## SLIDE 3 — Séparateur Partie 01

**01**  
**Présentation générale du projet**

- L'organisme d'accueil
- Contexte du projet
- Problématique
- Objectifs
- Méthodologie adoptée

---

## SLIDE 4 — L'organisme d'accueil : Matious Digital

**L'organisme d'accueil**

**Matious Digital** — Startup marocaine fondée en **2017** à Casablanca.

> *Deux ingénieurs, une vision : construire une technologie qui compte.*

| | |
|---|---|
| **Positionnement** | Société **AI-first** — ingénierie logicielle, extension d'équipe, plateformes intelligentes |
| **Rayonnement** | Clients internationaux (USA, Europe) — **100+ projets** livrés sur **4 continents** |
| **Expertise 2026** | Systèmes multi-agents, LLM, pipelines ML/NLP, workflows agentiques |

**Services Matious Digital :**

| Service | Description |
|---------|-------------|
| **Développement sur mesure** | Plateformes web & API full-stack (React, Next.js, FastAPI, PostgreSQL) |
| **Extension d'équipe** | Ingénieurs seniors intégrés au client (modèle *Team Extension*, depuis 2022) |
| **Solutions IA** | RAG, matching intelligent, agents LLM, pipelines ML en production |
| **Conseil technique** | Architecture, qualité code, mise en production |

**Ce que Matious apporte au PFE :** cadre professionnel AI-first, exigence qualité production, mentorat technique senior.

---

## SLIDE 5 — How we got here (timeline Matious)

**Matious Digital — Parcours 2017 → 2026**

```
2017 ──► Fondation au Maroc. Deux ingénieurs, une vision.
2018 ──► Premiers clients internationaux (USA, Europe).
2020 ──► Pivot IA : premiers systèmes RAG et pipelines ML en production.
2022 ──► Modèle Team Extension : ingénieurs embarqués full-time chez le client.
2024 ──► Société AI-first : 14 plateformes IA, multi-agents, LLM.
2026 ──► Aujourd'hui : 100+ projets, 9 ans, toujours en construction.
```

**Message jury :** MatiousHire s'inscrit dans l'ADN **AI-first** de Matious Digital — pas un CRUD classique, mais une **plateforme intelligente** livrable en production.

---

## SLIDE 6 — Leadership & valeurs Matious Digital

**Leadership — The people behind it**

*[Photo / noms des fondateurs ou encadrants si disponibles]*

**What drives us — Nos valeurs**

| Valeur | Signification pour le PFE |
|--------|---------------------------|
| **Ship, don't just plan** | MatiousHire est une application **fonctionnelle** (Next.js + FastAPI), pas une maquette |
| **Embedded, not outsourced** | Le stagiaire intégré à l'équipe Matious — même exigence que les projets clients |
| **AI-first thinking** | Le matching ML/NLP est au **centre** du design, pas une feature ajoutée |
| **Quality without compromise** | Tests pytest (39 tests), gestion d'erreurs centralisée, code revu (Ruff) |

---

## SLIDE 7 — Contexte du projet : le flux de recrutement

**Contexte du projet**

**Introduction — Le flux de recrutement aujourd'hui**

Aujourd'hui, le recrutement est souvent **dispersé** : emails, pièces jointes, fichiers Excel, suivis manuels.

| Acteur | Difficulté |
|--------|------------|
| **RH / Recruteur** | Volume élevé de CV, formats hétérogènes (PDF de qualité variable), tri long, comparaisons subjectives |
| **Candidat / Étudiant** | Offres nombreuses, peu personnalisées — ne sait pas **pourquoi** une offre lui correspond |
| **Entreprise** | Risque d'oubli, lenteur de réponse, manque de traçabilité |

**Contexte Matious Digital :**  
Dans le cadre de l'offre de services RH intelligents, Matious Digital confie le développement de **MatiousHire** — plateforme web centralisée avec **matching ML/NLP explicable**.

**Flux cible MatiousHire :**
```
Profil + CV → Extraction NLP → Score multi-critères → Recommandations / Classement → Explication IA → Entretien → Décision
```

---

## SLIDE 8 — Problématique

**Problématique**

**Limites du recrutement manuel et des plateformes sans IA**

| Limite | Impact |
|--------|--------|
| **Volume et lenteur** | Temps perdu sur des tâches répétitives |
| **Pas de centralisation** | Données éparpillées, pas de vue pipeline |
| **Scoring subjectif** | Biais humain, comparaisons non reproductibles |
| **Erreurs et oublis** | Candidats non traités, réponses tardives |
| **Manque d'explicabilité** | Le candidat et le recruteur ne comprennent pas le « pourquoi » du match |

**Question centrale :**  
Comment concevoir une plateforme web capable de **comparer automatiquement** un CV et une offre d'emploi pour produire un **score mesurable**, un **classement** et une **explication lisible** ?

---

## SLIDE 9 — Objectifs

**Objectifs**

**Objectif général**  
Concevoir et développer **MatiousHire**, une plateforme intelligente de recrutement basée sur le **matching ML/NLP**, permettant la recommandation d'offres aux candidats, le classement automatique des candidatures pour les recruteurs, et l'explicabilité des scores par un module IA.

**Objectifs spécifiques**

| # | Objectif |
|---|----------|
| O1 | Architecture full-stack modulaire (Next.js + FastAPI + PostgreSQL) |
| O2 | Modules métier : auth JWT, profils, offres, CV, entretiens, admin |
| O3 | Pipeline ML/NLP : score multi-critères (6 dimensions), TF-IDF, synonymes |
| O4 | API recommandation & ranking + historiques |
| O5 | Module LLM explicable (résumés, compétences manquantes, conseils) |
| O6 | Interfaces multi-rôles + tests automatisés (pytest) + documentation jury |

---

## SLIDE 10 — Méthodologie adoptée

**Méthodologie adoptée**

**Approche par itérations sur 4 mois (stage PFE)**

| Phase | Durée | Livrables |
|-------|-------|-----------|
| **Cadrage** | Mois 1 | Analyse besoin, schéma DB, auth, squelette app |
| **Métier** | Mois 2 | CRUD, upload CV, extraction, dashboards |
| **IA** | Mois 3 | Pipeline matching, API reco/ranking |
| **Intégration** | Mois 4 | LLM, admin, tests, doc, soutenance |

**Méthode :**
- Développement **agile** (sprints hebdomadaires avec encadrant Matious)
- Conception **UML** (cas d'utilisation, classes, architecture)
- Validation continue : **pytest** + démo encadrant
- Documentation technique parallèle (docs PFE)

**Outils de gestion :** Git, GitHub, Swagger (FastAPI auto-doc)

---

# PARTIE 02 — DÉFINITION DES FONCTIONNALITÉS

---

## SLIDE 11 — Séparateur Partie 02

**02**  
**Définition des fonctionnalités**

- Benchmarking comparatif
- Vue globale
- Identification des acteurs
- Besoins fonctionnels

---

## SLIDE 12 — Benchmarking comparatif

**Benchmarking comparatif**

| Plateforme | Matching IA | Score explicable | Upload CV | Pipeline recruteur | Open / custom |
|------------|-------------|------------------|-----------|-------------------|---------------|
| **LinkedIn Recruiter** | Partiel | Non | Non | Oui | SaaS fermé |
| **Indeed** | Basique mots-clés | Non | Non | Limité | SaaS |
| **HireVue** | Vidéo + IA | Partiel | Non | Oui | Coûteux |
| **MatiousHire (PFE)** | **ML/NLP multi-critères** | **Oui (LLM + breakdown)** | **Oui PDF/DOCX** | **Oui complet** | **Sur mesure** |

**Positionnement MatiousHire :**  
Plateforme **sur mesure**, **explicable**, combinant TF-IDF + dictionnaire compétences + fusion pondérée — adaptée PFE et déployable par Matious Digital pour ses clients RH.

---

## SLIDE 13 — Vue globale du système

**Vue globale**

**MatiousHire — Vue d'ensemble**

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Étudiant    │    │  Candidat    │    │  Recruteur   │    │    Admin     │
│  /student/*  │    │ /candidate/* │    │ /recruiter/* │    │  /admin/*    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   Next.js 15 (UI)   │
                          └─────────┬─────────┘
                                    │ REST / JWT
                          ┌─────────▼─────────┐
                          │   FastAPI (API)     │
                          ├─────────────────────┤
                          │ Matching ML/NLP     │
                          │ LLM explicable      │
                          │ CV extraction       │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │ PostgreSQL + CV     │
                          │ audit_logs + histo  │
                          └─────────────────────┘
```

---

## SLIDE 14 — Identification des acteurs

**Identification des acteurs**

| Acteur | Description | Actions principales |
|--------|-------------|---------------------|
| **Étudiant** | Profil académique, stages observation/opérationnel | Profil, CV, offres, recommandations IA |
| **Candidat** | Profil professionnel, stage fonctionnel 4–6 mois | Idem + parcours carrière |
| **Recruteur** | Publie offres, gère pipeline | CRUD offres, ranking IA, entretiens |
| **Administrateur** | Supervise la plateforme | Stats, utilisateurs, audit logs |
| **Système IA** | Acteur technique | Scoring, reco, explications LLM |

**Diagramme cas d'utilisation** *(slide suivante ou annexe UML)*

---

## SLIDE 15 — Besoins fonctionnels (1/2)

**Besoins fonctionnels**

**BF1 — Authentification & autorisation**
- Inscription / connexion par rôle (JWT)
- Protection des routes par rôle

**BF2 — Gestion des profils**
- CRUD profil étudiant / candidat / recruteur
- Différenciation student vs candidate (types de stage)

**BF3 — Gestion des CV**
- Upload PDF, DOCX, TXT (max 5 Mo)
- Extraction texte (pypdf) + détection compétences
- Stockage hybride : fichier + métadonnées PostgreSQL

**BF4 — Gestion des offres**
- CRUD offres (titre, description, compétences, localisation)
- Format compétences : `python,sql|optional:docker`

---

## SLIDE 16 — Besoins fonctionnels (2/2)

**Besoins fonctionnels (suite)**

**BF5 — Matching & recommandations IA**
- Score compatibilité 0–100 (6 critères pondérés)
- Recommandation offres : `GET /matching/.../me/recommendations`
- Classement candidats : `GET /matching/recruiters/jobs/{id}/ranking`

**BF6 — Explicabilité LLM**
- Explication score, compétences manquantes, conseils
- Questions d'entretien suggérées

**BF7 — Entretiens & notifications**
- Planification meetings, créneaux, disponibilités
- Notifications candidat / recruteur

**BF8 — Administration & traçabilité**
- Dashboard admin, journaux d'audit, historique recommandations

---

# PARTIE 03 — ÉTUDE CONCEPTUELLE

---

## SLIDE 17 — Séparateur Partie 03

**03**  
**Etude conceptuelle**

- Planning temporel
- Architecture globale
- Diagramme de classes
- Cas d'utilisation

---

## SLIDE 18 — Planning temporel (Gantt 4 mois)

**Planning temporel**

| Mois | S1 | S2 | S3 | S4 |
|------|----|----|----|----|
| **M1 — Fondations** | Analyse | Architecture | DB + Auth | Squelette UI |
| **M2 — Métier** | Profils | Offres | CV upload | Dashboards |
| **M3 — IA** | NLP | Scoring | API reco | Ranking |
| **M4 — Finalisation** | LLM | Admin/Audit | Tests pytest | Doc + soutenance |

**Jalons :** M1 = auth OK · M2 = CV extrait · M3 = score IA · M4 = démo complète

---

## SLIDE 19 — Architecture globale (6 couches)

**Architecture globale**

*(Reprendre le schéma 6 couches — identique doc PFE)*

| Couche | Technologies |
|--------|--------------|
| **Présentation** | Next.js 15, React 19, Fetch API |
| **API** | FastAPI, JWT, Pydantic |
| **Métier** | users, offers, CV, meetings, admin |
| **IA** | NLP, matching, embeddings, LLM |
| **Données** | PostgreSQL, uploads/cvs/, audit_logs, recommendation_history |
| **DevOps (cible)** | Docker, CI, cloud |

**Principe :** séparation des responsabilités — le moteur IA est un module indépendant (`app/modules/matching/`).

---

## SLIDE 20 — Architecture pipeline ML/NLP

**Architecture — Pipeline IA**

```
Profil candidat + Offre
        │
        ▼
[1] Collecte profil + CV
[2] Prétraitement NLP (tokenisation FR/EN)
[3] Extraction features (skills, TF-IDF, synonymes)
[4] Scoring multi-critères (formule 6 dimensions)
[5] Pénalités métier
[6] Explication LLM
[7] Classement décroissant
        │
        ▼
Score 0–100 + breakdown + explication
```

**Formule :**
```
S = 100 × (0,35·Comp + 0,25·Exp + 0,20·Sém + 0,10·Form + 0,05·Loc + 0,05·Disp)
S_final = S × pénalités
```

---

## SLIDE 21 — Diagramme de classes global (résumé jury)

**Diagramme de classes — vue synthèse MatiousHire**

> **Figure à insérer :** [`docs/uml/02_classes_resume_presentation.puml`](uml/02_classes_resume_presentation.puml)  
> Export PNG via [plantuml.com](https://www.plantuml.com/plantuml) → coller le fichier → télécharger PNG

**Structure en 3 colonnes (lisible en 1 slide) :**

| Zone | Contenu |
|------|---------|
| **Domaine métier** | Applicant → Student / Candidate, Recruiter, Admin, Job, Application, Meeting, RecommendationHistory, AuditLog |
| **Services applicatifs** | UserService, OfferService, CvService, MeetingService, AuditService |
| **Module IA** | MatchingService → MatchingPipeline → ScoreFormula, LlmService, MatchResult |

**Relations clés :**
- Recruteur `1 — 0..*` Job
- Candidat/Étudiant `1 — 0..*` Application `* — 1` Job
- MatchingService alimente RecommendationHistory (traçabilité)
- LlmService explique les scores du pipeline (explicabilité IA)

**Phrase oral jury :**
> *« Le diagramme de classes global montre trois couches : neuf entités PostgreSQL, six services métier, et le module IA avec pipeline de matching à six critères et couche LLM explicable. Student et Candidate héritent conceptuellement d'Applicant ; en base, une seule table students avec account_kind. »*

**Annexe technique (non projetée) :** `02_classes_methods.puml` — toutes les méthodes du backend.

*(Ancien tableau entités — conservé pour notes speaker)*

| Classe | Attributs clés | Relations |
|--------|----------------|-----------|
| **Student** | email, skills, cv_extracted_text, account_kind | → Application, RecommendationHistory |
| **Recruiter** | email, company_name | → Job |
| **Job** | title, description, required_skills, status | → Application |
| **Application** | status, match_score | Student ↔ Job |
| **RecommendationHistory** | compatibility_score, explanation | Student ↔ Job |
| **AuditLog** | actor_email, action, details | Traçabilité |
| **Meeting** | scheduled_at, status | Application ↔ Recruteur ↔ Student |

---

## SLIDE 22 — Cas d'utilisation

**Diagramme de cas d'utilisation**

> **Figure complète :** [`docs/PFE_UML_MATIOUSHIRE.md`](PFE_UML_MATIOUSHIRE.md) — §2 (PlantUML exportable)

**Packages :**
- **Authentification** : S'inscrire, Se connecter
- **Profil & CV** : Gérer profil, Uploader CV, Consulter extraction
- **Offres** : Consulter, Publier, Postuler, Sauvegarder
- **Matching IA** : Recommandations, Calcul score, Classement, Explication LLM
- **Entretiens** : Planifier, Disponibilités, Confirmer/Refuser
- **Administration** : Dashboard, Utilisateurs, Audit logs

**Acteurs :** Étudiant · Candidat · Recruteur · Administrateur · Système IA (secondaire)

**Slides annexe UML (optionnelles) :**
- Séquence recommandation IA — UML §4.1
- Séquence upload CV — UML §4.2
- Diagramme composants — UML §5
- Diagramme déploiement — UML §6

---

# PARTIE 04 — RÉALISATION

---

## SLIDE 23 — Séparateur Partie 04

**04**  
**Réalisation**

- Etude et choix techniques
- Environnement de la plateforme
- Mise en œuvre et démonstration

---

## SLIDE 24 — Choix techniques

**Choix techniques**

| Composant | Choix | Justification |
|-----------|-------|---------------|
| Frontend | **Next.js 15** | App Router, SSR, performance |
| Backend | **FastAPI** | Python = écosystème IA, Swagger auto |
| ORM | **SQLAlchemy 2 + Alembic** | Migrations versionnées |
| SGBD | **PostgreSQL** | Relationnel, robuste, production |
| Auth | **JWT (HMAC)** | Stateless, rôles dans token |
| NLP | **TF-IDF maison + synonymes** | Explicable, pas de boîte noire |
| Extraction CV | **pypdf** | Léger, sans GPU |
| Tests | **pytest (39 tests)** | Régression automatisée |
| Qualité | **Ruff** | Lint + format Python |

---

## SLIDE 25 — Environnement de la plateforme

**Environnement de la plateforme**

| Environnement | Configuration |
|---------------|---------------|
| **Backend** | Python 3.13, uvicorn, port 8000 |
| **Frontend** | Node.js, Next.js, port 3000 |
| **Base de données** | PostgreSQL (prod) / SQLite (tests) |
| **Stockage CV** | `uploads/cvs/` |
| **API doc** | Swagger UI → `/docs` |

**Commandes démo jury :**
```powershell
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run build && npm run start
```

---

## SLIDE 26 — Workflow applicatif MatiousHire

**Workflow — Parcours candidat → recruteur**

```
1. Candidat s'inscrit → complète profil → upload CV
2. Extraction texte + compétences → profil enrichi
3. GET /matching/candidates/me/recommendations
4. Affichage top matches + score + explication LLM
5. Candidat postule → application créée
6. Recruteur ouvre pipeline → ranking IA des candidats
7. Shortlist / entretien / décision
8. Audit log + historique recommandations enregistrés
```

---

## SLIDES 27–36 — Présentation graphique (captures d'écran)

**Présentation graphique — Interfaces**

| Slide | Capture | Message jury |
|-------|---------|--------------|
| 27 | Page login multi-rôles | Auth JWT, 4 rôles |
| 28 | Dashboard candidat + recommandations IA | Valeur IA pour candidat |
| 29 | Détail score ML/NLP (6 critères) | Explicabilité |
| 30 | Panneau explication LLM | IA explicable |
| 31 | Pipeline recruteur — ranking | Valeur IA pour recruteur |
| 32 | Création offre + compétences | Saisie métier |
| 33 | Upload CV + extraction | Couche données CV |
| 34 | Swagger `/matching/pipeline` | Transparence API |
| 35 | Admin dashboard + audit logs | Supervision |
| 36 | pytest — 39 tests passed | Qualité logicielle |

*(Insérer vos vraies captures d'écran du projet)*

---

## SLIDE 37 — Tests & qualité (pytest)

**Qualité logicielle — pytest**

| Couche | Fichiers tests | Vérifications |
|--------|----------------|---------------|
| Unit | test_auth, test_matching | JWT, formule score, NLP |
| Service | test_recommendations | Ranking, historiques |
| API | test_api_* | Endpoints, erreurs structurées |
| Données | test_data_* | CV storage, audit, history |

**Résultat :** `39 passed` — gestion d'erreurs centralisée (`error_handlers.py`)

---

# PARTIE 05 — CONCLUSION

---

## SLIDE 38 — Séparateur Partie 05

**05**  
**Conclusion**

---

## SLIDE 39 — Conclusion

**Conclusion**

Pour conclure, nous avons développé **MatiousHire**, une plateforme intelligente de recrutement pour **Matious Digital**, automatisant le parcours :

**Profil + CV → Matching ML/NLP → Recommandations / Classement → Explication IA → Entretien → Décision**

Ce projet répond aux défis de :
- lourdeur du tri manuel ;
- subjectivité du scoring ;
- manque d'explicabilité pour candidats et recruteurs ;
- absence de traçabilité (audit + historiques IA).

**Apports techniques :**
- Architecture modulaire 6 couches ;
- Score hybride explicable (6 critères + pénalités) ;
- 39 tests pytest, documentation complète ;
- Alignement avec la vision **AI-first** de Matious Digital.

**Perspectives :** Sentence-BERT, LLM cloud (Ollama/OpenAI), learning-to-rank, déploiement Docker/cloud pour clients Matious.

---

## SLIDE 40 — Merci

**Merci pour votre attention**

**Questions ?**

---

**[Logo MATIOUS — centre ou bas]**  
**[Logo EMSI]**

MatiousHire — PFE 2026  
Matious Digital × EMSI  
[Votre nom] — [email contact]

---

## ANNEXE — Script oral d'animation (15 min)

| Min | Slide | À dire |
|-----|-------|--------|
| 0–1 | 1 | Titre, contexte EMSI + Matious Digital |
| 1–2 | 2–4 | Plan + présentation Matious (startup AI-first) |
| 2–3 | 5–6 | Timeline + valeurs — lien avec le projet |
| 3–5 | 7–9 | Contexte RH, problématique, objectifs |
| 5–6 | 10 | Méthodologie 4 mois |
| 6–8 | 12–16 | Fonctionnalités, acteurs, benchmarking |
| 8–10 | 18–22 | Architecture, pipeline IA, UML |
| 10–13 | 24–36 | Démo live ou captures |
| 13–14 | 37 | Tests pytest |
| 14–15 | 39–40 | Conclusion + questions |

---

*Document de travail — à transférer slide par slide dans PowerPoint*
