import gi
try:
  gi.require_version('Pamac', '11')
except Exception as e:
  print("WARNING: installed Libpamac version does not match SDK")
from gi.repository import GLib, Pamac as pamac


class Pamac():
    def __init__(self, options={
        "config_path": "/etc/pamac.conf",
        "enable_aur": False,
        "enable_snap": True,
        "enable_flatpak": True
    }):
        self._packages = {
          "install": {
            "packages": [],
            "snaps:": [],
            "flatpaks": []
          },
          "remove": {
              "packages": [],
              "snaps": [],
              "flatpaks": []
          }
        }
        config = pamac.Config(conf_path=options["config_path"])
        config.set_enable_aur(options["enable_aur"])
        config.set_enable_snap(options["enable_snap"])
        config.set_enable_flatpak(options["enable_flatpak"])
        self.db = pamac.Database(config=config)
        self.db.enable_appstream()
        self.transaction = pamac.Transaction(database=self.db)
        self.transaction.connect(
            "emit-action", self.on_emit_action, self._packages)
        self.transaction.connect(
            "emit-action-progress", self._on_emit_action_progress, self._packages)
        self.transaction.connect("emit-hook-progress",
                                 self._on_emit_hook_progress, self._packages)
        self.transaction.connect(
            "emit-error", self.on_emit_error, self._packages)
        self.transaction.connect(
            "emit-warning", self.on_emit_warning, self._packages)
        self.loop = GLib.MainLoop()
        #print(dir(self.db))
        # for i in dir(self.transaction):
        #  print(i)

    def search_flatpaks(self, pkg: str) -> list:
        pkgs = []
        def callback(source_object, result):
            try:
                flatpaks = source_object.search_flatpaks_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in flatpaks:
                    pkgs.append(pkg)
            finally:
                self.loop.quit()

        self.db.search_flatpaks_async(pkg, callback)
        self.loop.run()
        return pkgs

    def search_snaps(self, pkg: str) -> list:
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
                self.loop.quit()

        self.db.search_snaps_async(pkg, callback)
        self.loop.run()
        return pkgs

    def search_pkgs(self, pkg: str) -> list:
        pkgs = []
        pkd_db = self.db.search_pkgs(pkg)
        for p in pkd_db:
            pkgs.append(p)
        return pkgs

    def get_app_icon(self, pkg: object) -> str or None:
        return self.db.get_pkg(pkg).get_icon()

    def get_app_name(self, pkg: str) -> str:
        """
        return application name if available otherwise returns pkg name.
        """
        name = self.db.get_pkg(pkg).get_app_name()
        if not name:
            name = self.db.get_pkg(pkg).get_name()
        return name

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
        pkgs = []
        for repo in self.get_repos():
            repository = self.db.get_repo_pkgs(repo)
            for pkg in repository:
                pkgs.append(pkg)

        return pkgs

    def get_all_snaps(self) -> list:
        """
        return all available snaps
        """
        pkgs = []
        def callback(source_object, result):
            try:
                snaps = source_object.get_category_snaps_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in snaps:
                    pkgs.append(pkg)
            finally:
                self.loop.quit()

        for cat in self.get_categories():
            self.db.get_category_snaps_async(cat, callback)
            self.loop.run()

        return pkgs

    def get_all_flatpaks(self) -> list:
        """
        return all available flatpaks
        """
        pkgs = []
        def on_category_flatpaks_ready_callback(source_object, result):
            try:
                flatpaks = source_object.get_category_flatpaks_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in flatpaks:
                    pkgs.append(pkg)
            finally:
                self.loop.quit()

        for cat in self.get_categories():
            self.db.get_category_flatpaks_async(
                cat, on_category_flatpaks_ready_callback)
            self.loop.run()

        return pkgs

    def add_pkgs_to_install(self, pkgs: list, pkg_format="packages"):
        """
        add packages to installation list
        :param pkg_format: packages/snaps/flatpaks
        """
        def add(pkg):
            self._packages["install"][pkg_format].append(pkg)
        for pkg in pkgs:
            add(pkg)
        
    def remove_pkgs_from_install(self, pkgs: list, pkg_format="packages"):
        """
        remove packages from installation list
        :param pkg_format: packages/snaps/flatpaks
        """
        def remove(pkg):
            if pkg in self._packages["install"][pkg_format]:
                self._packages["install"][pkg_format].remove(pkg)

        for pkg in pkgs:
            remove(pkg)

    def add_pkgs_to_remove(self, pkgs: list, pkg_format="packages"):
        """
        check if packages are installed and
        add packages to remove list
        :param pkg_format: packages/snaps/flatpaks
        """
        def remove(pkg):
            if self.db.is_installed_pkg(pkg):
                self._packages["remove"][pkg_format].append(pkg)

        for pkg in pkgs:
            remove(pkg)

    def sanitize_packages(self, packages: list) -> list:
        """
        removes packages from the list if they do not exist
        or are not installed
        """
        pkgs = []
        def check_pkg(pkg):
            error = f"package not existent: {pkg}"
            try:
                if self.db.get_pkg(pkg).get_name() == pkg:
                    if pkg not in self.get_installed_pkgs():
                        pkgs.append(pkg)
                else:
                    print(error)
            except AttributeError:
                print(error)

        for pkg in packages:
            check_pkg(pkg)
        return pkgs

    def get_installed_pkgs(self) -> list:
        """
        return a list of all installed packages
        """
        pkgs = []
        for pkg in self.db.get_installed_pkgs():
            pkgs.append(pkg.get_name())
        return pkgs

    def on_emit_action(self, transaction, action, data):
        print(action)
        return action

    def _on_emit_action_progress(self, transaction, action, status, progress, data):
        print(f"{action} {status} {progress}")
        return progress

    def _on_emit_hook_progress(self, transaction, action, details, status, progress, data):
        print(f"{action} {details} {status}")
        return progress

    def on_emit_warning(self, transaction, message, data):
        print(message)
        return message

    def on_emit_error(self, transaction, message, details, details_length, data):
        if details_length > 0:
            print(f"{message}:")
        for detail in details:
            print(detail)
        else:
            print(message)

    def get_progress(self) -> int:
        """
        return package manager progress
        """
        if self._on_emit_hook_progress():
            return self._on_emit_hook_progress()
        elif self._on_emit_action_progress():
            return self._on_emit_action_progress()

    def on_transaction_finish(self):
        """
        to be reimplemented if we need to do something affter transaction finishes
        """
        print("Transaction successful")

    def on_transaction_finished_callback(self, source_object, result, user_data):
        try:
            success = source_object.run_finish(result)
        except GLib.GError as e:
            print("Error: ", e.message)
        else:
            if success:
                self.on_transaction_finish()
            else:
                print("Ops something went wrong.")
        finally:
            self.loop.quit()
            self.transaction.quit_daemon()

    def _run_transaction(self):
        install_pkgs = self._packages["install"]["packages"]
        install_snaps = self._packages["install"]["snaps"]
        install_flatpaks = self._packages["install"]["flatpaks"]

        if install_pkgs:
          self.transaction.add_pkgs_to_upgrade(get_installed_pkgs())
          for pkg in install_pkgs:
            self.transaction.add_pkg_to_install(pkg)

        if install_snaps:
          self.transaction.add_snaps_to_upgrade(get_installed_snaps())
          for pkg in install_snaps:
            self.transaction.add_snaps_to_install(pkg)

        if install_flatpaks:
          self.transaction.add_flatpaks_to_upgrade(get_installed_flatpaks())
          for pkg in install_flatpaks:
            self.transaction.add_flatpaks_to_install(pkg)

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
