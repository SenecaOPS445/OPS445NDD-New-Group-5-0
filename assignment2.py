#!/usr/bin/env python3

import argparse
import os
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="backup.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_ssh_auth(user, ip):
    """Checks if SSH authentication is successful."""
    cmd = f"ssh {user}@{ip} exit"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        logging.error(f"SSH Authentication failed for {user}@{ip}: {result.stderr.decode()}")
        print(f"SSH Authentication failed for {user}@{ip}: {result.stderr.decode()}")
        return False
    else:
        logging.info(f"SSH Authentication successful for {user}@{ip}")
        print(f"SSH Authentication successful for {user}@{ip}")
        return True

def check_destination_exists(user, ip, destination):
    """Checks if the destination directory exists on the remote machine."""
    cmd = f"ssh {user}@{ip} test -d {destination}" 
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#Capture output and error using subprocess.PIPE and running command.
    if result.returncode != 0:
        logging.warning(f"Checked Destination: Destination directory {destination} does not exist on {user}@{ip}") # Added logging for error
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
    cron_time = convert_to_cron(schedule_time)
    #getting absolute path of the script
    script_path = os.path.abspath(__file__)
    cron_job = f'{cron_time} python3 {script_path} {source} {destination} {user} {ip}'
    try:
        # Check if the cron job already exists
        existing_jobs = subprocess.run("crontab -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cron_job in existing_jobs.stdout.decode():
            logging.info(f"Cron job already exists: {cron_job}")
            print(f"Backup is already scheduled for specified source, destination and time: {cron_job}")
            exit # exit with no code as no error occurred
        else: 
            # Add the cron job
            subprocess.run(f'(crontab -l; echo "{cron_job}") | crontab -', shell=True, check=True)
            logging.info(f"Added cron job: {cron_job}")
    except:
        logging.error(f"Error adding cron job: {cron_job}")
        print(f"Error adding cron job: {cron_job}")
        exit(1)

def convert_to_cron(schedule_time):
    """Converts a datetime string to cron format."""
    try:
        dt = datetime.strptime(schedule_time, "%d-%m-%Y %H:%M")
        return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
    except ValueError:
        logging.error(f"Invalid schedule time format: {schedule_time}. Expected format: DD-MM-YYYY HH:MM")
        print(f"Invalid schedule time format: {schedule_time}. Expected format: DD-MM-YYYY HH:MM")
        exit(1) # exit with code 1 as error occurred
    
def validate_ip(ip):
    """Validates the IP address format."""
    try:
        octets = ip.split('.')
        if len(octets) != 4:
            raise ValueError
        for each in octets:
            if not (0 <= int(each) <= 255):
                raise ValueError
        return True
    except ValueError:
        logging.error(f"Invalid IP address format: {ip}")
        print(f"Invalid IP address format: {ip}")
        return False    

def parse_arguments():
    """Handles command-line arguments."""
    parser = argparse.ArgumentParser(description="Backup script using rsync and SSH")
    parser.add_argument("source", help="Source directory to back up")
    parser.add_argument("destination", help="Destination directory on the remote machine")
    parser.add_argument("user", help="SSH username for the remote machine")
    parser.add_argument("ip", help="IP address of the remote machine")
    parser.add_argument("--schedule_time", help="Backup time in format DD-MM-YYYY HH:MM",default=None)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Validate IP address
    if not validate_ip(args.ip):
        exit(1)
    # Check SSH authentication
    if not check_ssh_auth(args.user, args.ip):
        exit(1)

    if args.schedule_time:
        # Schedule backup
        schedule_backup(args.source, args.destination, args.user, args.ip, args.schedule_time)
    else:
        # Perform backup
        perform_backup(args.source, args.destination, args.user, args.ip)    
