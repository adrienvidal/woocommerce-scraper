# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Scraper d'annonces de cession de fonds de commerce depuis [LesAnnoncesduCommerce.fr](https://www.lesannoncesducommerce.fr), avec export Excel et (plus tard) import WooCommerce via REST API.

**Contexte** : MVP de démo client. Priorité à la simplicité sur la robustesse.

## Stack

- **Python 3.11+** avec virtualenv `.venv`
- **requests + BeautifulSoup4 + lxml** — scraping HTML statique (pas de JS rendering nécessaire)
- **openpyxl** — export Excel
- **woocommerce** (SDK officiel) — import WooCommerce, à brancher plus tard

## Architecture

```
main.py               ← point d'entrée CLI
scraper/
  scraper.py          ← récupère les URLs depuis le sitemap + fetch HTML
  parser.py           ← extrait les champs depuis le HTML BeautifulSoup
  exporter.py         ← génère le fichier Excel
requirements.txt
.env.example          ← variables WooCommerce (non branché pour l'instant)
```

## Lancer le scraper

```bash
source .venv/bin/activate
python main.py --limit 10
```

L'export Excel est généré dans `exports/annonces_YYYYMMDD_HHMMSS.xlsx`.

## Source des URLs

Le site expose un sitemap structuré :
- `https://www.lesannoncesducommerce.fr/sitemap-ads-1.xml` (et -2, -3, -4)
- URLs d'annonces au format : `annonce,fonds-de-commerce,{dept},{ville},{slug},{id},offre-prix`

Le scraper filtre sur `fonds-de-commerce` et lit les URLs depuis `sitemap-ads-1.xml` par défaut.

## Champs extraits par annonce

| Champ | Sélecteur HTML |
|-------|----------------|
| Titre | `h1` |
| Référence | `span` contenant "Référence :" |
| Prix | `div.bg-ladc-turquoise-100` avec label "Prix :" |
| Description | `p.text.p-lg` |
| Date publication | `div.bg-ladc-turquoise-100` avec label "Publiée le :" |
| Localisation | Extrait de l'URL (segment index 3) |
| Activité | Extrait de l'URL (segment index 4) |
| Photos | `img` dans `.splide__slide` |
| ID interne | Extrait de l'URL (premier segment numérique) |

## WooCommerce (à brancher)

Les credentials vont dans `.env` (voir `.env.example`). Le connecteur sera dans `scraper/woo_client.py`.

```env
WC_URL=https://votre-site.com
WC_KEY=ck_xxxxxxxxxxxx
WC_SECRET=cs_xxxxxxxxxxxx
```

## Scraping Skill (Bright Data)

Le `/scrape` skill ([.claude/skills/scrape/SKILL.md](.claude/skills/scrape/SKILL.md)) est disponible mais non nécessaire — le site est en HTML statique sans protection anti-bot agressive.

```bash
bash .claude/skills/scrape/scripts/scrape.sh "https://example.com"
```
