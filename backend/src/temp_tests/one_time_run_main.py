import asyncio

from src.scraping.scraper_registry import init_scraper_registry, run_all_scrapers


def main():
    init_scraper_registry()
    asyncio.run(run_all_scrapers())


if __name__ == "__main__":
    main()
