# Registre des Traitements de Données - DeepPilot

> Document requis par l'article 30 du RGPD (Règlement Général sur la Protection des Données)

**Dernière mise à jour** : Mai 2026

---

## 1. Identification du responsable de traitement

| Champ | Valeur |
|-------|--------|
| **Responsable** | Raphaël Martin |
| **Qualité** | Étudiant Bachelor Data & IA, ECE Paris |
| **Email** | [à compléter] |
| **Adresse** | [à compléter] |

---

## 2. Traitements de données

### 2.1 Traitement principal : Analyse financière

| Champ | Description |
|-------|-------------|
| **Nom du traitement** | Collecte et analyse de données financières publiques |
| **Finalité** | Projet éducatif de copilote d'allocation d'actifs |
| **Base légale** | Intérêt légitime (article 6.1.f RGPD) |
| **Catégories de données** | Données financières publiques (prix ETF, indicateurs macro) |
| **Personnes concernées** | Aucune personne physique (données de marché uniquement) |
| **Destinataires** | Usage interne uniquement (projet académique) |
| **Transferts hors UE** | Non |
| **Durée de conservation** | Illimitée (données publiques, pas de données personnelles) |
| **Mesures de sécurité** | Voir section 4 |

### 2.2 Traitement secondaire : Logs techniques

| Champ | Description |
|-------|-------------|
| **Nom du traitement** | Journalisation des accès API |
| **Finalité** | Monitoring, débogage, détection d'anomalies |
| **Base légale** | Intérêt légitime (sécurité du système) |
| **Catégories de données** | Adresses IP, timestamps, endpoints appelés |
| **Personnes concernées** | Utilisateurs de l'API |
| **Destinataires** | Administrateur système uniquement |
| **Transferts hors UE** | Non (hébergement Supabase EU) |
| **Durée de conservation** | 30 jours |
| **Mesures de sécurité** | Accès restreint, pas de corrélation avec identité |

---

## 3. Sources de données

### 3.1 Données financières (pas de données personnelles)

| Source | Type | Fréquence | Données |
|--------|------|-----------|---------|
| Yahoo Finance (yfinance) | API REST | Quotidienne | Prix ETF ajustés |
| FRED (Federal Reserve) | API REST | Quotidienne | Indicateurs macro (VIX, taux, etc.) |
| INSEE | Fichier CSV | Ponctuelle | Inflation EU |
| BCE | Fichier CSV | Ponctuelle | Taux directeur |

**Note** : Toutes ces données sont publiques et ne contiennent aucune donnée personnelle.

### 3.2 Données techniques (logs)

| Donnée | Finalité | Conservation |
|--------|----------|--------------|
| Adresse IP | Rate limiting, sécurité | 30 jours |
| Timestamp | Monitoring | 30 jours |
| User-Agent | Stats techniques | 30 jours |

---

## 4. Mesures de sécurité

### 4.1 Sécurité technique

| Mesure | Implémentation |
|--------|----------------|
| **Chiffrement en transit** | HTTPS obligatoire (TLS 1.3) |
| **Chiffrement au repos** | Supabase encryption at rest |
| **Authentification DB** | Credentials en variables d'environnement |
| **Rate limiting** | 100 requêtes/minute par IP |
| **Validation des entrées** | Pydantic schemas, sanitization |

### 4.2 Sécurité organisationnelle

| Mesure | Description |
|--------|-------------|
| **Principe du moindre privilège** | Accès DB restreint aux opérations nécessaires |
| **Séparation des environnements** | Dev / Prod séparés |
| **Gestion des secrets** | Fichier .env gitignored |
| **Monitoring** | Logs d'accès, alertes anomalies |

---

## 5. Droits des personnes

### 5.1 Données personnelles traitées

**Actuellement : AUCUNE donnée personnelle n'est collectée.**

Le projet ne collecte que :
- Des données financières publiques (prix de marché)
- Des logs techniques minimaux (IP pour rate limiting)

### 5.2 Exercice des droits (si applicable à l'avenir)

| Droit | Procédure |
|-------|-----------|
| Accès (art. 15) | Demande par email au responsable |
| Rectification (art. 16) | Demande par email |
| Effacement (art. 17) | Demande par email |
| Limitation (art. 18) | Demande par email |
| Portabilité (art. 20) | Export JSON sur demande |
| Opposition (art. 21) | Demande par email |

**Délai de réponse** : 1 mois maximum (article 12.3 RGPD)

---

## 6. Sous-traitants

| Sous-traitant | Service | Localisation | Garanties RGPD |
|---------------|---------|--------------|----------------|
| Supabase Inc. | Base de données | EU (Francfort) | DPA signé, certifications |
| Google Cloud | BigQuery | EU | DPA, certifications ISO 27001 |
| Vercel (futur) | Hébergement front | EU | DPA disponible |

---

## 7. Analyse d'impact (AIPD)

### 7.1 Nécessité d'une AIPD

Une Analyse d'Impact sur la Protection des Données n'est **pas requise** car :

1. Pas de traitement à grande échelle de données sensibles
2. Pas de surveillance systématique de personnes
3. Pas de profilage avec effets juridiques
4. Pas de données de personnes vulnérables
5. Données uniquement publiques (marchés financiers)

### 7.2 Risques identifiés

| Risque | Probabilité | Impact | Mesure |
|--------|-------------|--------|--------|
| Fuite de credentials DB | Faible | Élevé | Variables d'env, rotation |
| Accès non autorisé API | Moyen | Faible | Rate limiting, logs |
| Indisponibilité service | Moyen | Faible | Monitoring, alertes |

---

## 8. Historique des modifications

| Date | Modification | Auteur |
|------|--------------|--------|
| Mai 2026 | Création initiale | Raphaël Martin |

---

## 9. Références

- RGPD : Règlement (UE) 2016/679
- CNIL : https://www.cnil.fr/
- Modèle de registre : https://www.cnil.fr/fr/RGDP-le-registre-des-activites-de-traitement
