import argparse
from scraper.scraper import scrape_all
from scraper.exporter import export_to_excel


def main():
    parser = argparse.ArgumentParser(description="Scraper LesAnnoncesduCommerce → Excel")
    parser.add_argument("--limit", type=int, default=10, help="Nombre d'annonces à scraper")
    parser.add_argument("--output", type=str, default=".", help="Dossier de sortie Excel")
    args = parser.parse_args()

    print(f"\n=== Scraper LesAnnoncesduCommerce ===")
    print(f"Limite : {args.limit} annonces\n")

    listings = scrape_all(limit=args.limit)

    if not listings:
        print("\nAucune annonce récupérée.")
        return

    print(f"\n{len(listings)} annonces récupérées. Export Excel...")
    filepath = export_to_excel(listings, output_dir=args.output)
    print(f"✓ Fichier généré : {filepath}\n")


if __name__ == "__main__":
    main()
