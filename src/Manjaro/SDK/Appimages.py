from urllib import request
from Manjaro.SDK import Utils
import json, pathlib, subprocess, os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk


class Appimage():
    def __init__(self, pm_instance):
        self.data_url = "https://raw.githubusercontent.com/AppImage/appimage.github.io/master/database/"
        self.git_url = "https://github.com/"
        self.provider = "https://appimage.github.io"
        self.pm = pm_instance
        self.install = []
        self.remove = []
        self.db = self._build_db()
        i = self.get_installed()
        for app in i:
            print(self.get_installed_details(app))

    def is_plugin_installed(self):
        return os.path.exists("/usr/bin/ail-cli")


    def _get_json(self, provider):
        response = request.urlopen(provider)
        if response.status == 200:
            data = json.loads(response.read())
            return data


    def search(self, value):
        pkgs = []
        search_value = value.lower()
        for app in self.db:
            name = app["name"].split(".")[1].lower()
            title = app["title"].lower()
            desc = app["description"].lower()
            if search_value in name:
                pkgs.append(app["name"])
            elif search_value in title:
                pkgs.append(app["name"])
            elif search_value in desc:
                pkgs.append(app["name"])
        return tuple(pkgs)


    def package_exists(self, pkg):
        for app in self.db:
            if pkg == app["name"]:
                return True
            else:
                return False


    def transaction_install(self):
        for pkg in self.install:
            name = pkg.replace('.', '/')
            release = self._get_json(f"https://api.github.com/repos/{name}/releases")
            id = release[0]["id"]
            assets = self._get_json(f"https://api.github.com/repos/{name}/releases/{id}/assets")
            download = assets[0]["browser_download_url"]
            file_name = assets[0]["name"]
            home = pathlib.Path.home()
            target = f"{home}/Downloads/{file_name}"
            request.urlretrieve(download, target)
            subprocess.run(["ail-cli", "integrate", target])


    def transaction_remove(self):
        #TODO there is not database that controls what is installed or not
        pass


    def get_details(self, pkg):
        for app in self.db:
            if pkg == app["name"]:
                return app 


    def get_available(self):
        pkgs = []
        for app in self.db:
            pkgs.append(app["name"])
        return tuple(pkgs)


    def _is_appimage(self, app):
        local = ".local"
        exec = app.get_executable()
        if local in app.get_filename() and exec.endswith("AppImage"):
            return True
        else:
            return False

    
    def get_installed_details(self, app):
        info = {}
        files = info["files"] = {}
        icon = app.get_icon()
        icon_theme = Gtk.IconTheme.get_default()      
        for icon_name in icon.props.names:
            lookup = icon_theme.lookup_icon(icon_name, 0, 0)
            if lookup is not None:
                files["icon"] = lookup.get_filename()

        files["desktop"] = app.get_filename()
        files["appimage"] = app.get_executable()
        info["title"] = app.get_name()
        info["description"] = app.get_description()
        for p in self.db:
            if p["title"] == info["title"]:
                info["package"] = p["name"]
            elif p["description"] == info["description"]:
                info["package"] = p["name"]
        return info


    def get_installed(self):
        installed = []
        for app in Gio.AppInfo.get_all():
            if self._is_appimage(app):
                installed.append(app)
        return installed


    def _build_db(self):
        appimage = []
        url = self._get_json(f"{self.provider}/feed.json")
        data = url["items"]
        for app in data:
            app_data = {}
            try:
                links = app["links"]
                if app["license"]:
                    app_data["license"] = app["license"]
                else:
                    app_data["license"] = None

                app_data["name"] = links[0]["url"].replace("/", ".")
                app_data["version"] = None
                app_data["url"] = self.git_url + links[0]["url"] + "/releases"
                app_data["format"] = "appimage"
                app_data["repository"] = "https://github.com/AppImage/appimage.github.io"
                app_data["title"] = app["name"].replace("_", " ").replace(".", " ").replace("-", " ")
                
                try:
                    app_data["description"] = Utils.strip_html(app["description"])
                except KeyError:
                    app_data["description"] = "No description available"
                
                try:
                    screenshots = []
                    for img in app["screenshots"]:
                        if not img.startswith("http"):
                            img = self.data_url + img
                        screenshots.append(img)

                    app_data["screenshots"] = screenshots
                except (KeyError, TypeError):
                    app_data["screenshots"] = ""

                try:
                    app_data["icon"] = self.data_url + app["icons"][0]
                except TypeError:
                    app_data["icon"] = None

                appimage.append(app_data)
            except (TypeError, KeyError):
                pass
        return appimage