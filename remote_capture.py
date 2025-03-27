#!/usr/bin/env python3
"""
Remote Capture Trigger using Paramiko

This script connects to the Raspberry Pi via SSH using Paramiko,
automatically supplies the password, and executes the capture script.
"""

import paramiko
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def capture_images(pi_ip: str, username: str = "dev", password: str = "admin0", script_path: str = "/home/dev/Desktop/automata/capture_both_cameras.py") -> bool:
    """
    Executes the capture_both_cameras.py script on the Raspberry Pi via SSH.

    :param pi_ip: IP address of the Raspberry Pi.
    :param username: SSH username (default "dev").
    :param password: SSH password (default "admin0").
    :param script_path: Full path to the capture script on the Pi.
    :return: True if the command succeeds, False otherwise.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logger.info(f"Connecting to {pi_ip} as {username}...")
        client.connect(pi_ip, username=username, password=password)
        command = f"python3 {script_path}"
        logger.info(f"Executing remote command: {command}")
        
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error_output = stderr.read().decode('utf-8').strip()
        
        if output:
            logger.info("Capture output: " + output)
        if error_output:
            logger.error("Capture error: " + error_output)
        
        return True
    except Exception as e:
        logger.error("SSH connection or execution error: " + str(e))
        return False
    finally:
        client.close()

if __name__ == "__main__":
    raspberry_ip = "192.168.1.96"  # Replace with your Pi's IP
    if capture_images(raspberry_ip):
        logger.info("Images captured successfully.")
    else:
        logger.error("Image capture failed.")
