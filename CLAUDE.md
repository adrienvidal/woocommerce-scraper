# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Scraper d'annonces de cession de fonds de commerce depuis deux sources :
- [LesAnnoncesduCommerce.fr](https://www.lesannoncesducommerce.fr)
- [Transentreprise.com](https://www.transentreprise.com)

Export Excel, et (plus tard) import WooCommerce via REST API.

**Contexte** : MVP de démo client. Priorité à la simplicité sur la robustesse.

## Stack

- **Python 3.11+** avec virtualenv `.venv`
- **requests + BeautifulSoup4 + lxml** — scraping HTML statique (pas de JS rendering nécessaire)
- **openpyxl** — export Excel
- **woocommerce** (SDK officiel) — import WooCommerce, à brancher plus tard

## Architecture

```
main.py                    ← point d'entrée CLI (flag --source)
scraper/
  lesannonces.py           ← sitemap + fetch + parse LesAnnoncesduCommerce
  transentreprise.py       ← sitemap + fetch + parse Transentreprise
  exporter.py              ← génère le fichier Excel
requirements.txt
.env.example               ← variables WooCommerce (non branché pour l'instant)
```

## Lancer le scraper

```bash
source .venv/bin/activate

# Une seule source
python main.py --source lesannonces --limit 10
python main.py --source transentreprise --limit 10

# Les deux sources dans un seul Excel
python main.py --source all --limit 20
```

L'export Excel est généré dans `exports/annonces_{source}_YYYYMMDD_HHMMSS.xlsx`.

## Source des URLs — LesAnnoncesduCommerce

Le site expose un sitemap structuré :
- `https://www.lesannoncesducommerce.fr/sitemap-ads-1.xml` (et -2, -3, -4)
- URLs d'annonces au format : `annonce,fonds-de-commerce,{dept},{ville},{slug},{id},offre-prix`

**Filtres actifs** :
- Type : `fonds-de-commerce` (présence dans l'URL)
- Région : **Auvergne-Rhône-Alpes** — filtrage par codes département (`01`, `03`, `07`, `15`, `26`, `38`, `42`, `43`, `63`, `69`, `73`, `74`) extrait du segment `{dept}` de l'URL (ex: `69-rhone`)

## Source des URLs — Transentreprise

- Sitemap : `https://www.transentreprise.com/sitemap/offre.xml`
- URLs au format : `/offres/fiche/{REF}/{slug}/{region}/{dept}/{territoire}`
- Filtre : présence de `auvergne-rhone-alpes` dans l'URL

## Champs extraits

| Champ | LesAnnonces | Transentreprise |
|-------|-------------|-----------------|
| Titre | `h1` | `h1.block-title > b` |
| Référence | `span` "Référence :" | `dl > dt/dd` |
| Prix | `div.bg-ladc-turquoise-100` | `dl > dt/dd` |
| C.A. | — | `dl > dt/dd` |
| Effectif | — | `dl > dt/dd` |
| Secteur d'activité | — | `dl > dt/dd` |
| Description | `p.text.p-lg` | `article.text-annonce` |
| Date publication | `div.bg-ladc-turquoise-100` | — |
| Localisation | Extrait de l'URL | `dl > dt/dd` |
| Activité | Extrait de l'URL | `dl > dt/dd` |
| Photos | `img` dans `.splide__slide` | `img[src*="mode=1&w=855"]` |
| ID interne | Extrait de l'URL | Référence |

## WooCommerce (à brancher)

Les credentials vont dans `.env` (voir `.env.example`). Le connecteur sera dans `scraper/woo_client.py`.

```env
WC_URL=https://votre-site.com
WC_KEY=ck_xxxxxxxxxxxx
WC_SECRET=cs_xxxxxxxxxxxx
```

## Scraping Skill (Bright Data)

Le `/scrape` skill ([.claude/skills/scrape/SKILL.md](.claude/skills/scrape/SKILL.md)) est disponible mais non nécessaire — les deux sites sont en HTML statique sans protection anti-bot agressive.

```bash
bash .claude/skills/scrape/scripts/scrape.sh "https://example.com"
```
