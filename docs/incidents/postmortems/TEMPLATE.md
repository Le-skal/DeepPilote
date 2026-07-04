# Post-Mortem : [Titre de l'incident]

**Date de l'incident** : YYYY-MM-DD
**Durée** : X heures Y minutes
**Niveau** : P1 / P2
**Auteur** : [Nom]

---

## Résumé

[Description en 2-3 phrases de ce qui s'est passé]

---

## Timeline

| Heure (UTC) | Événement |
|-------------|-----------|
| HH:MM | Première alerte reçue (source) |
| HH:MM | Début de l'investigation |
| HH:MM | Cause identifiée |
| HH:MM | Fix déployé |
| HH:MM | Service restauré |
| HH:MM | Monitoring confirme résolution |

---

## Impact

- **Utilisateurs affectés** : [nombre ou pourcentage]
- **Fonctionnalités impactées** : [liste]
- **Durée d'indisponibilité** : [durée]

---

## Cause racine

[Description détaillée de ce qui a causé l'incident]

### Pourquoi c'est arrivé (5 Whys)

1. Pourquoi le service était down ?
   → [Réponse]
2. Pourquoi [réponse précédente] ?
   → [Réponse]
3. Pourquoi [réponse précédente] ?
   → [Réponse]
4. Pourquoi [réponse précédente] ?
   → [Réponse]
5. Pourquoi [réponse précédente] ?
   → [Cause racine]

---

## Résolution

[Ce qui a été fait pour résoudre l'incident]

```bash
# Commandes exécutées si pertinent
```

---

## Leçons apprises

### Ce qui a bien fonctionné

- [Point positif 1]
- [Point positif 2]

### Ce qui peut être amélioré

- [Point d'amélioration 1]
- [Point d'amélioration 2]

---

## Actions de suivi

| Action | Responsable | Deadline | Status |
|--------|-------------|----------|--------|
| [Action 1] | [Nom] | YYYY-MM-DD | ⏳ En cours |
| [Action 2] | [Nom] | YYYY-MM-DD | ✅ Terminé |

---

## Métriques de réponse

- **Temps de détection (TTD)** : X min (temps entre début incident et première alerte)
- **Temps de réponse (TTR)** : X min (temps entre alerte et début investigation)
- **Temps de résolution (TTM)** : X min (temps entre début investigation et résolution)
