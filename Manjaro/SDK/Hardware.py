import subprocess
from gi.repository import Ldm


class Info():

    def __init__(self):
        self.hw_manager = Ldm.Manager()
        self.printers = self.hw_manager.get_devices(
            Ldm.DeviceType.USB | Ldm.DeviceType.PRINTER)

    def is_virtual_machine(self):
        detect_virtual_machine = subprocess.Popen(
            ["systemd-detect-virt"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        
        result = detect_virtual_machine.communicate()[-1]
        if result is None:
            return False
        else:
            return True

    def get_printers(self):
        return self.printers

    def get_printer_name(self, dev_nunber=0):
        return printers[device].get_name()

    def get_providers(self, device=self.printers, dev_nunber=0):
        return hw_manager.get_providers(device[dev_nunber])

    def get_device_driver(self, device=self.printers, provider_nunber=0):
        self.get_providers[provider_nunber].get_package()
