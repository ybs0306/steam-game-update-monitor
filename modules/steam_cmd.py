import logging
import os
import re
import subprocess

import vdf

logger = logging.getLogger("SteamMonitor")


class SteamChecker:
    def __init__(self, steamcmd_path):
        self.steamcmd_path = steamcmd_path

    def _extract_json_like_string(self, raw_output):
        """
        Use regular expressions to capture the outermost VDF structure
        string from the cluttered output of SteamCMD
        """
        # ! NOTE: This will grab content from the first `{` to the last `}`
        match = re.search(r"(\{.*\})", raw_output, re.DOTALL)
        if match:
            return match.group(1)
        return None

    def _deserialize_to_object(self, appid, vdf_content_str):
        """
        Deserialize a VDF format string into a Python Dictionary object
        """
        try:
            # * The content block returned by SteamCMD is usually such as { "common": ... }

            # * The standard VDF parser usually expects the format "Key" { ... }
            # * In order to ensure that vdf.loads can be parsed correctly, manually fill in the AppID as the Root Key
            fixed_vdf_str = f'"{appid}" {vdf_content_str}'

            data = vdf.loads(fixed_vdf_str)
            return data
        except Exception as e:
            logger.error(f"Failed to deserialize VDF data: {e}")
            return None

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

            vdf_string = self._extract_json_like_string(output)

            if not vdf_string:
                logger.warning(
                    f"Could not extract VDF structure from output for {appid}")
                return None

            data_obj = self._deserialize_to_object(appid, vdf_string)

            if not data_obj:
                return None

            try:
                # try standard path
                build_id = data_obj.get(str(appid), {}) \
                                   .get("depots", {}) \
                                   .get("branches", {}) \
                                   .get("public", {}) \
                                   .get("buildid")

                if build_id:
                    logger.info(f"Found BuildID for {appid}: {build_id}")
                    return build_id
                else:
                    logger.warning(
                        f"BuildID not found in standard path for {appid}. Dump keys: {data_obj.keys()}")
                    return None

            except KeyError as e:
                logger.error(f"KeyError while traversing VDF object: {e}")
                return None

        except Exception as e:
            logger.error(f"Exception checking {appid}: {e}")
            return None
