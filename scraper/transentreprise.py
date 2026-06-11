import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.transentreprise.com"
SITEMAP_URL = f"{BASE_URL}/sitemap/offre.xml"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_listing_urls(limit: int = 10) -> list[str]:
    resp = requests.get(SITEMAP_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml-xml")
    urls = [loc.text.strip() for loc in soup.find_all("loc")]
    urls = [u for u in urls if "auvergne-rhone-alpes" in u]
    return urls[:limit]


def fetch_listing(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        print(f"  ✗ Erreur fetch {url}: {e}")
        return None


def parse_listing(soup: BeautifulSoup, url: str) -> dict:
    fields = _extract_dl_fields(soup)
    return {
        "source": "transentreprise",
        "url": url,
        "id_interne": fields.get("Référence :", ""),
        "reference": fields.get("Référence :", ""),
        "titre": _extract_title(soup),
        "prix": fields.get("Prix :", ""),
        "ca": fields.get("C.A. :", ""),
        "effectif": fields.get("Effectif :", ""),
        "secteurs_activite": _get_secteurs(fields),
        "description": _extract_description(soup),
        "localisation": fields.get("Localisation :", ""),
        "activite": fields.get("Activité exercée :", ""),
        "date_publication": "",
        "photos": _extract_photos(soup),
    }


def _extract_dl_fields(soup: BeautifulSoup) -> dict:
    fields = {}
    dl = soup.find("dl")
    if not dl:
        return fields
    dts = dl.find_all("dt")
    for dt in dts:
        dd = dt.find_next_sibling("dd")
        if dd:
            fields[dt.get_text(strip=True)] = dd.get_text(separator=" ", strip=True)
    return fields


def _extract_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1", class_="block-title")
    if h1:
        b = h1.find("b")
        return b.get_text(strip=True) if b else h1.get_text(strip=True)
    return ""


def _extract_description(soup: BeautifulSoup) -> str:
    article = soup.find("article", class_="text-annonce")
    return article.get_text(separator=" ", strip=True) if article else ""


def _get_secteurs(fields: dict) -> str:
    return fields.get("Secteurs d'activité :", "") or fields.get("Secteur d'activité :", "")


def _extract_photos(soup: BeautifulSoup) -> list[str]:
    photos = []
    # src contient l'URL encodée : img?mode=1&w=855&...&url=%2FOffres%2F...
    for img in soup.find_all("img", src=re.compile(r"mode=1.*w=855")):
        src = img.get("src", "")
        photos.append(BASE_URL + src if src.startswith("/") else src)
    return photos


def scrape_all(limit: int = 10, delay: float = 1.5) -> list[dict]:
    print("Récupération des URLs depuis le sitemap transentreprise...")
    urls = get_listing_urls(limit=limit)
    print(f"  → {len(urls)} annonces trouvées\n")

    results = []
    for i, url in enumerate(urls, 1):
        ref = url.split("/fiche/")[1].split("/")[0] if "/fiche/" in url else url
        print(f"[{i}/{len(urls)}] {ref}")
        soup = fetch_listing(url)
        if soup:
            data = parse_listing(soup, url)
            results.append(data)
            print(f"  ✓ {data.get('titre', '—')[:60]}")
        time.sleep(delay)

    return results
