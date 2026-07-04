# Runbook : API Down

## Symptômes

- UptimeRobot alerte "API Health DOWN"
- Frontend affiche "Erreur de connexion"
- `/health` ne répond pas ou retourne 500

## Diagnostic

### 1. Vérifier le statut Render

1. Aller sur https://dashboard.render.com
2. Sélectionner le service `deeppilote`
3. Vérifier l'onglet "Events" pour les erreurs récentes

### 2. Vérifier les logs

```bash
# Sur Render Dashboard > Logs
# Chercher les erreurs récentes
```

### 3. Causes possibles

| Cause | Symptôme dans les logs |
|-------|------------------------|
| Cold start | "Starting..." puis timeout |
| Erreur Python | Traceback avec exception |
| DB inaccessible | "connection refused" ou "timeout" |
| Mémoire insuffisante | "OOM" ou "killed" |

## Résolution

### Cold start (Render Free tier)

Le service dort après 15 min d'inactivité.
- **Action** : Attendre ~30 secondes, le service redémarre automatiquement
- **Prévention** : Upgrader vers Render payant ou ajouter un ping périodique

### Erreur Python

1. Identifier l'erreur dans les logs
2. Reproduire localement si possible
3. Fixer et déployer

```bash
git add .
git commit -m "fix: [description]"
git push
# Render redéploie automatiquement
```

### Base de données inaccessible

Voir [db_error.md](db_error.md)

### Mémoire insuffisante

1. Vérifier les métriques mémoire sur Render
2. Optimiser le code (réduire taille des données chargées)
3. Si récurrent, upgrader le plan Render

## Vérification

Après résolution :

1. Tester `/health` manuellement
2. Vérifier que UptimeRobot revient "UP"
3. Tester les endpoints critiques (`/api/v1/ml/regime`)

## Escalade

Si non résolu après 30 min :
- Contacter le support Render
- Considérer un rollback vers la version précédente
