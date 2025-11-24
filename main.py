import json
import os

from modules.logger import setup_logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    logger = setup_logging()
    logger.info("Starting Steam Update Monitor...")

    try:
        # * Load config info
        games_config = load_json(os.path.join(CONFIG_DIR, "games.json"))

    except FileNotFoundError as fnf_error:
        logger.critical(f"Critical Error: {fnf_error}")
        raise fnf_error

    except Exception as e:
        logger.exception("An unexpected error occurred during execution.")

    logger.info("Check finished.")


if __name__ == "__main__":
    main()
