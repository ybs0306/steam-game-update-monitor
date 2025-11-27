import json
import os
from pathlib import Path

from modules.logger import setup_logging
from modules.steam_cmd import SteamChecker

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
        secrets = load_json(os.path.join(CONFIG_DIR, "secrets.json"))
        targets = load_json(os.path.join(CONFIG_DIR, "targets.json"))

        steamcmd_path = games_config.get("steamcmd_path")
        if not steamcmd_path:
            logger.error("steamcmd_path not configured in games.json")
            return

        if not Path(steamcmd_path).is_file():
            logger.error("steamcmd file is not exist")
            return

        # * Init SteamChecker
        checker = SteamChecker(steamcmd_path)

        games = games_config.get("games", [])

        # * Check every games
        for game in games:
            appid = game.get("appid")
            name = game.get("name", "Unknown Game")

            if not appid:
                continue

            current_build_id = checker.get_build_id(appid)

            if not current_build_id:
                logger.warning(f"Failed to retrieve BuildID for {name}")
                continue

    except FileNotFoundError as fnf_error:
        logger.critical(f"Critical Error: {fnf_error}")
        raise fnf_error

    except Exception as e:
        logger.exception("An unexpected error occurred during execution.")

    logger.info("Check finished.")


if __name__ == "__main__":
    main()
