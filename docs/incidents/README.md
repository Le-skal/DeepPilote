# Gestion des Incidents — DeepPilot

## Processus de gestion d'incident

### 1. Détection

Les incidents peuvent être détectés via :
- **UptimeRobot** : Alerte email si API ou frontend down
- **Sentry** : Alerte si erreur critique
- **Utilisateur** : Signalement manuel

### 2. Classification

| Niveau | Description | Temps de réponse | Exemple |
|--------|-------------|------------------|---------|
| P1 - Critique | Service totalement indisponible | < 15 min | API down, DB inaccessible |
| P2 - Majeur | Fonctionnalité importante dégradée | < 1h | ML endpoint en erreur |
| P3 - Mineur | Fonctionnalité secondaire affectée | < 4h | Graphique ne s'affiche pas |
| P4 - Cosmétique | Problème visuel, pas d'impact fonctionnel | < 24h | CSS cassé sur mobile |

### 3. Réponse

1. **Acknowledge** : Confirmer la prise en charge
2. **Investigate** : Consulter les logs (Render, Vercel, Sentry)
3. **Mitigate** : Appliquer un fix temporaire si possible
4. **Resolve** : Déployer le fix permanent
5. **Document** : Rédiger le post-mortem (si P1/P2)

### 4. Communication

- **P1/P2** : Notifier immédiatement les parties prenantes
- **P3/P4** : Inclure dans le rapport hebdomadaire

---

## Contacts

| Rôle | Nom | Contact |
|------|-----|---------|
| Développeur principal | Raphaël Martin | [GitHub](https://github.com/Le-skal) |

---

## Outils de monitoring

| Outil | URL | Usage |
|-------|-----|-------|
| Sentry | https://sentry.io | Tracking erreurs |
| UptimeRobot | https://uptimerobot.com | Monitoring uptime |
| Render Dashboard | https://dashboard.render.com | Logs backend |
| Vercel Dashboard | https://vercel.com/dashboard | Logs frontend |

---

## Runbooks

Guides de résolution pour les incidents courants :

- [API Down](runbooks/api_down.md)
- [Erreur Base de Données](runbooks/db_error.md)
- [Erreur Modèle ML](runbooks/ml_error.md)

---

## Post-mortems

Après chaque incident P1/P2, rédiger un post-mortem :

- [Template](postmortems/TEMPLATE.md)
