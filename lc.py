#!/usr/bin/python3

import os
import sys
import argparse
import subprocess
import getpass
import logging
from lib.luks import Luks
from lib.utils import create_img_file, mkfs, mount, umount, ask_pass

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def init_q():
    dir_path = input("Give directory path for the container: ")
    if not os.path.isdir(dir_path):
        logging.error("Directory path does not exist")
        sys.exit(1)
    mapper = input("Give name for the container: ")
    size = input("Give size for the container(MB): ")
    q_pw = input("Use password file [N/y]: ")
    if q_pw.lower() == "y":
        pw_file = input("Give path to EXISTING password file: ")
        password = None
        if not os.path.isfile(pw_file):
            logging.error("Password file does not exist")
            sys.exit(1)
    else:
        password = ask_pass(new=True)
        pw_file = None
    q_h = input("Use detached header [N/y]: ")
    if q_h.lower() == "y":
        header = input("Give path to header file/device: ")
    else:
        header = None
    return dir_path, mapper, size, password, pw_file, header

def parse_args():
    parser = argparse.ArgumentParser(
                prog='lc',
                description='LUKS containers')
    i_parser = parser.add_argument_group(title="Create containers")
    i_parser.add_argument('-i', '--init', action='store_true', help="Initialize a new container")
    o_parser = parser.add_argument_group(title="Open container")
    o_parser.add_argument('-o', '--open',metavar="PATH", help="Open container in PATH")
    o_parser.add_argument('-m', '--mount',metavar="PATH", help="PATH to mount container")
    o_parser.add_argument('-p', '--password', action='store_true', help="Use password")
    o_parser.add_argument('-pf', '--password-file', metavar="PATH", help="Use password file in PATH")
    o_parser.add_argument('-hf', '--header-file', metavar="PATH", help="Use header file in PATH")
    c_parser = parser.add_argument_group(title="Close container")
    c_parser.add_argument('-c', '--close', metavar="PATH", help="Close container in PATH")
    c_parser.add_argument('-u', '--umount',metavar="PATH", help="Mount PATH to container (if mounted)")
    args = parser.parse_args()
    return args

def create_container(path, mapper, size, password, pw_file, header):
    create_img_file(path, size)
    luks = Luks(path, mapper, password, header, pw_file)
    luks.format()
    luks.open()
    mkfs(f"/dev/mapper/{mapper}")
    luks.close()

def main(args):
    if args.init:
        dir_path, mapper, size, password, pw_file, header = init_q()
        path = os.path.join(dir_path, f"{mapper}.lc")
        create_container(path, mapper, size, password, pw_file, header)
        logging.info(f"Container created to path {path}")
        sys.exit()
    elif args.open:
        if args.password:
            password = ask_pass()
        else:
            password = None
        mapper = os.path.basename(args.open).replace('.lc', '')
        luks = Luks(args.open, mapper, password, args.header_file, args.password_file)
        luks.open()
        mount(f"/dev/mapper/{mapper}", args.mount)
    elif args.close:
        mapper = os.path.basename(args.close).replace('.lc', '')
        if args.umount:
            umount(args.umount)
        luks = Luks(None, mapper, None, args.header_file, args.password_file)
        luks.close()

if __name__=="__main__":
    if os.getuid() != 0:
        logging.error("This program needs to be run as root due to mount operations")
        sys.exit(1)
    args = parse_args()
    main(args)
