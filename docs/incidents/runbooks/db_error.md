# Runbook : Erreur Base de Données

## Symptômes

- `/health` retourne `{"database": "error"}`
- Endpoints data retournent 500
- Logs : "connection refused", "timeout", "authentication failed"

## Diagnostic

### 1. Vérifier Supabase

1. Aller sur https://supabase.com/dashboard
2. Sélectionner le projet DeepPilot
3. Vérifier :
   - Project Status (doit être "Active")
   - Database > Connection Pooling

### 2. Vérifier les credentials

```bash
# Sur Render > Environment
# Vérifier que ces variables sont correctes :
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...  # Format JWT
SUPABASE_DB_URL=postgresql://postgres.xxx:password@aws-0-eu-west-1.pooler.supabase.com:5432/postgres
```

### 3. Causes possibles

| Cause | Symptôme |
|-------|----------|
| Projet Supabase pausé | "Project paused" sur dashboard |
| Mauvaise URL de connexion | "host not found" |
| Pool de connexion saturé | "too many connections" |
| Credentials expirés | "authentication failed" |

## Résolution

### Projet Supabase pausé

Les projets inactifs sont pausés après 7 jours (free tier).

1. Aller sur Supabase Dashboard
2. Cliquer sur "Restore Project"
3. Attendre ~2 minutes

### Mauvaise URL de connexion

Utiliser l'URL **Session Pooler** (pas Direct) :

```
# Correct (Session Pooler - IPv4 compatible)
postgresql://postgres.xxx:password@aws-0-eu-west-1.pooler.supabase.com:5432/postgres

# Incorrect (Direct - IPv6 seulement)
postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

Mettre à jour sur Render > Environment > `SUPABASE_DB_URL`

### Pool saturé

1. Redémarrer le service Render (Manual Deploy > Clear cache)
2. Si récurrent, réduire le nombre de connexions dans le code

### Credentials expirés

1. Aller sur Supabase > Settings > API
2. Copier la nouvelle `anon key`
3. Mettre à jour `SUPABASE_KEY` sur Render

## Vérification

```bash
# Tester la connexion
curl https://deeppilote.onrender.com/health

# Doit retourner :
{"status":"ok","database":"ok","version":"1.0.0"}
```

## Prévention

- Activer les alertes email Supabase pour les pauses
- Garder un ping régulier sur l'API (via UptimeRobot)
