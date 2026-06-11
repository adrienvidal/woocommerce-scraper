import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.lesannoncesducommerce.fr"
SITEMAP_URL = f"{BASE_URL}/sitemap-ads-1.xml"

# Départements de la région Auvergne-Rhône-Alpes
AUVERGNE_RHONE_ALPES_DEPTS = {"01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_listing_urls(sitemap_url: str = SITEMAP_URL, limit: int = 10) -> list[str]:
    resp = requests.get(sitemap_url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml-xml")
    urls = [loc.text.strip() for loc in soup.find_all("loc")]

    # Garder uniquement les annonces fonds-de-commerce en Auvergne-Rhône-Alpes
    urls = [u for u in urls if "fonds-de-commerce" in u and _is_auvergne_rhone_alpes(u)]
    return urls[:limit]


def _is_auvergne_rhone_alpes(url: str) -> bool:
    # URL pattern: annonce,fonds-de-commerce,{69-rhone},{ville},...
    parts = url.rstrip("/").split(",")
    if len(parts) >= 3:
        dept_code = parts[2].split("-")[0]
        return dept_code in AUVERGNE_RHONE_ALPES_DEPTS
    return False


def fetch_listing(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        print(f"  ✗ Erreur fetch {url}: {e}")
        return None


def scrape_all(limit: int = 10, delay: float = 1.5) -> list[dict]:
    print(f"Récupération des URLs depuis le sitemap...")
    urls = get_listing_urls(limit=limit)
    print(f"  → {len(urls)} annonces trouvées\n")

    from scraper.parser import parse_listing

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url.split(',')[-2]}")
        soup = fetch_listing(url)
        if soup:
            data = parse_listing(soup, url)
            results.append(data)
            print(f"  ✓ {data.get('titre', '—')[:60]}")
        time.sleep(delay)

    return results
