# DeepPilot — TODO Phase 5 : Service IA tiers (Mistral)

> **Phase actuelle : Phase 5**
> Focus : Intégration Mistral API pour sentiment analysis
> Compétences visées : C6 (veille technique), C7 (identifier services IA), C8 (paramétrer service IA)

---

## Contexte

La Phase 5 ajoute une composante **sentiment de marché** au modèle DeepPilot.
L'objectif est d'utiliser un LLM (Mistral) pour analyser des textes financiers
et extraire un score de sentiment qui sera intégré comme feature ML.

---

## Compétences à valider

### C6 — Veille technique et réglementaire

- [ ] Documenter les services IA de sentiment analysis disponibles
- [ ] Comparer : Mistral, OpenAI, HuggingFace, FinBERT, etc.
- [ ] Justifier le choix de Mistral (EU-based, coût, performance)

### C7 — Identifier services IA préexistants

- [ ] Benchmark des APIs disponibles
- [ ] Évaluer coûts, latence, qualité
- [ ] Documenter les alternatives testées

### C8 — Paramétrer un service d'IA

- [ ] Configurer l'API Mistral
- [ ] Créer les prompts pour sentiment analysis
- [ ] Gérer les erreurs et rate limits
- [ ] Tester sur des exemples financiers

---

## ÉTAPE 0 — Setup [À FAIRE]

### 0.1 Dépendances

- [ ] Ajouter `mistralai` au requirements.txt
- [ ] Vérifier la clé API dans `.env` (MISTRAL_API_KEY)

### 0.2 Structure dossiers

```
ml/
├── sentiment/
│   ├── __init__.py
│   ├── config.py           # Configuration Mistral
│   ├── client.py           # Client Mistral wrapper
│   ├── prompts.py          # Prompts pour sentiment
│   ├── analyzer.py         # SentimentAnalyzer
│   └── news_sources.py     # Sources de news (APIs)
```

---

## ÉTAPE 1 — Veille technique (C6, C7) [À FAIRE]

### 1.1 Comparaison des services

| Service | Avantages | Inconvénients | Coût |
|---------|-----------|---------------|------|
| **Mistral** | EU-based, RGPD, rapide | Moins connu | ~0.002€/1k tokens |
| OpenAI | Qualité, écosystème | US, cher, RGPD? | ~0.01€/1k tokens |
| HuggingFace | Open-source, gratuit | Hébergement requis | Variable |
| FinBERT | Spécialisé finance | Fine-tuning requis | Gratuit |

### 1.2 Justification Mistral

- **RGPD** : Serveurs en Europe, conforme RGPD
- **Coût** : 5x moins cher que OpenAI
- **Performance** : Mistral-7B suffisant pour sentiment
- **Latence** : Réponses rapides (<1s)

### 1.3 Documentation

- [ ] Créer `docs/veille/services_ia_sentiment.md`

---

## ÉTAPE 2 — Client Mistral (C8) [À FAIRE]

### 2.1 Configuration

- [ ] `ml/sentiment/config.py` : modèle, température, max_tokens

### 2.2 Client wrapper

- [ ] `ml/sentiment/client.py` :
  - Connexion API
  - Gestion erreurs (rate limit, timeout)
  - Retry avec backoff

### 2.3 Prompts

- [ ] `ml/sentiment/prompts.py` :
  - Prompt système pour analyse financière
  - Format de réponse structuré (JSON)
  - Exemples few-shot

---

## ÉTAPE 3 — Sentiment Analyzer [À FAIRE]

### 3.1 Analyzer

- [ ] `ml/sentiment/analyzer.py` :
  - `analyze_text(text) -> float` : score [-1, 1]
  - `analyze_batch(texts) -> list[float]`
  - Cache des résultats (éviter appels répétés)

### 3.2 Validation

- [ ] Tester sur exemples connus :
  - "Markets crash amid recession fears" → négatif
  - "S&P 500 reaches all-time high" → positif
  - "Fed holds rates steady" → neutre

---

## ÉTAPE 4 — Sources de News [À FAIRE]

### 4.1 Sources légitimes (pas de scraping)

**Option 1 : API NewsAPI.org**
- 500 requêtes/jour gratuit
- Headlines financiers

**Option 2 : RSS Feeds**
- Yahoo Finance, Reuters, Bloomberg
- Gratuit, légal

**Option 3 : Données simulées**
- Pour le projet académique
- Headlines synthétiques basés sur VIX/rendements

### 4.2 Module news

- [ ] `ml/sentiment/news_sources.py` :
  - `fetch_headlines(date) -> list[str]`
  - Filtrage par ETF/secteur

---

## ÉTAPE 5 — Intégration ML [À FAIRE]

### 5.1 Feature sentiment

- [ ] Ajouter `sentiment_score` dans les features
- [ ] Moyenne mobile du sentiment (5j, 20j)
- [ ] Intégrer dans `prepare_prediction_features()`

### 5.2 Réévaluation modèles

- [ ] Réentraîner RF avec sentiment
- [ ] Comparer AUC avec/sans sentiment
- [ ] Documenter l'impact

---

## ÉTAPE 6 — Tests [À FAIRE]

- [ ] `tests/ml/test_sentiment.py` :
  - Test client Mistral (mock)
  - Test analyzer
  - Test prompts

---

## ÉTAPE 7 — Documentation [À FAIRE]

- [ ] `docs/veille/services_ia_sentiment.md` (C6, C7)
- [ ] `CHECKPOINT_PHASE5.md`
- [ ] Mise à jour `workflow.html`

---

## ✅ Definition of Done — Phase 5

- [ ] Veille documentée (C6)
- [ ] Benchmark services IA (C7)
- [ ] Client Mistral fonctionnel (C8)
- [ ] Sentiment analyzer testé
- [ ] Feature sentiment intégrée
- [ ] Tests passent
- [ ] Documentation complète

---

## Notes importantes

### Pas de scraping

Consigne explicite : pas de BeautifulSoup/Selenium.
On utilise des APIs légitimes ou des données simulées.

### Budget Mistral

Estimation pour le projet :
- ~1000 headlines à analyser
- ~100 tokens/headline
- Coût total : ~0.20€

---

## Prochaine étape

Commencer par l'ÉTAPE 1 (veille technique) pour valider C6 et C7.
