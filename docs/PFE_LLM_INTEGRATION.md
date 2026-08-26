# Intégration LLM — Résumés et explications explicables
## MatiousHire — Documentation jury PFE 2026

---

## 1. Positionnement du module LLM

Le module LLM **ne remplace pas** le recruteur. Il **explique** les résultats du moteur de matching (scores numériques) en langage naturel, pour :

- **Candidat** : comprendre pourquoi une offre lui correspond
- **Recruteur** : justifier un classement et préparer un entretien
- **Jury** : démontrer une IA **explicable** et **traçable**

> Principe : *« Le LLM aide à décider, il ne décide pas. »*

---

## 2. Architecture du module

```
Scores matching (ML/NLP)
        │
        ▼
┌───────────────────┐
│  LlmService       │
│  app/modules/llm/ │
└─────────┬─────────┘
          │
    ┌─────┴─────┬─────────────┬──────────────┐
    ▼           ▼             ▼              ▼
 Résumé CV   Résumé offre  Explication   Compétences
                              score       manquantes
```

### Fichiers

| Fichier | Rôle |
|---------|------|
| `explanation.py` | Génération textuelle (FR) |
| `service.py` | Orchestration `LlmInsight` |
| `routers/llm.py` | API REST |

---

## 3. Sorties générées (`LlmInsight`)

| Champ | Description |
|-------|-------------|
| `explanation` | Texte complet de compatibilité |
| `cv_summary` | Résumé intelligent du CV |
| `job_summary` | Résumé de l'offre |
| `matched_skills` | Compétences présentes |
| `missing_skills` | **Compétences manquantes** |
| `strengths` | Points forts du candidat |
| `score_justification` | Décomposition du score (%) |
| `improvement_tips` | Conseils d'amélioration profil |
| `interview_questions` | Questions d'entretien suggérées |
| `disclaimer` | Avertissement aide à la décision |

---

## 4. Exemple d'explication (format jury)

> *« Le candidat présente une compatibilité de 78% avec l'offre « Développeur Full-Stack » car il possède plusieurs compétences clés demandées, notamment Python, React, PostgreSQL. Son expérience correspond aux missions décrites. Le score est toutefois modéré en raison de : compétences manquantes : docker, aws. Score global 78% calculé ainsi : compétences 85%, expérience 70%, sémantique 72%... »*

---

## 5. API REST

| Méthode | Endpoint | Rôle |
|---------|----------|------|
| `GET` | `/llm/module` | Métadonnées module (démo jury) |
| `POST` | `/llm/explain` | Explication à la demande |
| `GET` | `/llm/candidates/me/cv-summary` | Résumé CV candidat |
| `GET` | `/llm/candidates/me/explain-job/{id}` | Explication pour une offre |
| `GET` | `/llm/recruiters/applications/{id}/explain` | Explication pour recruteur |

---

## 6. Interface utilisateur

- **Candidat** (`/candidate/jobs`) : bouton « Voir explication LLM complète »
- **Recruteur** (`/recruiter/pipeline`) : bouton « Explication IA » par candidat
- Panneau dépliable : résumés, compétences manquantes, conseils

---

## 7. Démo jury (5 min)

1. `GET /llm/module` dans Swagger — présenter le module
2. Connexion **candidat** → Jobs → recommandation → explication LLM
3. Montrer **compétences manquantes** en orange
4. Connexion **recruteur** → Pipeline → Explication IA sur un candidat
5. Insister : score chiffré + texte = **explicabilité**

---

## 8. Évolutions (perspectives)

- Connexion OpenAI / Ollama pour génération plus riche
- RAG sur base de compétences métier
- Feedback recruteur pour affiner les explications

---

*MatiousHire PFE 2026 — Module LLM v1.0.0*
