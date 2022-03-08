import gi
from gi.repository import GLib
from Manjaro.SDK import Utils

class Snap():
    def __init__(self, pm_instance):
        self.pm = pm_instance
        self.pm.config.set_enable_snap(True)
        self.install = []
        self.remove = []


    def search(self, pkg):
        pkgs = []
        def callback(source_object, result):
            try:
                snaps = source_object.search_snaps_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in snaps:
                    pkgs.append(pkg)
            finally:
                self.pm.loop.quit()

        self.pm.db.search_snaps_async(pkg, callback)
        self.pm.loop.run()
        return tuple(pkgs)

    
    def get_details(self, pkg):
        info = {}
        def callback(source_object, result):
            try:
                p = source_object.get_snap_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                info["format"] = "snap"
                info["app_id"] = p.get_app_id()
                info["title"] = p.get_app_name()
                info["channel"] = p.get_channel()
                info["channels"] = p.get_channels()
                info["confined"] = p.get_confined()
                info["description"] = p.get_desc()
                info["download_size"] = p.get_download_size()
                info["icon"] = p.get_icon()
                info["id"] = p.get_id()
                info["install_date"] = Utils.glib_date_to_string(p.get_install_date())
                info["installed_size"] = p.get_installed_size()
                info["installed_version"] = p.get_installed_version()
                info["launchable"] = p.get_launchable()
                info["license"] = p.get_license()
                info["long_description"] = p.get_long_desc()
                info["name"] = p.get_name()
                info["publisher"] = p.get_publisher()
                info["repository"] = p.get_repo()
                info["screenshots"] = p.get_screenshots()
                info["url"] = p.get_url()
                info["version"] = p.get_version()
            finally:
                self.pm.loop.quit()

        self.pm.db.get_snap_async(pkg, callback)
        self.pm.loop.run()
        return info

    def get_available(self, db=[]):
        def callback(source_object, result):
            try:
                snaps = source_object.get_category_snaps_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in snaps:
                    db.append(pkg)
            finally:
                self.pm.loop.quit()

        for cat in self.pm.get_categories():
            self.pm.db.get_category_snaps_async(cat, callback)
            self.pm.loop.run()

        return tuple(db)