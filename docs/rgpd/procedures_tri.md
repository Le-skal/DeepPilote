# Procédures TRI (Traitement des Risques et Incidents) — DeepPilot

> Document de procédures pour la gestion des incidents de sécurité et l'exercice des droits RGPD.

**Dernière mise à jour** : Mai 2026

---

## 1. Procédure de notification de violation de données

### 1.1 Définition

Une violation de données personnelles est une faille de sécurité entraînant, de manière accidentelle ou illicite :
- La destruction
- La perte
- L'altération
- La divulgation non autorisée
- L'accès non autorisé à des données personnelles

### 1.2 Délais de notification

| Destinataire | Délai | Condition |
|--------------|-------|-----------|
| CNIL | 72 heures | Risque pour les droits des personnes |
| Personnes concernées | Sans délai | Risque élevé pour leurs droits |

### 1.3 Procédure

```
1. DÉTECTION
   └── Identification de l'incident (logs, alertes, signalement)

2. CONFINEMENT (< 1 heure)
   ├── Isolation du système affecté
   ├── Révocation des accès compromis
   └── Préservation des preuves

3. ÉVALUATION (< 24 heures)
   ├── Nature des données affectées
   ├── Nombre de personnes concernées
   ├── Probabilité d'utilisation malveillante
   └── Gravité des conséquences

4. NOTIFICATION (< 72 heures si nécessaire)
   ├── CNIL : https://www.cnil.fr/fr/notifier-une-violation
   └── Personnes concernées (si risque élevé)

5. REMÉDIATION
   ├── Correction de la vulnérabilité
   ├── Mise à jour des mesures de sécurité
   └── Documentation dans le registre des violations

6. BILAN
   └── Analyse post-mortem et amélioration continue
```

### 1.4 Registre des violations

| Date | Description | Données | Personnes | CNIL | Mesures |
|------|-------------|---------|-----------|------|---------|
| - | Aucune violation à date | - | - | - | - |

---

## 2. Procédure d'exercice des droits

### 2.1 Droits concernés

| Droit | Article RGPD | Délai |
|-------|--------------|-------|
| Accès | Art. 15 | 1 mois |
| Rectification | Art. 16 | 1 mois |
| Effacement ("droit à l'oubli") | Art. 17 | 1 mois |
| Limitation | Art. 18 | 1 mois |
| Portabilité | Art. 20 | 1 mois |
| Opposition | Art. 21 | 1 mois |

### 2.2 Canal de demande

**Email** : [à définir]

### 2.3 Procédure de traitement

```
1. RÉCEPTION
   └── Accusé de réception sous 48h

2. VÉRIFICATION IDENTITÉ
   └── Demande de justificatif si doute

3. TRAITEMENT (< 1 mois)
   ├── Recherche des données
   ├── Exécution de la demande
   └── Documentation

4. RÉPONSE
   ├── Communication des données (accès)
   ├── Confirmation d'exécution (rectification, effacement)
   └── Export (portabilité)
```

### 2.4 Cas de refus

Le responsable peut refuser si :
- La demande est manifestement infondée ou excessive
- Les données sont nécessaires pour une obligation légale
- Les données sont nécessaires à la constatation d'un droit en justice

---

## 3. Gestion des sous-traitants

### 3.1 Liste des sous-traitants

| Sous-traitant | Service | Localisation | DPA | Dernière revue |
|---------------|---------|--------------|-----|----------------|
| Supabase Inc. | Base de données PostgreSQL | EU (Francfort) | Oui | Mai 2026 |
| Google Cloud | BigQuery (analytics) | EU | Oui | Mai 2026 |
| Vercel (futur) | Hébergement frontend | EU | À signer | - |

### 3.2 Exigences contractuelles

Chaque sous-traitant doit :
- Signer un DPA (Data Processing Agreement)
- Garantir des mesures de sécurité appropriées
- Ne pas faire appel à un sous-traitant ultérieur sans autorisation
- Notifier les violations sous 48h

### 3.3 Revue périodique

- **Fréquence** : Annuelle
- **Éléments vérifiés** :
  - Certifications à jour (ISO 27001, SOC 2)
  - Localisation des données
  - Mesures de sécurité

---

## 4. Analyse d'impact (AIPD)

### 4.1 Critères de déclenchement

Une AIPD est obligatoire si le traitement présente un risque élevé :

| Critère | DeepPilot |
|---------|-----------|
| Évaluation/scoring systématique | Non |
| Données sensibles à grande échelle | Non |
| Surveillance de lieux publics | Non |
| Croisement de données | Non |
| Personnes vulnérables | Non |

**Conclusion** : AIPD non requise actuellement.

### 4.2 Réévaluation

À réévaluer si :
- Introduction de fonctionnalités de profilage utilisateur
- Collecte de données personnelles sensibles
- Traitement automatisé avec effets significatifs

---

## 5. Contacts

| Rôle | Nom | Email |
|------|-----|-------|
| Responsable de traitement | Raphaël Martin | [à définir] |
| DPO (si applicable) | Raphaël Martin | [à définir] |
| Contact technique | Raphaël Martin | [à définir] |

---

## 6. Références

- [Guide CNIL sur les violations](https://www.cnil.fr/fr/les-violations-de-donnees-personnelles)
- [Notification CNIL](https://www.cnil.fr/fr/notifier-une-violation-de-donnees-personnelles)
- [Guide AIPD](https://www.cnil.fr/fr/RGPD-analyse-impact-protection-des-donnees-aipd)
