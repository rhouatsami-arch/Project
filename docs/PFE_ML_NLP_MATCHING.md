# Développement du moteur ML/NLP de matching et API recommandation
## MatiousHire — Documentation jury PFE 2026

---

## 1. Contexte et problématique

Dans une plateforme de recrutement, un recruteur reçoit de nombreuses candidatures. Le tri manuel est lent et subjectif. Un **étudiant** ou **candidat** doit aussi identifier rapidement les offres les plus adaptées à son profil.

**Objectif du module :** automatiser le **matching intelligent** entre profils et offres grâce à un **pipeline IA** combinant traitement NLP et scoring multi-critères.

---

## 2. Architecture du pipeline IA

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Profil candidat │     │  Offre d'emploi  │     │   Pipeline ML/NLP   │
│  - skills        │────▶│  - titre         │────▶│  1. Collecte        │
│  - CV extrait    │     │  - description   │     │  2. Prétraitement   │
│  - expériences   │     │  - compétences   │     │  3. Extraction      │
│  - formation     │     │  - localisation  │     │  4. Scoring         │
└─────────────────┘     └──────────────────┘     │  5. Classement      │
                                                    └──────────┬──────────┘
                                                               │
                                                    ┌──────────▼──────────┐
                                                    │ Score compatibilité │
                                                    │ + explication       │
                                                    └─────────────────────┘
```

### Étapes du pipeline (`app/modules/matching/pipeline.py`)

| Étape | Nom | Technique |
|-------|-----|-----------|
| 1 | **Collecte** | Agrégation profil structuré + texte brut du CV |
| 2 | **Prétraitement NLP** | Normalisation, tokenisation, stop-words FR/EN |
| 3 | **Extraction de features** | Dictionnaire + embeddings synonymes + TF-IDF |
| 4 | **Scoring multi-critères** | Fusion pondérée de 6 dimensions (formule PFE) |
| 5 | **Explication LLM** | Texte lisible + compétences manquantes |
| 6 | **Classement** | Tri décroissant + libellé (Excellent → Faible) |

---

## 3. Score de compatibilité — formule mathématique (implémentée)

Le score final \(S\) est une **somme pondérée** sur **6 dimensions**, normalisée entre **0 et 100** :

\[
S = 100 \times (
0{,}35\,S_{\text{skills}} +
0{,}25\,S_{\text{experience}} +
0{,}20\,S_{\text{semantic}} +
0{,}10\,S_{\text{education}} +
0{,}05\,S_{\text{location}} +
0{,}05\,S_{\text{availability}}
)
\]

### 3.1 Compétences \(S_{skills}\) — 35%
- Skills explicites + détection NLP (dictionnaire)
- Jaccard + couverture des skills requis + synonymes (embeddings légers)

### 3.2 Expérience \(S_{experience}\) — 25%
- Chevauchement expériences / projets / bio vs description de l'offre

### 3.3 Sémantique TF-IDF \(S_{semantic}\) — 20%
- Similarité cosinus TF-IDF entre corpus CV et corpus offre

### 3.4 Formation \(S_{education}\) — 10%
- Alignement du `field_of_study` avec le texte de l'offre

### 3.5 Localisation \(S_{location}\) — 5%
- Correspondance ville / zone géographique

### 3.6 Disponibilité / stage \(S_{availability}\) — 5%
- Type de stage (observation, opérationnel, **fonctionnel 4–6 mois**)

---

## 4. API REST — endpoints

| Méthode | Endpoint | Rôle | Description |
|---------|----------|------|-------------|
| `GET` | `/matching/pipeline` | Public | Métadonnées du pipeline (étapes, poids, algorithmes) |
| `POST` | `/matching/score` | Public | Calcul de score à la demande (démo jury) |
| `GET` | `/matching/students/me/recommendations` | Étudiant | Offres recommandées classées |
| `GET` | `/matching/candidates/me/recommendations` | Candidat | Offres recommandées classées |
| `GET` | `/matching/recruiters/jobs/{id}/ranking` | Recruteur | Classement détaillé des candidats |

### Exemple de réponse — recommandation

```json
{
  "job": { "title": "Développeur Full-Stack", "required_skills": "Python, React, PostgreSQL" },
  "compatibility_score": 78,
  "rank_label": "Strong match",
  "breakdown": {
    "skills_score": 85,
    "nlp_semantic_score": 72,
    "profile_alignment_score": 65,
    "internship_fit_score": 80,
    "matched_skills": ["python", "react", "postgresql"],
    "missing_skills": []
  },
  "explanation": "Global compatibility score: 78%. Skills overlap: 85%. ..."
}
```

---

## 5. Intégration dans l'application

- **À la candidature** : le score est calculé automatiquement via `MatchingService`
- **Pipeline recruteur** : candidats triés par score ML/NLP
- **Page Jobs étudiant/candidat** : section « Top matches » avec recommandations IA
- **Rétrocompatibilité** : l'ancien `candidate_match_score()` délègue au nouveau moteur

---

## 6. Choix techniques justifiables devant le jury

| Choix | Justification |
|-------|---------------|
| TF-IDF sans dépendance lourde | Léger, explicable, pas de GPU requis — adapté PFE |
| Scoring multi-critères | Évite la sur-dépendance aux seules compétences listées |
| Explication textuelle | Transparence et confiance (explainable AI light) |
| Module isolé `app/modules/matching/` | Séparation des responsabilités, testable, évolutif |
| API dédiée `/matching` | Démonstration claire pour la soutenance |

---

## 7. Évolutions possibles (perspectives)

- Embeddings sémantiques (Sentence-BERT, OpenAI embeddings)
- Apprentissage supervisé sur historique d'embauches
- Feedback recruteur pour réentraînement des poids
- Cache Redis des scores pour la montée en charge

---

## 8. Démo jury — scénario recommandé (testé)

1. `GET /matching/pipeline` → étapes + poids 0.35/0.25/0.20/0.10/0.05/0.05
2. `POST /matching/score` → ex. compétences 100%, score global ~67% (« Bonne correspondance »)
3. Login **candidat** → `/candidate/jobs` → Top matches IA
4. Bouton **explication LLM** → compétences manquantes / justification
5. Login **recruteur** → `/recruiter/pipeline` → classement par score

### Offre démo créée pour la soutenance
- Titre : **Full Stack Developer Intern (PFE)**
- Skills : Python, FastAPI, React, PostgreSQL, Docker
- Lieu : Casablanca

---

*MatiousHire — PFE 2026 — Module ML/NLP Matching v1.0.0*
