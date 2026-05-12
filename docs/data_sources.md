# Sources de données — DeepPilot

Ce document décrit les sources de données utilisées dans le projet, leur fiabilité, et les points d'attention.

## 1. Yahoo Finance (yfinance)

### Description
API gratuite pour les prix historiques des actions et ETF cotés aux États-Unis.

### Données récupérées
- Prix ajustés (adjusted close) : prend en compte splits et dividendes
- Période : 2010-01-01 → aujourd'hui
- Fréquence : journalière

### ETF téléchargés

| Ticker | Nom | Disponible depuis |
|--------|-----|-------------------|
| SPY | SPDR S&P 500 | 1993 |
| EFA | iShares MSCI EAFE | 2001 |
| EEM | iShares MSCI Emerging Markets | 2003 |
| TLT | iShares 20+ Year Treasury | 2002 |
| HYG | iShares High Yield Corporate | 2007 |
| GLD | SPDR Gold Shares | 2004 |
| VNQ | Vanguard Real Estate | 2004 |
| SH | ProShares Short S&P 500 | 2006 |
| URTH | iShares MSCI World | 2012 |
| QQQ | Invesco QQQ Trust | 1999 |

### Fiabilité
- **Haute** pour les ETF majeurs (SPY, QQQ, etc.)
- Données ajustées automatiquement après splits/dividendes
- Légers retards possibles (fin de journée)

### Points d'attention
- Rate limiting si trop de requêtes
- La colonne "Close" dans yfinance >= 0.2.x est déjà l'adjusted close
- Jours fériés US (NYSE) : pas de données

### URL
https://pypi.org/project/yfinance/

---

## 2. FRED (Federal Reserve Economic Data)

### Description
Base de données économiques de la Federal Reserve Bank of St. Louis. Accès via API avec clé gratuite.

### Données récupérées

| Code FRED | Nom | Fréquence | Description |
|-----------|-----|-----------|-------------|
| VIXCLS | VIX | Daily | Indice de volatilité implicite S&P 500 |
| BAMLH0A0HYM2 | HY Spread | Daily | Spread crédit high yield (BofA) |
| T10Y2Y | Yield Curve | Daily | Spread 10Y - 2Y Treasury |
| DGS3MO | 3-Month Treasury | Daily | Taux sans risque |
| DGS10 | 10-Year Treasury | Daily | Taux long terme |
| DCOILWTICO | WTI Oil | Daily | Prix pétrole brut |
| DEXUSEU | USD/EUR | Daily | Taux de change |
| UNRATE | Unemployment | Monthly | Taux de chômage US |
| CPIAUCSL | CPI | Monthly | Indice des prix à la consommation |

### Fiabilité
- **Très haute** : source officielle de la Fed
- Données révisées parfois a posteriori (notamment CPI, UNRATE)
- Historique long (plusieurs décennies)

### Points d'attention
- Séries mensuelles (UNRATE, CPI) : nécessitent forward-fill pour aligner sur daily
- Certaines séries ont des trous (jours fériés différents de NYSE)
- La courbe de taux T10Y2Y peut être négative (inversion)

### URL
- API : https://fred.stlouisfed.org/docs/api/fred/
- Clé API : https://fred.stlouisfed.org/docs/api/api_key.html

---

## 3. INSEE (Institut National de la Statistique)

### Description
Statistiques officielles françaises. Téléchargement manuel de fichiers CSV.

### Données récupérées
- Inflation zone euro (IPCH)
- Séries mensuelles

### Fiabilité
- **Très haute** : source officielle
- Format CSV parfois complexe (séparateur `;`, encodage `latin-1`)

### Points d'attention
- Téléchargement manuel requis (pas d'API publique simple)
- Format dates variable (YYYY-MM, YYYY-Qx, etc.)
- Encodage souvent `latin-1` ou `windows-1252`

### URL
https://www.insee.fr/fr/statistiques

---

## 4. BCE / ECB (Banque Centrale Européenne)

### Description
Statistiques de la Banque Centrale Européenne. Statistical Data Warehouse.

### Données récupérées
- Taux directeur BCE
- Séries mensuelles/hebdomadaires

### Fiabilité
- **Très haute** : source officielle
- Données disponibles en CSV ou SDMX

### Points d'attention
- Interface de téléchargement complexe
- Plusieurs formats de dates possibles

### URL
https://sdw.ecb.europa.eu/

---

## 5. Google BigQuery

### Description
Entrepôt de données cloud pour requêtes SQL à grande échelle.

### Utilisation dans le projet
- Stockage alternatif pour volumétrie importante
- Tables partitionnées par date
- Requêtes d'agrégation mensuelles

### Fiabilité
- **Très haute** : infrastructure Google Cloud
- Facturation au volume scanné (attention aux coûts)

### Points d'attention
- Nécessite un projet GCP et un service account
- Free tier : 1 TB de requêtes/mois
- Région EU recommandée (RGPD)

### URL
https://console.cloud.google.com/bigquery

---

## Calendrier de mise à jour

| Source | Fréquence MAJ | Meilleur moment |
|--------|---------------|-----------------|
| yfinance | Daily | Après 22h CET (fermeture NYSE) |
| FRED | Daily | Après 21h CET |
| INSEE | Mensuelle | Début de mois |
| BCE | Variable | Vérifier calendrier ECB |

---

## Qualité des données

### Contrôles appliqués
1. **Monotonie temporelle** : index strictement croissant
2. **Plages de validité** : VIX ∈ [0, 150], prix > 0
3. **Détection outliers** : returns > |10%| flaggés
4. **Valeurs manquantes** : forward-fill si gap ≤ 5 jours

### Taux de complétude attendu
- Prix ETF : > 99% (hors weekends/jours fériés)
- VIX, spreads : > 99%
- Séries mensuelles : 100% après forward-fill
