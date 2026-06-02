import sys
import subprocess
import os

def config(args):
    """Main config function"""
    if args.dns:
        configure_dns(args.dns)
    elif args.change_hostname:
        change_hostname()
    elif args.change_shell:
        change_shell()
    elif args.mirror_rank:
        rank_mirrors()
    elif args.journal_limit:
        limit_journal_logs()
    elif args.swapiness:
        change_swappiness()
    elif args.timezone:
        change_timezone()
    else:
        print("Config requires at least one parameter.")

def configure_dns(provider):
    """Configure DNS in systemd-resolved's resolved.conf"""
    dns_servers = {
        'quad9': '9.9.9.9 149.112.112.112',
        'cloudflare': '1.1.1.1 1.0.0.1',
        'adguard': '94.140.14.14 94.140.15.15',
        'google': '8.8.8.8 8.8.4.4'
    }
    
    if provider not in dns_servers:
        print(f"Invalid DNS provider: {provider}")
        return False
    
    dns_config = dns_servers[provider]
    
    try:
        # Create the configuration content
        resolved_content = f"""[Resolve]
DNS={dns_config}
FallbackDNS=
Domains=~.
DNSSEC=yes
DNSOverTLS=opportunistic
MulticastDNS=yes
LLMNR=yes
Cache=yes
DNSStubListener=yes
"""
        
        # Write to /etc/systemd/resolved.conf
        with open('/etc/systemd/resolved.conf', 'w') as file:
            file.write(resolved_content)
        # Restart systemd-resolved service
        subprocess.run(['sudo', 'systemctl', 'restart', 'systemd-resolved'], check=True)
        print(f"DNS configured to {provider} successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart systemd-resolved: {e}")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def change_hostname():
    print("Enter your desired hostname:")
    hostname = input("Hostname: ")
    
    # Validate hostname (basic validation)
    if not hostname or len(hostname) == 0:
        print("Hostname cannot be empty.")
        sys.exit(1)
    try:
        # Write the new hostname to /etc/hostname
        with open('/etc/hostname', 'w') as f:
            f.write(hostname + '\n')
        
        # Also update the current hostname using hostnamectl
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', hostname], check=True)
        
        print(f"Hostname changed to {hostname} successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to set hostname: {e}")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    
def change_shell():
    print("Enter your desired shell (e.g., /bin/bash, /bin/zsh):")
    shell = input("Shell: ")
    
    # Validate that the shell exists
    try:
        subprocess.run(['which', shell], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print(f"Shell {shell} not found on this system.")
        return False
    
    try:
        # Change the user's shell using chsh
        subprocess.run(['chsh', '-s', shell], check=True)
        
        print(f"Shell changed to {shell} successfully!")
        print("You may need to log out and back in for the changes to take effect.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to change shell: {e}")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def limit_journal_logs():
    config_dir = "/etc/systemd/journald.conf.d"
    config_file = f"{config_dir}/99-limit-size.conf"
    
    print("Limiting systemd journal logs capacity to 200MB...")
    try:
        # Create directory path if missing
        subprocess.run(["sudo", "mkdir", "-p", config_dir], check=True)
        
        # Drop configuration values directly into file destination using sudo tee
        config_content = "[Journal]\nSystemMaxUse=200M\n"
        proc = subprocess.Popen(["sudo", "tee", config_file], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        proc.communicate(input=config_content)
        
        # Restart the daemon service to reload rules
        subprocess.run(["sudo", "systemctl", "restart", "systemd-journald"], check=True)
        print("Journal size cap applied and service restarted successfully.")
    except Exception as e:
        print(f"Failed to configure journal limit: {e}")

def change_swappiness():
    val = input("Enter preferred swappiness value (0-100, recommended for desktop: 10): ").strip()
    if not val.isdigit() or not (0 <= int(val) <= 100):
        print("Invalid entry. Please enter a number between 0 and 100.")
        return

    config_file = "/etc/sysctl.d/99-swappiness.conf"
    print(f"Setting persistent swappiness index value to {val}...")
    try:
        # Write configuration rule persistently
        proc = subprocess.Popen(["sudo", "tee", config_file], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        proc.communicate(input=f"vm.swappiness={val}\n")
        
        # Apply runtime configurations immediately
        subprocess.run(["sudo", "sysctl", "--system"], check=True)
        print("Swappiness value configured and reloaded successfully!")
    except Exception as e:
        print(f"An error occurred writing configuration: {e}")

def rank_mirrors():
    print("Ranking pacman mirrors for speed (this might take a minute)...")
    try:
        # Check and install reflector if missing
        subprocess.run(["sudo", "pacman", "-S", "--needed", "--noconfirm", "reflector"], check=True)
        
        # Run reflector to pull the latest 10 HTTPS mirrors sorted by download speed
        subprocess.run([
            "sudo", "reflector", 
            "--latest", "10", 
            "--protocol", "https", 
            "--sort", "rate", 
            "--save", "/etc/pacman.d/mirrorlist"
        ], check=True)
        print("Mirror list optimized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to optimize mirror list: {e}")

def change_timezone():
    print("Available regions:")
    regions = os.listdir('/usr/share/zoneinfo')
    # Filter out files that aren't regions (like localtime, posix, right, etc.)
    regions = [r for r in regions if os.path.isdir(f'/usr/share/zoneinfo/{r}')]
    for region in sorted(regions):
        print(f"  {region}")
    
    region = input("\nEnter your region from the list above: ")
    
    # Validate region
    if not region or not os.path.isdir(f'/usr/share/zoneinfo/{region}'):
        print("Invalid region selected.")
        return False
    
    print(f"\nAvailable cities/areas in {region}:")
    areas = os.listdir(f'/usr/share/zoneinfo/{region}')
    for area in sorted(areas):
        print(f"  {area}")
    
    city = input("\nEnter your city/area from the list above: ")
    
    # Validate city/area
    if not city or not os.path.exists(f'/usr/share/zoneinfo/{region}/{city}'):
        print("Invalid city/area selected.")
        return False
    
    try:
        # Remove the existing localtime symlink
        if os.path.exists('/etc/localtime'):
            subprocess.run(['sudo', 'rm', '/etc/localtime'], check=True)
        
        # Create new symlink
        subprocess.run(['sudo', 'ln', '-s', f'/usr/share/zoneinfo/{region}/{city}', '/etc/localtime'], check=True)
        
        # Update /etc/timezone file
        with open('/etc/timezone', 'w') as f:
            f.write(f'{region}/{city}\n')
        
        print(f"Timezone successfully changed to {region}/{city}!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to change timezone: {e}")
        return False
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
