import sys
import subprocess

def config(args):
    """Main config function"""
    if args.dns:
        configure_dns(args.dns)
    elif args.change_hostname:
        change_hostname()
    elif args.change_shell:
        change_shell()
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