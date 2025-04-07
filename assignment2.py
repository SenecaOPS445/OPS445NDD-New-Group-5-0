#!/usr/bin/env python3

import argparse
import os
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="backup.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def check_destination_exists(user, ip, destination):
    """Checks if the destination directory exists on the remote machine."""
    cmd = f"ssh {user}@{ip} test -d {destination}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=sub)
    return result.returncode == 0

def perform_backup(source, destination, user, ip, full_backup=False):
    """Performs full or incremental backup using rsync."""
    #Divyansh
def schedule_backup(source, destination, user, ip, schedule_time):
    """Schedules the backup using crontab."""
    #JD
    def schedule_backup(source, destination, user, ip, schedule_time):
    """Schedules the backup using crontab."""
   
    cron_time = converts_into_cron_format(schedule_time)

    cron_job = f'echo "{cron_time} python3 /home/ubuntu/backups {source} {destination} {user} {ip}" | crontab -'

    subprocess.run(cron_job, shell=True, check=True)

    logging.info(f"Scheduled backup at {schedule_time} with cron job: {cron_job}")

def converts_into_cron_format(schedule_time):
    """Converts a datetime string to cron format."""

    dt = datetime.strptime(schedule_time, "%d-%m-%Y %H:%M")

    return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"

def parse_arguments():
    """Handles command-line arguments."""
    #Ebrahim
    def parse_arguments():
    """Handles command-line arguments."""
    parser = argparse.ArgumentParser(description="Backup script using rsync and SSH")

    parser.add_argument("source", help="Source directory to back up")
    parser.add_argument("destination", help="Destination directory on the remote machine")
    parser.add_argument("user", help="SSH username")
    parser.add_argument("ip", help="IP address of the remote machine")
    parser.add_argument("schedule_time", help="Backup time in format DD-MM-YYYY HH:MM")

    return parser.parse_args()

def main():
    """Main execution flow."""
    #Divyansh
 
if __name__ == "__main__":
    main()
   
