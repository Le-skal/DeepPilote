# Veille Technique — Services IA pour Sentiment Analysis

**Date** : 4 juillet 2026
**Auteur** : Raphaël Martin
**Compétences** : C6 (veille technique), C7 (identifier services IA)

---

## 1. Contexte et Objectif

### 1.1 Besoin

Le projet DeepPilot nécessite un module d'analyse de sentiment pour :
- Analyser des headlines financiers
- Extraire un score de sentiment [-1, 1]
- Intégrer ce score comme feature dans le modèle ML

### 1.2 Critères de sélection

| Critère | Importance | Justification |
|---------|------------|---------------|
| **Conformité RGPD** | Critique | Projet académique EU, données potentiellement sensibles |
| **Coût** | Haute | Budget limité (~5€ pour le projet) |
| **Qualité** | Haute | Doit comprendre le jargon financier |
| **Latence** | Moyenne | Batch processing acceptable |
| **Facilité d'intégration** | Moyenne | API REST préférée |

---

## 2. Services IA Analysés

### 2.1 OpenAI (GPT-4 / GPT-3.5)

**Description** : Leader du marché, modèles GPT très performants.

| Aspect | Évaluation |
|--------|------------|
| Qualité | ⭐⭐⭐⭐⭐ Excellent |
| Coût | ⭐⭐ ~$0.01/1k tokens (GPT-3.5) |
| RGPD | ⭐⭐ Serveurs US, opt-out possible |
| Latence | ⭐⭐⭐⭐ Rapide |
| Documentation | ⭐⭐⭐⭐⭐ Excellente |

**Avantages** :
- Meilleure qualité de compréhension
- Écosystème mature
- Beaucoup d'exemples disponibles

**Inconvénients** :
- Serveurs principalement aux US
- Coût élevé pour gros volumes
- Politique de données moins claire pour RGPD

---

### 2.2 Mistral AI

**Description** : Startup française, modèles open-weight, serveurs EU.

| Aspect | Évaluation |
|--------|------------|
| Qualité | ⭐⭐⭐⭐ Très bon |
| Coût | ⭐⭐⭐⭐⭐ ~$0.002/1k tokens |
| RGPD | ⭐⭐⭐⭐⭐ Serveurs EU, conforme |
| Latence | ⭐⭐⭐⭐ Rapide |
| Documentation | ⭐⭐⭐⭐ Bonne |

**Avantages** :
- **RGPD natif** : Entreprise française, serveurs en Europe
- **5x moins cher** que OpenAI
- Modèles performants (Mistral-7B, Mixtral-8x7B)
- API compatible OpenAI (facile à migrer)

**Inconvénients** :
- Écosystème moins mature
- Moins d'exemples dans la communauté

---

### 2.3 HuggingFace Inference API

**Description** : Plateforme open-source, modèles variés.

| Aspect | Évaluation |
|--------|------------|
| Qualité | ⭐⭐⭐ Variable selon modèle |
| Coût | ⭐⭐⭐⭐ Gratuit (limité) à payant |
| RGPD | ⭐⭐⭐ Dépend de l'hébergement |
| Latence | ⭐⭐⭐ Variable |
| Documentation | ⭐⭐⭐⭐ Bonne |

**Avantages** :
- Accès à des modèles spécialisés (FinBERT)
- Tier gratuit disponible
- Possibilité d'auto-hébergement

**Inconvénients** :
- Qualité variable
- Rate limits sur tier gratuit
- Nécessite plus de configuration

---

### 2.4 FinBERT (HuggingFace)

**Description** : BERT fine-tuné sur textes financiers.

| Aspect | Évaluation |
|--------|------------|
| Qualité | ⭐⭐⭐⭐⭐ Excellent pour finance |
| Coût | ⭐⭐⭐⭐⭐ Gratuit (self-hosted) |
| RGPD | ⭐⭐⭐⭐⭐ Contrôle total |
| Latence | ⭐⭐⭐ Dépend du hardware |
| Documentation | ⭐⭐⭐ Moyenne |

**Avantages** :
- Spécialisé finance
- Gratuit
- Contrôle total des données

**Inconvénients** :
- Nécessite GPU pour inférence rapide
- Plus complexe à déployer
- Limité au sentiment (pas de génération)

