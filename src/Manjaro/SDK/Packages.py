from Manjaro.SDK import Utils


class Package():
    def __init__(self, pm_instance):
        self.pm = pm_instance
        self.install = []
        self.remove = []
        

    def search(self, pkg):
        pkgs = []
        pkg_db = self.pm.db.search_pkgs(pkg)
        for p in pkg_db:
            pkgs.append(p)
        return tuple(pkgs)

    
    def get_name(self, pkg):
        name = self.pm.db.get_pkg(pkg).get_app_name()
        if not name:
            name = self.pm.db.get_pkg(pkg).get_name()
        return name


    def get_available(self, db=[]):
        for repo in self.pm.get_repos():
            repository = self.pm.db.get_repo_pkgs(repo)
            for pkg in repository:
                db.append(pkg)
        return tuple(db)

    
    def get_installed(self):
        pkgs = []
        for pkg in self.pm.db.get_installed_pkgs():
            pkgs.append(pkg.get_name())
        return tuple(pkgs)


    def get_details(self, pkg):
        p = self.pm.db.get_pkg(pkg)
        info = {}
        info["format"] = "package"
        info["files"] = p.get_files()
        info["app_id"] = p.get_app_id()
        info["title"] = p.get_app_name()
        info["backups"] = p.get_backups()
        info["build_date"] = Utils.glib_date_to_string(p.get_build_date())
        info["check_depends"] = p.get_checkdepends()
        info["conflits"] = p.get_conflicts()
        info["depends"] = p.get_depends()
        info["description"] = p.get_desc()
        info["download_size"] = Utils.convert_bytes_to_human(p.get_download_size())
        info["groups"] = p.get_groups()
        info["icon"] = p.get_icon()
        info["pkg_id"] = p.get_id()
        info["install_date"] = Utils.glib_date_to_string(p.get_install_date())
        info["installed_size"] = Utils.convert_bytes_to_human(p.get_installed_size())
        info["installed_version"] = p.get_installed_version()
        info["launchable"] = p.get_launchable()
        info["license"] = p.get_license()
        info["long_description"] = p.get_long_desc()
        info["makedepends"] = p.get_makedepends()
        info["name"] = p.get_name()
        info["optdepends"] = p.get_optdepends()
        info["optionalfor"] = p.get_optionalfor()
        info["packager"] = p.get_packager()
        info["provides"] = p.get_provides()
        info["reason"] = None
        if p.get_reason():
            info["reason"] = p.get_reason()
        info["replaces"] = p.get_replaces()
        info["repository"] = p.get_repo()
        info["required_by"] = p.get_requiredby()
        info["screenshots"] = p.get_screenshots()
        info["url"] = p.get_url()
        info["version"] = p.get_version()
        return info