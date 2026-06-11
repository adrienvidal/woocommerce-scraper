import re
from bs4 import BeautifulSoup


def parse_listing(soup: BeautifulSoup, url: str) -> dict:
    return {
        "url": url,
        "id_interne": _extract_id(url),
        "titre": _extract_title(soup),
        "reference": _extract_reference(soup),
        "prix": _extract_price(soup),
        "description": _extract_description(soup),
        "date_publication": _extract_date(soup),
        "localisation": _extract_location(url),
        "activite": _extract_activity(url),
        "photos": _extract_photos(soup),
    }


def _extract_id(url: str) -> str:
    # URL pattern: ...,...,550272,...
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
    if p:
        return p.get_text(separator=" ", strip=True)
    return ""


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
    # URL pattern: ...,vente-bar-brasserie-restaurant-paris-1er-75001,...
    parts = url.rstrip("/").split(",")
    if len(parts) >= 5:
        # Enlever la partie localisation à la fin du slug
        slug = parts[4]
        # Retirer le code postal/ville en fin de slug
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
