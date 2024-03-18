import sys
import subprocess
import logging

class Luks:

    def __init__(self, path, mapper, password=None, header=None, pwfile=None):
        self.path = path
        self.mapper = mapper
        self.password = password
        self.header = header
        self.pwfile = pwfile

    def format(self):
        logging.info(f"Running luksFormat to {self.path}")
        if not self.pwfile:
            if self.header:
                cmd = subprocess.Popen(f"echo -n {self.password} | /sbin/cryptsetup luksFormat --header {self.header} {self.path} -q -d -", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
            else:
                cmd = subprocess.Popen(f"echo -n {self.password} | /sbin/cryptsetup luksFormat {self.path} -q -d -", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
        else:
            if self.header:
                cmd = subprocess.Popen(f"/sbin/cryptsetup luksFormat --header {self.header} {self.path} -q -d {self.pwfile}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
            else:
                cmd = subprocess.Popen(f"/sbin/cryptsetup luksFormat {self.path} -q -d {self.pwfile}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
        if err:
            print(err.decode('UTF-8'))
            sys.exit(1)

    def open(self):
        logging.info(f"Running luksOpen to {self.path} (path) - {self.mapper} (mapper)")
        if not self.pwfile:
            if self.header:
                cmd = subprocess.Popen(f"echo -n {self.password} | /sbin/cryptsetup luksOpen --header {self.header} {self.path} {self.mapper} -d -", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
            else:
                cmd = subprocess.Popen(f"echo -n {self.password} | /sbin/cryptsetup luksOpen {self.path} {self.mapper} -d -", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
        else:
            if self.header:
                cmd = subprocess.Popen(f"/sbin/cryptsetup luksOpen --header {self.header} {self.path} {self.mapper} -d {self.pwfile}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()
            else:
                cmd = subprocess.Popen(f"/sbin/cryptsetup luksOpen {self.path} {self.mapper} -d {self.pwfile}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = cmd.communicate()

        if err:
            print(err.decode('UTF-8'))
            sys.exit(1)

    def close(self):
        logging.info(f"Running luksClose to {self.mapper}")
        subprocess.call(["/sbin/cryptsetup", "luksClose", f"{self.mapper}"])
