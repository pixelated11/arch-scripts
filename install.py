import sys
import subprocess
import os
# pixelated11.page.gd

# Install argument handler
def install(args):
    if args.development:
        install_development()
    elif args.qemu_full:
        install_qemu()
    elif args.sandbox:
        install_sandbox()
    elif args.gaming:
        install_gaming()
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

def install_sandbox():
    sandbox_packages = ['docker', 'docker-compose', 'docker-buildx']
    print("Installing Sandbox/Containerization packages...")
    try:
        subprocess.run(["sudo", "pacman", "-S", "--needed"] + sandbox_packages, check=True)
        print("Packages installed successfully!")
        
        # Enable and start the docker socket daemon safely
        print("Enabling and starting Docker daemon...")
        subprocess.run(["sudo", "systemctl", "enable", "--now", "docker.service"], check=True)
        
        # Add user to docker group so they don't have to use sudo for every container command
        username = os.getenv('SUDO_USER') or os.getenv('USER')
        if username and username != 'root':
            print(f"Adding user '{username}' to the docker group...")
            subprocess.run(["sudo", "usermod", "-aG", "docker", username], check=True)
            print("Successfully added to group. Note: You must log out and back in for group changes to take effect.")
            
    except subprocess.CalledProcessError as e:
        print(f"Installation or configuration failed: {e}")
        sys.exit(1)

def detect_gpu_vendor():
    """
    Detects the GPU vendor by inspecting lspci or system device paths.
    Returns: 'amd', 'nvidia', 'intel', or 'unknown'
    """
    try:
        # Run lspci filtering for VGA/3D controller strings
        result = subprocess.run(['lspci'], capture_output=True, text=True, check=True)
        lspci_output = result.stdout.lower()
        
        if 'nvidia' in lspci_output:
            return 'nvidia'
        elif 'ati' in lspci_output or 'amd' in lspci_output or 'radeon' in lspci_output:
            return 'amd'
        elif 'intel' in lspci_output:
            return 'intel'
    except Exception:
        # Fallback to checking /sys/class/drm entries if lspci is missing
        if os.path.exists('/sys/class/drm/card0/device/vendor'):
            try:
                with open('/sys/class/drm/card0/device/vendor', 'r') as f:
                    vendor_id = f.read().strip()
                    if '0x10de' in vendor_id: return 'nvidia'
                    if '0x1002' in vendor_id: return 'amd'
                    if '0x8086' in vendor_id: return 'intel'
            except Exception:
                pass
    return 'unknown'

def install_gaming():
    # Base packages shared across all GPUs
    gaming_packages = [
        'gamemode', 'lib32-gamemode',
        'mangohud', 'lib32-mangohud',
        'wine-staging', 'giflib', 'lib32-giflib', 'steam'
    ]
    
    gpu = detect_gpu_vendor()
    print(f"Detected GPU vendor: {gpu.upper()}")
    
    # Append driver packages based on hardware vendor
    if gpu == 'amd':
        gaming_packages += ['vulkan-radeon', 'lib32-vulkan-radeon']
    elif gpu == 'nvidia':
        # Proprietary drivers and 32-bit utils for Nvidia hardware
        gaming_packages += ['nvidia-utils', 'lib32-nvidia-utils', 'nvidia-settings']
    elif gpu == 'intel':
        # Vulkan drivers for modern Intel integrated or Arc graphics
        gaming_packages += ['vulkan-intel', 'lib32-vulkan-intel']
    else:
        print("Warning: Could not reliably detect GPU hardware. Skipping explicit Vulkan drivers.")
        print("You may need to install the appropriate vulkan driver manually.")

    print("Installing Gaming Optimization packages...")
    try:
        # Inform user to ensure [multilib] repository is active
        subprocess.run(["sudo", "pacman", "-S", "--needed"] + gaming_packages, check=True)
        print("Gaming packages installed successfully!")
        print("\nTo use these utilities:")
        print("  - Add 'gamemoderun mangohud %command%' to your game launch choices.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to install gaming packages: {e}")
        print("Tip: Ensure the [multilib] repository is enabled in /etc/pacman.conf")
        sys.exit(1)