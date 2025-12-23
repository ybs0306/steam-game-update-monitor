import requests
import logging

from telegram.helpers import escape_markdown


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
                    "parse_mode": "MarkdownV2"
                }
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Telegram notification sent to {chat_id}")
            except Exception as e:
                logger.error(
                    f"Failed to send Telegram message to {chat_id}: {e}")

    def notify(self, app_name, appid, old_build, new_build):
        app_name = escape_markdown(app_name, version=2)
        old_build = escape_markdown(old_build, version=2)
        new_build = escape_markdown(new_build, version=2)

        # Add escape characters according to MarkdownV2 restrictions
        # Characters that need to be escaped include the following:
        # _ * [ ] ( ) ~ ` > # + - = | { } . !
        # https://core.telegram.org/bots/api#markdownv2-style
        msg = (
            f"[*{app_name}*](https://store\.steampowered\.com/app/{appid}) Game Update Detected\.\n"
            f"Old Build: `{old_build}`\n"
            f"New Build: `{new_build}`\n\n"
            f"Update is available on Steam\."
        )

        self.send_telegram(msg)
