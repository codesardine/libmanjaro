import unittest
try:
    from Manjaro.SDK import PackageManager
except Exception as e:
    print(e)

try:
    from Manjaro.SDK import Branches
except Exception as e:
    print(e)

try:
    from Manjaro.SDK import Os
except Exception as e:
    print(e)

try:
    from Manjaro.SDK import Hardware
except Exception as e:
    print(e)

class TestBranches(unittest.TestCase):

    def test_get_branch(self):
        i = Branches.Branch().get_branch()
        self.assertIsInstance(i, str)
        print(f"test get branch done!")


class TestOsInfo(unittest.TestCase):
    def test_env_variables(self):
        i = Os.Info().get_inv_variables()
        self.assertIsInstance(i, dict)
        print(f"test env variables done!")


class TestHardwareInfo(unittest.TestCase):
    def test_virtual_machine(self):
        i = Hardware.Info().is_virtual_machine()
        self.assertIsInstance(i, bool)
        print(f"test virtual machine done!")


class TestPamac(unittest.TestCase):
    def test_pkg_details(self):
        i = PackageManager.Pamac()
        p = i.get_pkg_details("gimp")
        self.assertIsInstance(p, dict)
        print(f"test pkg details done!")

    def test_snap_details(self):
        i = PackageManager.Pamac()
        pkg = "gimp"
        p = i.get_snap_details(pkg)
        self.assertEqual(p["name"], pkg)
        print(f"test snap details done!")

    def test_flatpak_details(self):
        i = PackageManager.Pamac()
        pkg = "org.gimp.GIMP"
        _id = "flathub/app/org.gimp.GIMP/x86_64/stable"
        p = i.get_flatpak_details(_id)
        self.assertEqual(p["name"], pkg)
        print(f"test flatpak details done!")

    def test_search_pkgs(self):
        i = PackageManager.Pamac()
        p = i.search_pkgs("gimp")
        self.assertIsInstance(p[0], object)
        print(f"test search pkg done!")

    def test_search_snaps(self):
        i = PackageManager.Pamac()
        s = i.search_snaps("gimp")
        self.assertIsInstance(s[0], object)
        print(f"test search snap done!")

    def test_search_flatpaks(self):
        i = PackageManager.Pamac()
        f = i.search_flatpaks("gimp")
        self.assertIsInstance(f[0], object)
        print(f"test search flatpak done!")

    def test_repos(self):
        i = PackageManager.Pamac().get_repos()
        self.assertIsInstance(i, list)
        self.assertEqual(i[0], "core")
        print(f"test repos done!")

    def test_categories(self):
        i = PackageManager.Pamac().get_categories()
        self.assertIsInstance(i, list)
        self.assertEqual(i[0], "Featured")
        print(f"test categories done!")

    def test_get_all_package_formats(self):
        i = PackageManager.Pamac()
        packages = i.get_all_pkgs()
        snaps = i.get_all_snaps()
        flatpaks = i.get_all_flatpaks()
        self.assertIsInstance(packages, tuple)
        self.assertIsInstance(packages[0], object)
        self.assertIsInstance(snaps, tuple)
        self.assertIsInstance(snaps[0], object)
        self.assertIsInstance(flatpaks, tuple)
        self.assertIsInstance(flatpaks[0], object)
        print(f"test get packages done!")

    def test_package_names(self):
        i = PackageManager.Pamac()
        self.assertIsInstance(i.get_app_name("gimp"), str)
        self.assertIsInstance(i.get_app_name("libpamac"), str)
        print(f"test get packages done!")

    def test_add_packages(self):
        pkgs = ["gimp", "inkscape"]
        i = PackageManager.Pamac()
        i.add_pkgs_to_install(pkgs)
        self.assertListEqual(pkgs, i._packages["install"]["packages"])
        print(f"test add packages done!")

    def test_remove_packages(self):
        pkgs = ["gimp", "inkscape"]
        i = PackageManager.Pamac()
        i.add_pkgs_to_install(pkgs)
        i.remove_pkgs_from_install(pkgs)
        self.assertListEqual([], i._packages["install"]["packages"])
        print(f"test remove packages done!")

    def test_package_sanitation(self):
        not_installed_pkg = "dosbox"
        installed_pkg = "pamac-gtk"
        pkgs = [installed_pkg, "non-existent", not_installed_pkg]
        i = PackageManager.Pamac()
        p = i.db.is_installed_pkg(not_installed_pkg)
        self.assertFalse(p)
        s = i.sanitize_packages(pkgs)
        self.assertListEqual([not_installed_pkg], s)
        print(f"test sanitize packages done!")


if __name__ == '__main__':
    unittest.main()