---

### 2.5 Google Vertex AI

**Description** : Suite ML Google Cloud avec PaLM/Gemini.

| Aspect | Évaluation |
|--------|------------|
| Qualité | ⭐⭐⭐⭐ Très bon |
| Coût | ⭐⭐⭐ Comparable OpenAI |
| RGPD | ⭐⭐⭐⭐ Options EU disponibles |
| Latence | ⭐⭐⭐⭐ Rapide |
| Documentation | ⭐⭐⭐⭐ Bonne |

**Avantages** :
- Intégration GCP (déjà utilisé pour BigQuery)
- Options de région EU

**Inconvénients** :
- Configuration plus complexe
- Coût similaire à OpenAI

---

## 3. Tableau Comparatif

| Service | RGPD | Coût/1k tokens | Qualité | Complexité |
|---------|------|----------------|---------|------------|
| OpenAI GPT-3.5 | ⚠️ | $0.010 | ⭐⭐⭐⭐⭐ | Facile |
| **Mistral** | ✅ | **$0.002** | ⭐⭐⭐⭐ | Facile |
| HuggingFace | ⚠️ | Variable | ⭐⭐⭐ | Moyen |
| FinBERT | ✅ | Gratuit | ⭐⭐⭐⭐⭐ | Complexe |
| Vertex AI | ✅ | $0.008 | ⭐⭐⭐⭐ | Moyen |

---

## 4. Choix Final : Mistral AI

### 4.1 Justification

**Mistral AI** est le meilleur choix pour DeepPilot car :

1. **Conformité RGPD** (critique)
   - Entreprise française basée à Paris
   - Serveurs en Europe
   - Politique de données claire
   - Aligné avec les exigences du projet académique

2. **Coût optimal**
   - 5x moins cher que OpenAI
   - Budget total estimé : ~0.20€ pour 1000 headlines
   - Permet d'expérimenter sans contrainte budgétaire

3. **Qualité suffisante**
   - Mistral-7B-Instruct performant pour classification
   - Comprend le contexte financier
   - Réponses structurées (JSON) possibles

4. **Facilité d'intégration**
   - SDK Python officiel (`mistralai`)
   - API compatible OpenAI (migration facile si besoin)
   - Documentation claire

### 4.2 Modèle sélectionné

**`mistral-small-latest`** (anciennement Mistral-7B-Instruct)

- Suffisant pour classification de sentiment
- Latence < 1s
- Coût minimal

### 4.3 Alternative de backup

Si Mistral indisponible :
1. **FinBERT** via HuggingFace (gratuit, offline)
2. **OpenAI GPT-3.5** (qualité supérieure, mais US)

---

## 5. Aspects Réglementaires

### 5.1 RGPD

- **Base légale** : Intérêt légitime (art. 6.1.f)
- **Données traitées** : Headlines publics (pas de données personnelles)
- **Sous-traitant** : Mistral AI (EU)
- **Durée conservation** : Résultats anonymisés, pas de stockage des textes

### 5.2 Propriété intellectuelle

- Headlines analysés = domaine public ou fair use
- Résultats (scores) = créés par le projet
- Pas de problème de PI identifié

---

## 6. Estimation Coûts

| Élément | Quantité | Coût unitaire | Total |
|---------|----------|---------------|-------|
| Headlines | 1000 | ~100 tokens | 100k tokens |
| Mistral small | 100k tokens | $0.002/1k | **$0.20** |

**Budget total Phase 5** : < 1€

---

## 7. Conclusion

Mistral AI est le choix optimal pour DeepPilot :
- ✅ RGPD compliant (entreprise française)
- ✅ Coût minimal (~0.20€)
- ✅ Qualité suffisante pour sentiment
- ✅ Intégration simple (SDK Python)

Ce choix valide les compétences :
- **C6** : Veille technique documentée
- **C7** : Benchmark de 5 services IA réalisé

---

## Références

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [OpenAI Pricing](https://openai.com/pricing)
- [FinBERT Paper](https://arxiv.org/abs/1908.10063)
- [RGPD Article 6](https://eur-lex.europa.eu/eli/reg/2016/679)

---

**Document créé le 4 juillet 2026**
