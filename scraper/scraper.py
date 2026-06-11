import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.lesannoncesducommerce.fr"
SITEMAP_URL = f"{BASE_URL}/sitemap-ads-1.xml"

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

    # Garder uniquement les annonces fonds-de-commerce
    urls = [u for u in urls if "fonds-de-commerce" in u]
    return urls[:limit]


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
