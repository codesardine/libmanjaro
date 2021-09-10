import os, subprocess


class Info():

    def __init__(self):
        self.inv_variables = self.get_inv_variables()

    def get_inv_variables(self) -> dict: 
        output = subprocess.check_output("printenv", shell=True)
        dict = {}
        s = output.decode('utf-8').splitlines()
        for i in s:
            split = i.split("=", 1)
            dict[split[0]] = str(split[1])          
        return dict

    def get_lsb_version(self):
        lsb = subprocess.Popen(["lsb_release"], shell=True)
        return lsb.replace("LSB Version:", "").trim()

    
    
