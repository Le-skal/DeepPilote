# DeepPilot — TODO Principal

> **Phase actuelle : Phase 4 terminée**
> Prochaine étape : Phase 5 (Mistral API - Sentiment Analysis)

---

## Progression globale

| Phase | Focus | Status | Compétences |
|-------|-------|--------|-------------|
| Phase 1 | Data + Analyse exploratoire | ✅ Terminée | C1, C2, C3, C4 |
| Phase 2 | API REST + RGPD | ✅ Terminée | C4, C5 |
| Phase 3 | Modèles ML (HMM + RF) | ✅ Terminée | C9, C12 |
| Phase 4 | MLOps (MLflow, monitoring) | ✅ Terminée | C11, C13 |
| Phase 5 | Service IA tiers (Mistral) | ⏳ À faire | C6, C7, C8 |
| Phase 6 | Application Next.js | ⏳ À faire | C14, C15, C17 |
| Phase 7 | CI/CD + monitoring app | ⏳ À faire | C18, C19, C20, C21 |
| Phase 8 | Rapports + soutenance | ⏳ À faire | C16 |

---

## Fichiers TODO par phase

- `TODO_PHASE2.md` - API REST + RGPD (terminée)
- `TODO_PHASE3.md` - Modèles ML (terminée)
- `TODO_PHASE4.md` - MLOps (terminée)

---

## Résumé des résultats

### Phase 3 - ML
- **HMM** : 4 régimes, stabilité 97.9%, détecte correctement les crises
- **Random Forest** : accuracy 55-58%, AUC ~0.51
- **DeepPilot Portfolio** : CAGR 5.59%, Sharpe 0.41, Max DD -17.2%
- **61 tests ML passent**

### Phase 4 - MLOps
- **MLflow tracking** : 4 expériences configurées
- **Model Registry** : versioning des modèles HMM et RF
- **Drift Detection** : PSI + KS test fonctionnels
- **Monitoring** : alertes de performance avec seuils
- **30 tests MLOps passent**
- **182 tests totaux**

---

## Prochaines étapes (Phase 5)

1. Intégration Mistral API pour sentiment analysis
2. Extraction de news financières
3. Score de sentiment par ETF
4. Intégration du sentiment dans les features ML

---

## Documentation clé

- `CLAUDE.md` - Instructions projet pour Claude Code
- `CHECKPOINT_PHASE*.md` - Résumé de chaque phase
- `docs/mlops/README.md` - Guide MLOps complet
