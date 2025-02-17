import os
import re
import subprocess
import time
import logging

def is_valid_project_name(name: str) -> bool:
    return bool(re.match(r'^[\w\-]+$', name))

def run_command(command, cwd, description, retry=1):
    for attempt in range(retry):
        try:
            logging.info(f"Running: {command} in {cwd}")
            subprocess.run(command, cwd=cwd, shell=True, check=True)
            return
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during {description}: {e}")
            if attempt < retry - 1:
                time.sleep(1)
            else:
                raise