def parse_arguments():
    """Handles command-line arguments."""
    parser = argparse.ArgumentParser(description="Backup script using rsync and SSH")

    parser.add_argument("source", help="Source directory to back up")
    parser.add_argument("destination", help="Destination directory on the remote machine")
    parser.add_argument("user", help="SSH username")
    parser.add_argument("ip", help="IP address of the remote machine")
    parser.add_argument("schedule_time", help="Backup time in format DD-MM-YYYY HH:MM")

    return parser.parse_args()

