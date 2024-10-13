import subprocess

def get_sudo_password_gui():
    """ Display a Zenity dialog to get the sudo password. """
    try:
        result = subprocess.run(
            ['zenity', '--password', '--title=Sudo Password'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:  # User input is successful
            return result.stdout.decode('utf-8').strip()  # Return the entered password
        else:
            print("No password provided or user canceled.")
            return None
    except Exception as e:
        print(f"An error occurred while getting the password: {e}")
        return None
