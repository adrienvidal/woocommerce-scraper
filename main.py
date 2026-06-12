import argparse
import time
from pathlib import Path
from scraper.exporter import export_to_excel


def main():
    parser = argparse.ArgumentParser(description="Scraper annonces cession → Excel")
    parser.add_argument("--limit", type=int, default=10, help="Nombre d'annonces à scraper")
    parser.add_argument("--output", type=str, default="exports", help="Dossier de sortie Excel")
    parser.add_argument(
        "--source",
        choices=["lesannonces", "transentreprise", "all"],
        default="lesannonces",
        help="Source à scraper (défaut: lesannonces)",
    )
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)

    start = time.time()
    listings = []

    if args.source in ("lesannonces", "all"):
        from scraper.lesannonces import scrape_all as scrape_lesannonces
        print(f"\n=== LesAnnoncesduCommerce ===")
        listings += scrape_lesannonces(limit=args.limit)

    if args.source in ("transentreprise", "all"):
        from scraper.transentreprise import scrape_all as scrape_transentreprise
        print(f"\n=== Transentreprise ===")
        listings += scrape_transentreprise(limit=args.limit)

    if not listings:
        print("\nAucune annonce récupérée.")
        return

    print(f"\n{len(listings)} annonces récupérées. Export Excel...")
    filepath = export_to_excel(listings, output_dir=args.output, source=args.source)
    elapsed = time.time() - start
    print(f"✓ Fichier généré : {filepath}")
    print(f"  Temps écoulé : {elapsed:.1f}s\n")


if __name__ == "__main__":
    main()
