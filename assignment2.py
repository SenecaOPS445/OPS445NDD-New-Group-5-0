#!/usr/bin/env python3

import argparse
import os
import subprocess
import logging
import datetime

# Configure logging
logging.basicConfig(filename="backup.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_destination_exists(user, ip, destination):
    """Checks if the destination directory exists on the remote machine."""
    cmd = f"ssh {user}@{ip} test -d {destination}" 
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#Capture output and error using subprocess.PIPE and running command.
    if result.returncode != 0:
        logging.error(f"Checked Destination: Destination directory {destination} does not exist on {user}@{ip}") # Added logging for error
        return False
    else:
        logging.info(f"Checked Destination: Destination directory {destination} exists on {user}@{ip}") # Added logging for success
        return True

def perform_backup(source, destination, user, ip):
    """Performs full or incremental backup using rsync."""
#rsync -avz --delete  -e "ssh -i vm2/vm2.key" /home/ubuntu/backups/ ubuntu@10.0.0.46:/home/ubuntu/backups Rsync manual Command
    rsync_cmd_incremental = f"rsync -avz --delete -e 'ssh' {source} {user}@{ip}:{destination}"
    rsync_cmd_full = f"rsync -avz -e 'ssh' {source} {user}@{ip}:{destination}"
    
    if check_destination_exists(user, ip, destination):
        print(" Remote destination directory exists. Incremental backup will be performed.")
        print("Files deleted locally since last backup, will also be deleted remotely if you continue.")
        choice = input("Do you want to proceed with deleting remote-only files? (yes/no): ").strip().lower()
        if choice == "yes":
            logging.info(f"Starting Incremental Backup from {source} to {user}@{ip}:{destination}") #added logging for backup start
            print(f"Starting Incremental Backupfrom {source} to {user}@{ip}:{destination}.")
            print("Files deleted locally since last backup, will be deleted remotely.")
            # Perform incremental backup with deletion of remote-only files
            cmd_result = subprocess.run(rsync_cmd_incremental, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd_result.returncode != 0:
                logging.error(f"Backup failed: {cmd_result.stderr.decode()}")
                print(f"Backup failed: {cmd_result.stderr.decode()}")
            else:
                logging.info(f"Incremental Backup completed successfully: {cmd_result.stdout.decode()}")
                print(f"Backup completed successfully: {cmd_result.stdout.decode()}")
        else:
            logging.info(f"Starting Incremental Backup from {source} to {user}@{ip}:{destination}") #added logging for backup start
            print(f"Starting Incremental Backup from {source} to {user}@{ip}:{destination}")
            print("Files deleted locally since last backup, will not be deleted remotely.")
            # Perform incremental backup without deletion of remote-only files
            cmd_result = subprocess.run(rsync_cmd_full, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd_result.returncode != 0:
                logging.error(f"Backup failed: {cmd_result.stderr.decode()}")
                print(f"Backup failed: {cmd_result.stderr.decode()}")
            else:
                logging.info(f"Incremental Backup completed successfully: {cmd_result.stdout.decode()}")
                print(f"Backup completed successfully: {cmd_result.stdout.decode()}")        
    else:
        # Perform full backup
        logging.info(f"Destination directory does not exist. Performing full backup.") #added logging for full backup
        print("Destination directory does not exist. Performing full backup.")
        cmd_result = subprocess.run(rsync_cmd_full, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cmd_result.returncode != 0:
            logging.error(f"Backup failed: {cmd_result.stderr.decode()}")
            print(f"Backup failed: {cmd_result.stderr.decode()}")
        else:
            logging.info(f"Backup completed successfully: {cmd_result.stdout.decode()}")
            print(f"Backup completed successfully: {cmd_result.stdout.decode()}")

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
   
