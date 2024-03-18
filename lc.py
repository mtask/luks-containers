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

def parse_args():
    parser = argparse.ArgumentParser(
                prog='lc',
                description='LUKS containers')
    parser.add_argument('-i', '--init', action='store_true', help="Initialize a new container")
    parser.add_argument('-s', '--size', metavar="SIZE", help="Container size in MB")
    parser.add_argument('-o', '--open', action='store_true', help="Open container")
    parser.add_argument('-m', '--mount-path', metavar="PATH", help="PATH to mount container (default /mnt/)", default="/mnt")
    parser.add_argument('-f', '--file', metavar="NAME", help="Container path. Must end with '.lc'.", required=True)
    parser.add_argument('-pf', '--password-file', metavar="PATH", help="Use password file in PATH. Password prompted if not specified.")
    parser.add_argument('-hf', '--header-file', metavar="PATH", help="Use header file or device in PATH. Does not need to exist with --init.")
    parser.add_argument('-c', '--close', action='store_true', help="Close container")
    args = parser.parse_args()
    if args.init and not args.size:
        logging.error("You must specify --size <MB> with --init")
        sys.exit(1)
    return args

def create_container(path, mapper, size, password, pw_file, header):
    create_img_file(path, size)
    luks = Luks(path, mapper, password, header, pw_file)
    luks.format()
    luks.open()
    mkfs(f"/dev/mapper/{mapper}")

def validate_path(path):
    if not path.endswith('.lc'):
        logging.error('Path must end with ".lc"')
        sys.exit(1)
    return path

def build_container(args):
    container = {}
    container['path'] = validate_path(args.file)
    container['size'] = args.size
    container['mount_path'] = args.mount_path
    container['password_file'] = args.password_file
    container['header_file'] = args.header_file
    container['mapper'] = os.path.basename(args.file).replace('.lc', '')
    new_container = True if args.init else False
    if not args.password_file and not args.close:
        container['password'] = ask_pass(new=new_container)
    else:
        container['password'] = None
    return container

def main(args):
    container = build_container(args)
    if args.init:
        create_container(
            container['path'],
            container['mapper'],
            container['size'],
            container['password'],
            container['password_file'],
            container['header_file']
        )
        mount(f"/dev/mapper/{container['mapper']}", args.mount_path)
        logging.info(f"Container created to path {container['path']} and mounted to path {args.mount_path}")
        sys.exit(0)
    elif args.open:
        luks = Luks(container['path'], container['mapper'], container['password'], container['header_file'], container['password_file'])
        luks.open()
        mount(f"/dev/mapper/{container['mapper']}", args.mount_path)
    elif args.close:
        umount(args.mount_path)
        luks = Luks(None, container['mapper'], None, container['header_file'], container['password_file'])
        luks.close()

if __name__=="__main__":
    if os.getuid() != 0:
        logging.error("This program needs to be run as root due to mount operations")
        sys.exit(1)
    args = parse_args()
    main(args)
