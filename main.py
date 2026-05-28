#!/usr/bin/env python3
import sys
import os
import subprocess
import argparse
from update import *
from config import *
from install import *
# Add the arch_scripts module to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'lib/python3/site-packages'))
    
parser = argparse.ArgumentParser(
    prog="arch-scripts",
    description="A useful CLI tool to do stuff in archlinux."
)
# Arguments
parser.add_argument(
    '--version',
    '-v',
    action="version",
    version="Preview, version v0.6.9, Production build."
)

sub = parser.add_subparsers(dest='command', required=True)
# Subcommands

# -- Config --
config_parser = sub.add_parser('config', help="Configures stuff using script.")
config_parser.add_argument('--dns', choices=['quad9', 'cloudflare', 'adguard', 'google'], 
                          help='Configure DNS provider for systemd-resolved')
config_parser.add_argument(
    '--change-hostname',
    action='store_true',
    help="Changes your system hostname."
)
config_parser.add_argument(
    '--change-shell',
    action='store_true',
    help="Changes the default shell for the current user."
)

# -- Update --
sub.add_parser('update', help="Updates system using script.")

# -- Install --
install_parser = sub.add_parser('install', help="Installs various pack of packages.")
install_parser.add_argument(
    '--development',
    help="Installs basic development packages, such as cmake, git, and more.",
    action='store_true'
)
install_parser.add_argument(
    '--qemu-full',
    help="Installs a full QEMU KVM package.",
    action='store_true'
)
    
def main():
    args = parser.parse_args()
    # Make sure to parse args first

    if args.command == 'update':
        update()
    elif args.command == 'config':
        config(args)
    elif args.command == 'install':
        install(args)


if __name__ == "__main__":
    main()

# beep beep bop bop