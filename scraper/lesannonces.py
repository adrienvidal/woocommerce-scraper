import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.lesannoncesducommerce.fr"
SITEMAP_URL = f"{BASE_URL}/sitemap-ads-1.xml"

AUVERGNE_RHONE_ALPES_DEPTS = {"01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"}

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


def parse_listing(soup: BeautifulSoup, url: str) -> dict:
    return {
        "source": "lesannonces",
        "url": url,
        "id_interne": _extract_id(url),
        "reference": _extract_reference(soup),
        "titre": _extract_title(soup),
        "prix": _extract_price(soup),
        "ca": "",
        "effectif": "",
        "secteurs_activite": "",
        "description": _extract_description(soup),
        "localisation": _extract_location(url),
        "activite": _extract_activity(url),
        "date_publication": _extract_date(soup),
        "photos": _extract_photos(soup),
    }


def _extract_id(url: str) -> str:
    parts = url.rstrip("/").split(",")
    for part in reversed(parts):
        if part.isdigit():
            return part
    return ""


def _extract_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""


def _extract_reference(soup: BeautifulSoup) -> str:
    span = soup.find("span", string=re.compile(r"Référence\s*:"))
    if span:
        return span.get_text(strip=True).replace("Référence :", "").strip()
    return ""


def _extract_price(soup: BeautifulSoup) -> str:
    for div in soup.find_all("div", class_=re.compile("bg-ladc-turquoise")):
        strongs = div.find_all("strong")
        if len(strongs) >= 2 and "Prix" in strongs[0].get_text():
            return strongs[1].get_text(strip=True)
    return ""


def _extract_description(soup: BeautifulSoup) -> str:
    p = soup.find("p", class_=re.compile(r"text.*p-lg"))
    return p.get_text(separator=" ", strip=True) if p else ""


def _extract_date(soup: BeautifulSoup) -> str:
    for div in soup.find_all("div", class_=re.compile("bg-ladc-turquoise")):
        strongs = div.find_all("strong")
        if len(strongs) >= 2 and "Publiée" in strongs[0].get_text():
            return strongs[1].get_text(strip=True)
    return ""


def _extract_location(url: str) -> str:
    # URL pattern: annonce,fonds-de-commerce,75-paris,paris-1er-75001,...
    parts = url.rstrip("/").split(",")
    if len(parts) >= 4:
        return parts[3].replace("-", " ").title()
    return ""


def _extract_activity(url: str) -> str:
    parts = url.rstrip("/").split(",")
    if len(parts) >= 5:
        slug = parts[4]
        slug = re.sub(r"-\d{5}$", "", slug)
        slug = re.sub(r"-[a-z]+-\d+.*$", "", slug)
        return slug.replace("-", " ").replace("vente ", "").title().strip()
    return ""


def _extract_photos(soup: BeautifulSoup) -> list[str]:
    photos = []
    for slide in soup.find_all("li", class_="splide__slide"):
        img = slide.find("img")
        if img and img.get("src"):
            photos.append(img["src"])
    return photos


def scrape_all(limit: int = 10, delay: float = 1.5) -> list[dict]:
    print("Récupération des URLs depuis le sitemap lesannoncesducommerce...")
    urls = get_listing_urls(limit=limit)
    print(f"  → {len(urls)} annonces trouvées\n")

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
