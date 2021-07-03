import os, subprocess


class Info():

    def __init__(self):
        self.inv_variables = self.get_inv_variables()

    def get_inv_variables() -> dict: 
        output = subprocess.check_output("printenv", shell=True)
        dict = {}
        s = output.decode('utf-8').splitlines()
        for i in s:
            split = i.split("=", 1)
            dict[split[0]] = str(split[1])          
        return dict

    def get_desktop_session(self):
        ds = os.environ.get('DESKTOP_SESSION')
        if not ds:
            ds = os.environ.get('XDG_CURRENT_DESKTOP')
        return ds

    def get_desktop_lang(self):
        return os.environ.get('LANG')

    def get_session_display(self):
        return os.environ.get('DISPLAY')

    def get_user_home_folder(self):
        return os.environ.get('HOME')

    def get_gdk_backend(self):
        return os.environ.get('GDK_BACKEND')
        
    def get_qt_qpa_platform_theme(self):
        return os.environ.get('QT_QPA_PLATFORMTHEME')

    def get_lsb_version(self):
        lsb = Popen(["lsb_release"], shell=shell)
        return lsb.replace("LSB Version:", "").trim()

    
    
