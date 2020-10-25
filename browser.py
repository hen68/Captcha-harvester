import os
import tempfile
import subprocess
from threading import Thread
import plistlib


def get_browser_location(browser_file: str, browser_name: str):
    file_path = f"{os.environ['HOME']}/Library/Preferences/{browser_file}.plist"
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            last_use = plistlib.load(file).get('LastRunAppBundlePath')
            if last_use:
                return os.path.join(last_use, "Contents", "MacOS", browser_name)


def launch(domain: str, host: str, port: int, width: int = 400, height: int = 580, extension: str = None):
    browser_commands = []
    path_exec = get_browser_location('com.Google.Chrome', "Google Chrome")
    if path_exec:
        temp_dir = tempfile.TemporaryDirectory()
        user_data = f"--user-data-dir={os.path.join(temp_dir.name, 'Profiles')}"

        browser_commands.extend((
            path_exec,
            user_data,
            '--no-default-browser-check',
            '--no-check-default-browser',
            '--no-first-run',
            f'--host-rules=MAP {domain} {host}:{port}',
            f"--window-size={width},{height}",
            f"--app=http://{domain}"
        ))
        if extension:
            browser_commands.append(f'--load-extension={extension}')
        browser_instance = Thread(target=subprocess.run, args=(browser_commands,), daemon=True)
        return browser_instance
    else:
        return False


