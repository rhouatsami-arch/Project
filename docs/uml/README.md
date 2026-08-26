# MatiousHire — Diagrammes PlantUML (PFE 2026)

Diagrammes UML et **architecture** pour soutenance jury — Matious Digital × EMSI.

Export : [plantuml.com](https://www.plantuml.com/plantuml) · VS Code PlantUML · draw.io

---

## Architecture (figures jury — priorité)

| Fichier | Diagramme | Slide |
|---------|-----------|-------|
| **`00_architecture_overview.puml`** | **Vue d'ensemble système (synthèse)** | Slide 19 |
| **`09_architecture_layers.puml`** | **Architecture 6 couches (figure principale)** | Slide 19 |
| `10_architecture_context.puml` | Contexte système (acteurs + Matious Digital) | Slide 4 / 19 |
| `11_architecture_packages.puml` | Packages backend + frontend | Slide 19 / annexe |
| `12_architecture_ia_module.puml` | Architecture interne module IA | Slide 20 |
| `13_architecture_data_flow.puml` | Flux de données (CV · Reco · Ranking) | Slide 20 |
| `14_architecture_frontend.puml` | Routes Next.js + composants | Slide 6 |
| `06_components.puml` | Composants (vue simplifiée) | Slide 19 |
| `07_deployment.puml` | Déploiement (ports, nœuds) | Slide 25 |

## Modélisation métier — Diagrammes de classes

| Fichier | Diagramme | Slide |
|---------|-----------|-------|
| **`02_classes_resume_presentation.puml`** | **RESUME GLOBAL jury (1 slide PowerPoint)** | **Slide 21** |
| `02_classes_methods.puml` | Toutes les methodes (services + API + IA) | Annexe technique |
| `02_classes_methods_domain.puml` | Methodes par entite domaine | Annexe |
| `02_classes_domain.puml` | Entites PostgreSQL (5 packages) | Annexe |
| `02_classes_services.puml` | Services Python detailles | Annexe |
| `02_classes_global.puml` | Domaine + services (vue intermediaire) | Annexe |
| `02_classes.puml` | Domaine seul (compact) | Apercu |
| `01_use_case.puml` | Cas d'utilisation | Slide 22 |

Guide classes : [`README_CLASSES.md`](README_CLASSES.md)

## Séquences & activité

| Fichier | Diagramme | Slide |
|---------|-----------|-------|
| `03_seq_recommendation.puml` | Séquence recommandations IA | Slide 20 |
| `04_seq_upload_cv.puml` | Séquence upload CV | Slide 33 |
| `05_seq_ranking.puml` | Séquence classement recruteur | Slide 31 |
| `08_activity_matching.puml` | Activité pipeline IA | Slide 20 |

---

## Ordre recommandé pour PowerPoint (architecture)

1. `00_architecture_overview.puml` — vue globale 1 slide
2. `09_architecture_layers.puml` — détail 6 couches
3. `12_architecture_ia_module.puml` — cœur IA du PFE
4. `07_deployment.puml` — déploiement technique
5. `01_use_case.puml` + **`02_classes_resume_presentation.puml`** — UML metier (slide jury)

---

## Export PNG (3 méthodes)

### 1. En ligne
[plantuml.com/plantuml/uml](https://www.plantuml.com/plantuml/uml/) → coller `.puml` → PNG

### 2. VS Code / Cursor
Extension **PlantUML** + [Graphviz](https://graphviz.org/download/) → `Alt+D` → Export

### 3. draw.io
**Arrange → Insert → Advanced → PlantUML**

---

## StarUML

Générer PNG via PlantUML (recommandé) ou recréer manuellement en suivant les `.puml`.

---

Documentation : [`../PFE_UML_MATIOUSHIRE.md`](../PFE_UML_MATIOUSHIRE.md) · [`../PFE_COUCHE_DONNEES.md`](../PFE_COUCHE_DONNEES.md)

*MatiousHire — PFE 2026*
