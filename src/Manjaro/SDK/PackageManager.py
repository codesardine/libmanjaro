import gi
try:
    gi.require_version('Pamac', '11')
except Exception as e:
    print("WARNING: installed Libpamac version does not match SDK")
from gi.repository import GLib, Pamac as pamac
from Manjaro.SDK.Snaps import Snap
from Manjaro.SDK.Flatpaks import Flatpak
from Manjaro.SDK.Packages import Package
from Manjaro.SDK.Appimages import Appimage


class Pamac():
    def __init__(self, options={
        "config_path": "/etc/pamac.conf",
        "dry_run": False,
        "upgrade": False,
        "aur": False
    }):
        self.config = pamac.Config(conf_path=options["config_path"])
        self.options = options
        self.config.set_enable_flatpak(True)
        self.db = pamac.Database(config=self.config)
        self.config.set_enable_aur(options["aur"])
        self.db.enable_appstream()
        self.data = None
        self.package = Package(self)
        self.snap = Snap(self)
        self.flatpak = Flatpak(self)
        self.appimage = Appimage(self)
        self.transaction = pamac.Transaction(database=self.db)
        self.transaction.connect("emit-action", self.on_emit_action, self.data)
        self.transaction.connect("emit-action-progress", self._on_emit_action_progress, self.data)
        self.transaction.connect("emit-hook-progress", self._on_emit_hook_progress, self.data)
        self.transaction.connect("emit-error", self.on_emit_error, self.data)
        self.transaction.connect("emit-warning", self.on_emit_warning, self.data)
        self.loop = GLib.MainLoop()


    def search_flatpaks(self, pkg: str) -> list:
        return self.flatpak.search(pkg)


    def search_snaps(self, pkg: str) -> list:
        return self.snap.search(pkg)   


    def search_pkgs(self, pkg: str) -> list:
        return self.package.search(pkg)


    def get_app_name(self, pkg: str) -> str:
        """
        return application name if available otherwise returns pkg name.
        """
        return self.package.get_name(pkg)


    def get_pkg_details(self, pkg):
        return self.package.get_details(pkg)


    def get_snap_details(self, pkg):
        return self.snap.get_details(pkg)


    def get_flatpak_details(self, pkg):
        return self.flatpak.get_details(pkg)


    def get_repos(self) -> list:
        """
        return repositories names
        """
        return self.db.get_repos_names()


    def get_categories(self) -> list:
        """
        return categories names
        """
        return self.db.get_categories_names()


    def get_all_pkgs(self) -> list:
        """
        return all available native packages
        """
        return self.package.get_available()


    def get_all_snaps(self) -> list:
        """
        return all available snaps
        """
        return self.snap.get_available()


    def get_all_flatpaks(self) -> list:
        """
        return all available flatpaks
        """
        return self.flatpak.get_available()


    def get_all_appimages(self) -> list:
        """
        return all available appimages
        """
        return self.appimage.get_available()


    def add_pkgs_to_install(self, pkgs: list, pkg_format="packages"):
        """
        add packages to installation list
        :param pkg_format: packages/snaps/flatpaks
        """            
        if pkg_format == "packages":
            target = self.package.install

        elif pkg_format == "snaps":
            target = self.snap.install

        elif pkg_format == "flatpaks":
            target = self.flatpak.install

        elif pkg_format == "appimages":
            target = self.appimage.install

        for pkg in pkgs:
            target.append(pkg)


    def add_pkgs_to_remove(self, pkgs: list, pkg_format="packages"):
        """
        add packages to remove list
        :param pkg_format: packages/snaps/flatpaks
        """
        if pkg_format == "packages":
            target = self.package.remove

        elif pkg_format == "snaps":
            target = self.snap.remove

        elif pkg_format == "flatpaks":
            target = self.flatpak.remove

        elif pkg_format == "appimages":
            target = self.appimage.remove

        for pkg in pkgs:
            target.append(pkg)


    def get_installed_pkgs(self) -> list:
        """
        return a list of all installed packages
        """
        return self.package.get_installed()


    def on_msg_emit(self, action=None, progress=None, status=None, details=[], message=None):
        """
        to be reimplemented if we need to do something after transaction finishes
        """
        for msg in (action, progress, status, message, details):
            if msg:
                pass
                #print(msg)


    def on_emit_action(self, transaction, action, data):
        self.on_msg_emit(action=action)


    def _on_emit_action_progress(self, transaction, action, status, progress, data):
       self.on_msg_emit(action=action, status=status, progress=progress)


    def _on_emit_hook_progress(self, transaction, action, details, status, progress, data):
        self.on_msg_emit(action=action, details=details, status=status)


    def on_emit_warning(self, transaction, message, data):
        self.on_msg_emit(message=message)


    def on_emit_error(self, transaction, message, details, data):
	    self.on_msg_emit(message=message, details=details)
        
    
    def on_transaction_finish(self):
        """
        to be reimplemented if we need to do something after transaction finishes
        """

        
    def on_transaction_finished_callback(self, source_object, result, user_data):
        try:
            success = source_object.run_finish(result)
        except GLib.GError as e:
            print("Error: ", e.message)
        else:
            if success:
                pass
        finally:
            self.loop.quit()
            self.transaction.quit_daemon()
            self.on_transaction_finish()


    def _run_transaction(self):
        self.transaction.set_dry_run(self.options["dry_run"])

        if self.options["upgrade"]:
            self.transaction.add_pkgs_to_upgrade(self.get_installed_pkgs())
                
        if self.package.install:
            for pkg in self.package.install:
                self.transaction.add_pkg_to_install(pkg)

        if self.snap.install:
            for pkg in self.snap.install:
                self.transaction.add_snap_to_install(pkg)

        if self.flatpak.install:
            for pkg in self.flatpak.install:
                self.transaction.add_flatpak_to_install(pkg)

        if self.appimage.install:
            self.appimage.transaction_install()

        if self.appimage.remove:
            self.appimage.transaction_remove()

        if self.package.remove:
            for pkg in self.package.remove:
                self.transaction.add_pkg_to_remove(pkg)

        if self.snap.remove:
            for pkg in self.snap.remove:
                self.transaction.add_snap_to_remove(pkg)

        if self.flatpak.remove:
            for pkg in self.flatpak.remove:
                self.transaction.add_flatpak_to_remove(pkg)

        self.transaction.run_async(self.on_transaction_finished_callback, None)
        self.loop.run()


    def on_before_transaction(self):
        """
        to be reimplemented if we need to do something before transaction starts
        """
        pass


    def run(self):
        self.on_before_transaction()
        self._run_transaction()
