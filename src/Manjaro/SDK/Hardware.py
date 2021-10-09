import subprocess
#import pyudev


class Graphics:

    def set_open(device="pci"):
        subprocess.run(["mhwd", "-a", device, "free", "0300"])

    def set_proprietary(device="pci"):
        subprocess.run(["mhwd", "-a", device, "nonfree", "0300"])


class Info():

    def __init__(self):
        #TODO hardware detection using udev
        #self.context = pyudev.Context()
        pass

    def graphics_driver(self):
        subprocess.run(["mhwd", "-l", "-d"])

    def is_virtual_machine(self):
        detect_virtual_machine = subprocess.Popen(
            ["systemd-detect-virt"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        
        result = detect_virtual_machine.communicate()[-1]
        if result is None:
            return False
        else:
            return True
