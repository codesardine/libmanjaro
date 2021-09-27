from subprocess import Popen


class Branch():

    def __init__(self):
        self.config = "/etc/pacman-mirrors.conf"

    def get_branch(self):
        with open(self.config, "r") as f:
            for line in f:
                if "Branch = " in line:
                    branch = line.replace("Branch = ", "").replace("#", "").strip()
                    return branch


    def set_branch_mirrors(self, branch):
        if self.get_branch() != branch:
            cmd = ["pkexec", "pacman-mirrors", "--fasttrack",
                    "--api", "--set-branch", f"{branch}"]
            Popen(cmd)
