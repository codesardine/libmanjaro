import subprocess
import pyudev


class Info():

    def __init__(self):
        #TODO hardware detection using udev
        self.context = pyudev.Context()


    def is_virtual_machine(self):
        detect_virtual_machine = subprocess.Popen(
            ["systemd-detect-virt"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        
        result = detect_virtual_machine.communicate()[-1]
        if result is None:
            return False
        else:
            return True
