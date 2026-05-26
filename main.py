import subprocess
import argparse
from update import update
from config import config
    
parser = argparse.ArgumentParser(
    prog="arch-scripts",
    description="A useful CLI tool to do stuff in archlinux."
)
# Arguments
parser.add_argument(
    '--version',
    '-v',
    action="version",
    version="Preview, version v0.1.0, Production build."
)

sub = parser.add_subparsers(dest='command', required=True)
# Subcommands

# -- Config --
config_parser = sub.add_parser('config', help="Configures stuff using script.")
config_parser.add_argument('--dns', choices=['quad9', 'cloudflare', 'adguard', 'google'], 
                          help='Configure DNS provider for systemd-resolved')

# -- Update --
sub.add_parser('update', help="Updates system using script.")
    
def main():
    args = parser.parse_args()
    # Make sure to parse args first

    if args.command == 'update':
        update()
    elif args.command == 'config':
        config(args)


if __name__ == "__main__":
    main()

# beep beep bop bop