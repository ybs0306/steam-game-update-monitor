import requests
import logging

logger = logging.getLogger("SteamMonitor")


class Notifier:
    def __init__(self, secrets, targets):
        self.secrets = secrets
        self.targets = targets

    def send_telegram(self, message):
        token = self.secrets.get("telegram_bot_token")
        chat_ids = self.targets.get("telegram", {}).get("chat_ids", [])

        if not token or not chat_ids:
            logger.warning(
                "Telegram token or chat_ids missing. Skipping notification.")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        for chat_id in chat_ids:
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Telegram notification sent to {chat_id}")
            except Exception as e:
                logger.error(
                    f"Failed to send Telegram message to {chat_id}: {e}")

    def notify(self, app_name, appid, old_build, new_build):
        msg = (
            f"*{app_name}* Game Update Detected.\n"
            f"Old Build: `{old_build}`\n"
            f"New Build: `{new_build}`\n\n"
            f"Update is available on Steam.\n"
            f"https://store.steampowered.com/app/{appid}"
        )

        self.send_telegram(msg)
