# WooCommerce Scraper

Scraper d'annonces de cession de fonds de commerce depuis [LesAnnoncesduCommerce.fr](https://www.lesannoncesducommerce.fr), avec export Excel et import WooCommerce (à venir).

## Prérequis

- Python 3.11+

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Lancer le scraper

```bash
source .venv/bin/activate
python main.py --limit 10
deactivate
```

Le fichier Excel est généré dans `exports/annonces_YYYYMMDD_HHMMSS.xlsx`.

## Structure

```
main.py               ← point d'entrée CLI
scraper/
  scraper.py          ← récupère les URLs depuis le sitemap + fetch HTML
  parser.py           ← extrait les champs depuis le HTML
  exporter.py         ← génère le fichier Excel
exports/              ← fichiers Excel générés
requirements.txt
.env.example          ← credentials WooCommerce (à configurer)
```

## Champs extraits

| Champ | Source |
|-------|--------|
| Titre | `<h1>` |
| Référence | `span` "Référence :" |
| Prix | `div` "Prix :" |
| Description | `p.text.p-lg` |
| Localisation | URL |
| Activité | URL |
| Date publication | `div` "Publiée le :" |
| Photos | `img` dans `.splide__slide` |
| ID interne | URL |

## WooCommerce (à venir)

Copier `.env.example` en `.env` et renseigner les credentials :

```bash
cp .env.example .env
```

```env
WC_URL=https://votre-site.com
WC_KEY=ck_xxxxxxxxxxxx
WC_SECRET=cs_xxxxxxxxxxxx
```
