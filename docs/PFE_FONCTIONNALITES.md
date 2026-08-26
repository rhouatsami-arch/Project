# Fonctionnalités principales — Plateforme RH intelligente (PFE 2026)

## Rôles utilisateurs

### Candidat / Étudiant
- Créer un compte et compléter le profil
- Déposer un CV (PDF, DOCX, TXT)
- Consulter les offres recommandées par IA
- Comprendre **pourquoi** une offre correspond (explication LLM)

### Recruteur
- Créer un compte et publier des offres
- Consulter les candidats classés par score de matching
- Visualiser les scores et explications IA
- Planifier des réunions d'entretien

### Administrateur
- Superviser la plateforme (`/admin/dashboard`)
- Gérer et consulter les utilisateurs
- Suivre les performances (stats, journaux d'audit)

---

## Fonctionnalités implémentées

| Fonctionnalité | Endpoint / Page |
|----------------|-----------------|
| Inscription / connexion | `/login`, `/auth/*` |
| Rôles candidat, recruteur, admin | JWT + cartes login |
| Profil candidat | `/student/profile`, `/candidate/profile` |
| Upload CV | `POST /students/me/cv` |
| Extraction CV | `GET /me/cv/extracted` |
| CRUD offres | `/jobs`, `/recruiter/jobs` |
| Score matching | `/matching/score`, `/matching/pipeline` |
| Pipeline IA tracé | `POST /matching/pipeline/run` |
| Classement candidats | `/matching/recruiters/jobs/{id}/ranking` + pipeline UI |
| Recommandations | `/matching/*/me/recommendations` |
| Explication IA | `POST /llm/explain` |
| Résumé CV/offre | Module `app/modules/llm/` |
| Dashboard recruteur | `/recruiters/me/dashboard`, `/recruiter/dashboard` |
| Actions pipeline | shortlist / reject / hire + notifications |
| Filtres candidats | recherche, statut, score min. |
| Disponibilités candidat | `/meetings/availability`, `/candidate/interviews` |
| Confirmation / refus / annulation | `/meetings/{id}/confirm|refuse|cancel|reschedule` |
| Notifications | `/llm/*/me/notifications` |
| Historique recommandations | `/llm/*/me/recommendation-history` |
| Dashboard admin | `/admin/dashboard` |

---

## Formule de score (Axe 6)

```
Score = 0.35×compétences + 0.25×expérience + 0.20×sémantique
      + 0.10×formation + 0.05×localisation + 0.05×disponibilité
```

**Approches combinées :**
1. Matching mots-clés + embeddings synonymes
2. TF-IDF + similarité cosinus
3. Explication LLM explicable (aide à la décision)

---

## Compte admin de démo

```
Email: admin@matioushire.com
Password: Password123
```

Créer via Register → Admin sur `/login`.
