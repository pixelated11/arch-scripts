import sys
import subprocess
import os
# goo goo ga ga
def install(args):
    if args.development:
        install_development()
    elif args.qemu_full:
        install_qemu()
    else:
        print("Install requires at least one parameter.")

def install_development():
    dev_packages = [
        'base-devel',
        'git',
        'github-cli',
        'jdk-openjdk',
        'gcc',
        'libgcc'
    ]
    print("Installing development packages...")
    try:
        subprocess.run(["sudo", "pacman", "-S", "--needed"] + dev_packages, check=True)
        print("Packages installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages using pacman: {e}")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occured: {e}")
        sys.exit(1)

def install_qemu():
    qemu_packages = [
        'qemu-full',
        'virt-manager'
    ]
    print("Installing QEMU packages...")
    try:
        subprocess.run(["sudo", "pacman", "-S", "--needed"] + qemu_packages, check=True)
        print("Packages installed successfully!")
        configure_libvirtd()
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages using pacman: {e}")
        sys.exit(1)
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occured: {e}")
        sys.exit(1)

def configure_libvirtd():
    print("Configuring libvirtd...")
    
    # Try to enable libvirtd service, but continue even if it fails
    try:
        subprocess.run(["sudo", "systemctl", "enable", "--now", "libvirtd"], check=True)
        print("Enabling service successful!")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Enabling service encountered an error: {e}")
        print("Continuing with usermod configuration...")
    except PermissionError:
        print("Warning: Permission denied when enabling service.")
        print("Continuing with usermod configuration...")
    except Exception as e:
        print(f"Warning: An error occurred when enabling service: {e}")
        print("Continuing with usermod configuration...")
    
    # This code will always execute, regardless of whether the above succeeded or failed
    print("Usermodding libvirtd...")
    try:
        # Get the actual username instead of using $USER which won't expand in subprocess
        username = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
        subprocess.run(["sudo", "usermod", "-aG", "libvirt", username], check=True)
        print("Usermod successful! Configuring done.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Usermodding failed: {e}")
        sys.exit(1)  # Exit here since this is critical
    except PermissionError as e:
        print("Error: Permission denied. Please run with sudo.")
        sys.exit(1)  # Exit here since this is critical
    except Exception as e:
        print(f"Error: An error occurred during usermod: {e}")
        sys.exit(1)  # Exit here since this is critical