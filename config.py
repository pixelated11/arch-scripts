import sys
import subprocess
import argparse


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
        with open('/etc/systemd/resolved.conf', 'w') as f:
            f.write(resolved_content)
        
        # Restart systemd-resolved service
        subprocess.run(['sudo', 'systemctl', 'restart', 'systemd-resolved'], check=True)
        print(f"DNS configured to {provider} successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart systemd-resolved: {e}")
        return False
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def config(args):
    """Main config function"""
    if args.dns:
        configure_dns(args.dns)
    else:
        print("No configuration options specified. Use --dns to configure DNS.")
