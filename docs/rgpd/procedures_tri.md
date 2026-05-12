# Procédures TRI (Traitement des Risques et Incidents) — DeepPilot

> **Note** : Ce document sera complété en Phase 2/7 lorsque l'application sera en production.
> Pour l'instant (Phase 1), ces procédures sont préparées mais non actives.

## Statut actuel (Phase 1)

Pas d'utilisateurs, pas de données personnelles → pas de risques RGPD identifiés.

---

## À compléter en phases ultérieures

### 1. Procédure de notification de violation de données

#### Délai
- Notification à la CNIL : 72 heures maximum après découverte
- Notification aux personnes concernées : sans délai injustifié si risque élevé

#### Étapes
1. Identification et confinement de l'incident
2. Évaluation de la gravité
3. Documentation dans le registre des violations
4. Notification CNIL si nécessaire
5. Notification utilisateurs si nécessaire
6. Mesures correctives

#### Formulaire CNIL
https://www.cnil.fr/fr/notifier-une-violation-de-donnees-personnelles

---

### 2. Procédure d'exercice des droits

#### Droits concernés
- Droit d'accès (art. 15 RGPD)
- Droit de rectification (art. 16)
- Droit à l'effacement (art. 17)
- Droit à la portabilité (art. 20)
- Droit d'opposition (art. 21)

#### Délai de réponse
- 1 mois maximum (prolongeable de 2 mois si complexe)

#### Canal de contact
- Email : [à définir]
- Formulaire in-app : [à définir]

---

### 3. Procédure de gestion des sous-traitants

#### Sous-traitants actuels
| Sous-traitant | Service | Localisation | Contrat DPA |
|---------------|---------|--------------|-------------|
| Supabase | BDD | EU (Francfort) | À signer |
| Vercel | Hébergement | US (SCCs) | À vérifier |
| Google Cloud | BigQuery | EU | DPA standard |

#### Vérifications périodiques
- Annuelle : revue des contrats et certifications
- À chaque changement : mise à jour du registre

---

### 4. Analyse d'impact (AIPD)

#### Critères de déclenchement
Une AIPD est requise si le traitement :
- Implique une évaluation systématique (scoring, profilage)
- Traite des données sensibles à grande échelle
- Surveille systématiquement un lieu public

#### Statut DeepPilot
- Phase 1-5 : AIPD non requise (pas de données personnelles)
- Phase 6+ : À évaluer selon les fonctionnalités

---

## Contacts

| Rôle | Nom | Email |
|------|-----|-------|
| Responsable de traitement | [À définir] | - |
| DPO (si applicable) | [À définir] | - |
| Contact technique | Raphaël Martin | - |

---

## Références

- Guide CNIL AIPD : https://www.cnil.fr/fr/RGPD-analyse-impact-protection-des-donnees-aipd
- Notification violations : https://www.cnil.fr/fr/les-violations-de-donnees-personnelles
