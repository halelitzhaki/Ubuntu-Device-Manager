import subprocess


class RootProcessLauncher:
    """ Launching processes with root privileges """

    def __init__(self, sudo_password: str) -> None:
        self.sudo_password = sudo_password

    def execute(self, command: str) -> None:
        """ Execute command with sudo, so it could run in root privileges """
        sudo_command = ['sudo', '-S']
        sudo_command += command.split()  # Preparing command with sudo

        subprocess.Popen(sudo_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) \
            .communicate(input=f'{self.sudo_password}\n'.encode())

    def execute_with_input(self, command: str, input_data: str) -> None:
        """ Execute command with sudo, so it could run in root privileges. And inserting input after.
        For Example - inserting text to a file with root privileges """
        sudo_command = ['sudo', '-S']
        sudo_command += command.split() # Preparing command with sudo

        subprocess.Popen(sudo_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) \
            .communicate(input=f'{self.sudo_password}\n{input_data}\n'.encode())
