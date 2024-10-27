import subprocess
def clean():
    """ Clean logs """
    subprocess.run(["echo", "{}", ">", "../data/vendor_allow_counts.json"])
    subprocess.run(["echo", "[]", ">", "../data/usb_device_logs.json"])

    subprocess.Popen(['sudo', '-S', 'tee', '-a', '/etc/udev/rules.d/99-disable-usb-automount.rules'],
                     stdin=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate(input=f'uiop[]\n\n'.encode())
    subprocess.Popen(['sudo', '-S', 'tee', '-a', '/etc/udev/rules.d/99-usb-blacklist.rules.rules'],
                     stdin=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate(input=f'\n'.encode())


if __name__ == "__main__":
    clean()
