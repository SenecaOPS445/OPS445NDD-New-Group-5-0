#!/usr/bin/env python3
#Assignment 2 OPS445 NDD
#Contributors: Divyansh Pandya (dpandya17), Kledis GJoni (kgjoni), Ebrahim Patel (epatel16), Seamus Dujua (sjdujua)


import argparse
import os
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="backup.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") #formatting the log file with date, time and level of logging

def check_host_unreachable(ip):
    """Checks if the host is unreachable. Returns True if unreachable."""
    # Using ping command to check if the host is reachable
    # The command may vary based on the OS. This is for Linux/Unix as our script is for Linus only.
    cmd = f"ping -c 1 {ip}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        logging.error(f"Host unreachable: {ip}")
        print(f"Host unreachable: {ip}")
        return True
    else:
        logging.info(f"Host reachable: {ip}")
        return False

def check_ssh_auth(user, ip):
    """Checks if SSH authentication is successful. Returns True if successful."""
    # Using SSH command without password to check authentication
    cmd = f"ssh {user}@{ip} exit"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        logging.error(f"SSH Authentication failed for {user}@{ip}: {result.stderr.decode()}")
        print(f"SSH Authentication failed for {user}@{ip}: {result.stderr.decode()}")
        return False
    else:
        logging.info(f"SSH Authentication successful for {user}@{ip}")
        return True

def check_destination_exists(user, ip, destination):
    """Checks if the destination directory exists on the remote machine. Returns True if exists."""
    cmd = f"ssh {user}@{ip} test -d {destination}" 
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)#Capture output and error using subprocess.PIPE and running command.
    if result.returncode != 0:
        logging.warning(f"Checked Destination: Destination directory {destination} does not exist on {user}@{ip}") # Added logging for error
        return False
    else:
        logging.info(f"Checked Destination: Destination directory {destination} exists on {user}@{ip}") # Added logging for success
        return True

def perform_backup(source, destination, user, ip, noninteractive = False):  # default value of noninteractive is kept false
    """Performs full or incremental backup using rsync. This function checks if the destination directory exists on the remote machine and performs the appropriate backup."""
    # Commands for rsync that will be used for backup
    rsync_cmd_incremental = f"rsync -avz --delete -e 'ssh' {source} {user}@{ip}:{destination}"
    rsync_cmd_full = f"rsync -avz -e 'ssh' {source} {user}@{ip}:{destination}"
    
    if check_destination_exists(user, ip, destination):
        print(" Remote destination directory exists. Incremental backup will be performed.")
        print("Files deleted locally since last backup, will also be deleted remotely if you continue.")

        if noninteractive:
            choice = "no"
        else:
            choice = input("Do you want to proceed with deleting remote-only files? (yes/no): ").strip().lower() #added input prompt for user confirmation
        # Validate user input
        if choice not in ["yes", "no"]:
            logging.error(f"Invalid choice: {choice}. Expected 'yes' or 'no'.")
            print(f"Invalid choice: {choice}. Expected 'yes' or 'no'.")
            exit(1) # exit with code 1 as error occurred
        
        if choice == "yes":
            logging.info(f"Starting Incremental Backup from {source} to {user}@{ip}:{destination}") #added log entry for backup start
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
            logging.info(f"Starting Incremental Backup from {source} to {user}@{ip}:{destination}") #added logging entry for backup start
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
    cron_job = f'{cron_time} python3 {script_path} {source} {destination} {user} {ip}' #cron job to be added to crontab
    try:
        # Check if the cron job already exists
        existing_jobs = subprocess.run("crontab -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cron_job in existing_jobs.stdout.decode(): # Check output of crontab -l for the cron job
            # If the cron job already exists, log the message and exit
            logging.info(f"Cron job already exists: {cron_job}")
            print(f"Backup is already scheduled for specified source, destination and time: {cron_job}")
            exit # exit with no code as no error occurred
        else: 
            # Add the cron job to crontab
            subprocess.run(f'(crontab -l; echo "{cron_job}") | crontab -', shell=True, check=True)
            logging.info(f"Added cron job: {cron_job}")
            print(f"Backup scheduled successfully: {cron_job}. Use 'crontab -l' to view scheduled jobs.")
    except:
        logging.error(f"Error adding cron job: {cron_job}")
        print(f"Error adding cron job: {cron_job}")
        exit(1)

def convert_to_cron(schedule_time):
    """Converts a datetime string to cron format and checks if the scheduled time is in the past."""
    try:
        dt = datetime.strptime(schedule_time, "%d-%m-%Y %H:%M")
        if datetime.strptime(schedule_time, "%d-%m-%Y %H:%M") < datetime.now(): # check if the scheduled time is in the past
            # if the scheduled time is in the past, log the error and exit
            logging.error(f"Scheduled time is in the past: {schedule_time}")
            print(f"Scheduled time is in the past: {schedule_time}")
            exit(1) # exit with code 1 as error occurred because of past time
        return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *" # return cron format time
    except ValueError: # check if the datetime string is in the correct format
        # if the datetime string is not in the correct format, log the error and exit
        logging.error(f"Invalid schedule time format: {schedule_time}. Expected format: DD-MM-YYYY HH:MM")
        print(f"Invalid schedule time format: {schedule_time}. Expected format: DD-MM-YYYY HH:MM")
        exit(1) # exit with code 1 as error occurred because of invalid format
    
def validate_ip(ip):
    """Validates the IP address format. Returns True if the IP address is valid, 
    otherwise logs and prints an error and returns False."""
    try:
        octets = ip.split('.')
        if len(octets) != 4:
            raise ValueError # raise ValueError manually if the length of octets is not 4
        # manually raising the ValueError as it will stop execution there and jump to  
        for each in octets:
            if not (0 <= int(each) <= 255):
                raise ValueError # check if each octet is between 0 and 255
        return True
    except ValueError:
        logging.error(f"Invalid IP address format: {ip}")
        print(f"Invalid IP address format: {ip}")
        return False    
  
def parse_arguments():
    """Handles command-line arguments."""
    parser = argparse.ArgumentParser(description="Backup script using rsync and SSH for secure data transfer.\nSupports full and incremental backups with optional scheduling.") 
    #Creating an argument parser object with description for --help argument
    parser.add_argument("source", help="Source directory to back up")
    parser.add_argument("destination", help="Destination directory on the remote machine")
    parser.add_argument("user", help="SSH username for the remote machine")
    parser.add_argument("ip", help="IP address of the remote machine")
    parser.add_argument("--schedule_time", help="Backup time in format DD-MM-YYYY HH:MM",default=None)
    parser.add_argument("--noninteractive", action="store_true",
                        help="Run backup in non-interactive mode (skip deletion prompt; defaults to not deleting remote-only files)")
    return parser.parse_args() 

if __name__ == "__main__":
    args = parse_arguments()
    logging.info( # Added log entry for every execution of the script to differ each execution in log file.
        "Backup script execution started with parameters: "
        f"source={args.source}, destination={args.destination}, user={args.user}, ip={args.ip}, schedule_time={args.schedule_time}"
    )
    # Validate IP address
    if not validate_ip(args.ip):
        exit(1)
    #Check if the host is reachable
    if check_host_unreachable(args.ip):
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
