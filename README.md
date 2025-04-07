# Winter 2025 Assignment 2
### Overview

This Python script provides a versatile backup solution using rsync and SSH for secure data transfer. It supports both full and incremental backups, with optional scheduling via cron jobs. This script is created as per the requirements and limitations of Assignment 2 of OPS445 course from Seneca Polytechnic.

### Contributors

- Divyansh Pandya (dpandya17)
- Kledis GJoni (kgjoni)
- Ebrahim Patel (epatel16)
- Seamus Dujua (sjdujua)

### Features

- **Backup Types:**
    - **Incremental Backup:** Automatically detects changes since the last backup and synchronizes only modified files.
    - **Full Backup:** Copies all files from the source to the destination.
- **Error Handling:** Logs all events, errors and warnings to `backup.log` for easy troubleshooting.
- **Interactive Mode:** Allows users to choose whether to delete remote-only files during incremental backup.
- **Scheduling:** Enables users to schedule backups using cron jobs for automated execution at specified times.

### Requirements

- Python 3
- rsync
- Password-less SSH access to the remote machine

### Usage

1. **Command-line Arguments:**
    - `source`: Source directory to back up.
    - `destination`: Destination directory on the remote machine.
    - `user`: SSH username for the remote machine.
    - `ip`: IP address of the remote machine.
    - `-schedule_time`: Optional. Backup time in format `DD-MM-YYYY HH:MM` for scheduling.
    - `-noninteractive`: Optional flag. Run backup in non-interactive mode (skip deletion prompt).
2. Syntax: 
    
    ```bash
    python3 assignment2.py <source_directory> <destination_directory> <ssh_user> <remote_ip> [--schedule_time "DD-MM-YYYY HH:MM"] [--noninteractive]
    
    ```
    
3. **Examples:**
    - Perform a backup:
        
        ```bash
        bash
        Copy
        python3 backup_script.py /path/to/source /path/to/destination username 192.168.1.100
        
        ```
        
    - Schedule a backup for a 6PM on 7th April 2025:
        
        ```bash
        bash
        Copy
        python3 backup_script.py /path/to/source /path/to/destination username 192.168.1.100 --schedule_time "07-04-2025 18:00"
        
        ```
        

### Limitations

- Currently supports Linux/Unix systems only due to specific commands used (`ping`, `rsync`, `ssh`).
