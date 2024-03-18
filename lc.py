#!/usr/bin/python3

import os

import json
import sys
import argparse
import subprocess
import getpass
import logging
from pathlib import Path
from lib.luks import Luks
from lib.utils import create_img_file, mkfs, mount, umount, ask_pass

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def parse_args():
    parser = argparse.ArgumentParser(
                prog='lc',
                description='LUKS containers')
    parser.add_argument('-i', '--init', action='store_true', help="Initialize a new container")
    parser.add_argument('-s', '--size', metavar="SIZE", help="Container size in MB")
    parser.add_argument('-qo', '--quick-open', action='store_true', help="Quick open container from list")
    parser.add_argument('-qc', '--quick-close', action='store_true', help="Quick close container from list")
    parser.add_argument('-o', '--open', action='store_true', help="Open container")
    parser.add_argument('-m', '--mount-path', metavar="PATH", help="PATH to mount container (default /mnt/)", default="/mnt")
    parser.add_argument('-f', '--file', metavar="NAME", help="Container path. Must end with '.lc'.")
    parser.add_argument('-pf', '--password-file', metavar="PATH", help="Use password file in PATH. Password prompted if not specified.")
    parser.add_argument('-hf', '--header-file', metavar="PATH", help="Use header file or device in PATH. Does not need to exist with --init.")
    parser.add_argument('-c', '--close', action='store_true', help="Close container")
    args = parser.parse_args()
    if args.init and not args.size:
        logging.error("You must specify --size <MB> with --init")
        sys.exit(1)
    if not args.quick_open and not args.file and not args.quick_close:
        logging.error("You must specify --file <file> when not using --quick-open or --quick-close")
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

def validate_mapper(mapper, new):
    if os.path.isfile(os.path.expanduser(f'~/.lc/{mapper}.json')) and new:
        logging.error(f'Container with this name ({mapper}) already exists')
        sys.exit(1)
    return mapper

def build_container(args):
    container = {}
    container['path'] = validate_path(args.file)
    container['size'] = args.size
    container['mount_path'] = args.mount_path
    container['password_file'] = args.password_file
    container['header_file'] = args.header_file
    container['mapper'] = validate_mapper(os.path.basename(args.file).replace('.lc', ''), args.init)
    new_container = True if args.init else False
    if not args.password_file and not args.close:
        container['password'] = ask_pass(new=new_container)
    else:
        container['password'] = None
    return container

def save_container(container):
    container['password'] = ''
    with open(os.path.expanduser(f'~/.lc/{container["mapper"]}.json'), 'w+') as f:
        f.write(json.dumps(container))

def get_container(opening):
    index = 0
    container_list = os.listdir(os.path.expanduser(f'~/.lc/'))
    for i in container_list:
        if not i.endswith('.json'):
            continue
        index += 1
        print(f"{index}) {i.replace('.json', '')}")
    if index == 0:
        logging.error("No stored container information")
        sys.exit(1)
    pick = int(input("Select container (N): "))
    with open(os.path.expanduser(f'~/.lc/{container_list[pick-1]}')) as f:
        container = json.load(f)
    # Don't ask password is container is being closed
    if not container['password_file'] and opening:
        container['password'] = ask_pass(new=False)
    else:
        container['password'] = None
    return container

def clean():
    container_list = os.listdir(os.path.expanduser(f'~/.lc/'))
    for i in container_list:
        with open(os.path.expanduser(f'~/.lc/{i}')) as f:
            container_path = json.load(f)['path']
        if not os.path.isfile(container_path):
            logging.info(f"Deleting orphan stored container info {i}")
            os.unlink(os.path.expanduser(f'~/.lc/{i}'))

def main(args):
    if args.quick_open or args.quick_close:
        container = get_container(args.quick_open)
    else:
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
        save_container(container)
        sys.exit(0)
    elif args.open or args.quick_open:
        luks = Luks(container['path'], container['mapper'], container['password'], container['header_file'], container['password_file'])
        luks.open()
        mount(f"/dev/mapper/{container['mapper']}", args.mount_path)
    elif args.close or args.quick_close:
        umount(args.mount_path)
        luks = Luks(None, container['mapper'], None, container['header_file'], container['password_file'])
        luks.close()

if __name__=="__main__":
    if os.getuid() != 0:
        logging.error("This program needs to be run as root due to mount operations")
        sys.exit(1)
    args = parse_args()
    Path(os.path.expanduser('~/.lc')).mkdir(parents=True, exist_ok=True)
    Path(args.mount_path).mkdir(parents=True, exist_ok=True)
    clean()
    main(args)
