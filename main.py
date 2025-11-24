from modules.logger import setup_logging


def main():
    logger = setup_logging()
    logger.info("Starting Steam Update Monitor...")

    logger.info("Check finished.")


if __name__ == "__main__":
    main()
