import sys
import subprocess

def update():
    # Error code checking declaration, yes yes
    result = subprocess.run(["sudo", "pacman", "-Syu"])

    if result.returncode == 0:
        print(f"Update successful.")

    else:
        print(f"Process exited with code {result.returncode}")
        
    # Ask user to choose AUR helper
    print("\nSelect AUR helper:")
    print("1. yay")
    print("2. paru")
    print("3. Skip AUR updates")
    
    choice = input("Enter your choice (1/2/3): ")
    
    if choice == "1":
        aur_result = subprocess.run(["yay", "-Syu"])
        if aur_result.returncode != 0:
            print(f"yay update failed with code {aur_result.returncode}")
    elif choice == "2":
        aur_result = subprocess.run(["paru", "-Syu"])
        if aur_result.returncode != 0:
            print(f"paru update failed with code {aur_result.returncode}")
    elif choice == "3":
        print("Skipping AUR updates.")
    else:
        print("Invalid choice. Skipping AUR updates.")
    
    input("Press any key to exit...")
    sys.exit(0 if result.returncode == 0 else result.returncode)