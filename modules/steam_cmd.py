import logging
import os
import re
import subprocess

logger = logging.getLogger("SteamMonitor")


class SteamChecker:
    def __init__(self, steamcmd_path):
        self.steamcmd_path = steamcmd_path

    def get_build_id(self, appid):
        """
        call steamcmd get app_info & parser buildid
        """
        logger.info(f"Checking BuildID for AppID: {appid}...")

        cmd = [
            self.steamcmd_path,
            "+login", "anonymous",
            "+app_info_update", "1",  # force update info
            "+app_info_print", str(appid),
            "+quit"
        ]

        try:
            # Execute the instruction and capture the output
            # creationflags=0x08000000 can hide the console window popup on Windows (CREATE_NO_WINDOW)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            raw_out, raw_err = process.communicate()

            if process.returncode != 0:
                logger.error(f"SteamCMD error: {process.stderr}")
                return None

            try:
                output = raw_out.decode("utf-8")
            except UnicodeDecodeError:
                output = raw_out.decode("utf-8", errors="replace")

        except Exception as e:
            logger.error(f"Exception checking {appid}: {e}")
            return None
