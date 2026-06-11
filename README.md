# WooCommerce Scraper

Scraper d'annonces de cession de fonds de commerce en Auvergne-Rhône-Alpes, avec export Excel et import WooCommerce (à venir).

**Sources** :
- [LesAnnoncesduCommerce.fr](https://www.lesannoncesducommerce.fr)
- [Transentreprise.com](https://www.transentreprise.com)

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

# Une seule source
python main.py --source lesannonces --limit 10
python main.py --source transentreprise --limit 10

# Les deux sources dans un seul Excel
python main.py --source all --limit 20

deactivate
```

Le fichier Excel est généré dans `exports/annonces_{source}_YYYYMMDD_HHMMSS.xlsx`.

## Structure

```
main.py                    ← point d'entrée CLI (flag --source)
scraper/
  lesannonces.py           ← sitemap + fetch + parse LesAnnoncesduCommerce
  transentreprise.py       ← sitemap + fetch + parse Transentreprise
  exporter.py              ← génère le fichier Excel
exports/                   ← fichiers Excel générés
requirements.txt
.env.example               ← credentials WooCommerce (à configurer)
```

## Champs extraits

| Champ | LesAnnonces | Transentreprise |
|-------|-------------|-----------------|
| Titre | ✓ | ✓ |
| Référence | ✓ | ✓ |
| Prix | ✓ | ✓ |
| C.A. | — | ✓ |
| Effectif | — | ✓ |
| Secteur d'activité | — | ✓ |
| Description | ✓ | ✓ |
| Date publication | ✓ | — |
| Localisation | ✓ | ✓ |
| Activité | ✓ | ✓ |
| Photos | ✓ | ✓ |

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
