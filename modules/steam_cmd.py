import logging
import os
import re
import subprocess

import vdf

logger = logging.getLogger("SteamMonitor")


class SteamChecker:
    def __init__(self, steamcmd_path):
        self.steamcmd_path = steamcmd_path
        if not os.path.exists(self.steamcmd_path):
            raise FileNotFoundError(
                f"SteamCMD executable not found at: {self.steamcmd_path}")

    def _extract_vdf_block(self, full_text, start_index):
        """
        Extract a full VDF block starting from a given index (assumed '{'), 
        using brace counting to find the matching closing '}'.

        Args:
            full_text (str): The complete raw text containing VDF data.
            start_index (int): The index position where the opening '{' starts.

        Returns:
            tuple: (vdf_block_str, end_index)
                - vdf_block_str (str or None): The extracted VDF block as a string.
                - end_index (int): The index of the closing '}' plus one, or start_index if failed.
        """
        brace_count = 0
        end_index = -1

        # * Scan from start_index
        for i in range(start_index, len(full_text)):
            char = full_text[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1

                # When brace count reaches zero, outermost closing brace found
                if brace_count == 0:
                    end_index = i + 1  # include closing '}'
                    break

        if end_index != -1:
            return full_text[start_index:end_index], end_index

        # * If ending brace not found (incomplete data), return None and original start index
        return None, start_index

    def _parse_batch_output(self, raw_output):
        """
        Parse batch output from SteamCMD using a cursor to skip already processed blocks.

        Args:
            raw_output (str): The raw string output from SteamCMD.

        Returns:
            dict: A mapping of { "appid": "buildid", ... }
        """
        results = {}
        pattern = re.compile(r'"(\d+)"\s*(\{)', re.MULTILINE)

        current_pos = 0
        total_len = len(raw_output)

        while current_pos < total_len:
            # * Search for the next match starting from the current cursor position
            match = pattern.search(raw_output, current_pos)

            if not match:
                # * If there are no matching features later, the loop will break directly
                break

            appid = match.group(1)
            start_brace_index = match.start(2)  # '{' position in string

            # * Try to retrieve the complete block and get the "end position" of the block
            vdf_block_str, end_index = self._extract_vdf_block(
                raw_output, start_brace_index)

            if vdf_block_str:
                # * Manually add Key: "appid" { ... } to comply with VDF format
                valid_vdf = f'"{appid}" {vdf_block_str}'

                try:
                    data = vdf.loads(valid_vdf)
                    build_id = self._extract_buildid_from_dict(data, appid)

                    if build_id:
                        results[appid] = build_id
                        logger.info(f"Parsed {appid} -> BuildID: {build_id}")
                    else:
                        logger.warning(
                            f"Parsed {appid} but buildid not found in standard path.")

                except Exception as e:
                    logger.error(f"Failed to parse VDF chunk for {appid}: {e}")

                # After successfully processing a block, move the cursor to the end of the block
                current_pos = end_index

            else:
                # * If bracket counting fails (probably corrupted format)
                # In order to avoid a dead loop, go back to the end of "Current Matches" and continue searching.
                logger.warning(
                    f"Could not extract full VDF block for {appid}, skipping header.")
                current_pos = match.end()

        return results

    def _extract_buildid_from_dict(self, data_obj, appid):
        """
        Helper function to extract buildid from VDF object
        """
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

    def _build_query_cmd(self, appids):
        cmd = [self.steamcmd_path, "+login",
               "anonymous", "+app_info_update", "1"]

        for appid in appids:
            cmd.extend(["+app_info_print", str(appid)])

        cmd.append("+quit")

        return cmd

    def get_batch_build_ids(self, appids):
        """
        Query multiple AppIDs in batches
        """
        if not appids:
            return {}

        appids_str = ", ".join(appids)
        logger.info(f"Batch checking BuildIDs for: {appids_str}...")

        cmd = self._build_query_cmd(appids)

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

            # * Parse batch output
            build_ids_map = self._parse_batch_output(output)

            found_count = len(build_ids_map)
            logger.info(
                f"Batch check finished. Found {found_count}/{len(appids)} build IDs.")

            return build_ids_map

        except Exception as e:
            logger.error(f"Exception checking {appids_str}: {e}")
            return None
