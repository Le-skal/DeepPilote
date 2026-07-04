# Runbook : Erreur Modèle ML

## Symptômes

- `/api/v1/ml/regime` retourne des valeurs par défaut (confidence = 0)
- `/api/v1/ml/portfolio` retourne equal weight
- Logs : erreurs Python liées à `hmmlearn`, `scipy`, ou `pandas`

## Diagnostic

### 1. Vérifier le statut du cache

```bash
curl https://deeppilote.onrender.com/api/v1/ml/status
```

Réponse attendue :
```json
{
  "cache_size": 1,
  "cache_ttl_seconds": 21600,
  "cache_ttl_hours": 6.0
}
```

Si `cache_size: 0`, le modèle n'a pas pu être entraîné.

### 2. Vérifier les logs Render

Chercher dans les logs :
- `[ML] Training HMM model...`
- `[ML] Not enough data to train HMM`
- `[ERROR]` suivi d'une exception

### 3. Causes possibles

| Cause | Symptôme |
|-------|----------|
| Pas assez de données | "Not enough data" dans les logs |
| Erreur de données | NaN, valeurs manquantes |
| Erreur HMM | Exception `hmmlearn` |
| Timeout entraînement | Request timeout (>30s) |

## Résolution

### Pas assez de données

Le modèle nécessite au moins 100 jours de données.

1. Vérifier que les tables `macro_indicators` et `etf_prices` ont des données récentes
2. Lancer le script de mise à jour des données si nécessaire

### Erreur de données (NaN)

1. Vérifier les données en base
2. Identifier les valeurs manquantes
3. Exécuter le script de nettoyage

### Forcer le réentraînement

```bash
curl -X POST https://deeppilote.onrender.com/api/v1/ml/refresh
```

Puis vérifier :
```bash
curl https://deeppilote.onrender.com/api/v1/ml/regime
```

### Timeout entraînement

Si l'entraînement prend trop de temps :

1. Réduire la quantité de données (modifier `days` dans `ml_service.py`)
2. Ou upgrader le plan Render (plus de CPU)

## Vérification

```bash
# Vérifier le régime
curl https://deeppilote.onrender.com/api/v1/ml/regime

# Doit retourner confidence > 0 :
{
  "regime": "bull",
  "confidence": 0.85,
  ...
}
```

## Fallback

Si le ML ne fonctionne pas, l'API retourne des valeurs par défaut :
- Régime : "stable" avec confidence 0
- Portfolio : equal weight (12.5% par ETF)

Cela permet au frontend de continuer à fonctionner.
