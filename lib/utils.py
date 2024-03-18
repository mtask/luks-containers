import logging
import subprocess
import getpass

def create_img_file(path, sizemb):
    logging.info(f"Creating {sizemb}MB container image")
    cmd = subprocess.Popen(["dd", "if=/dev/zero", f"of={path}", "bs=1M", f"count={sizemb}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = cmd.communicate()
    if "records out" not in repr(err.decode('UTF-8')):
        logging.error(f"Error in container creation: {repr(err.decode('UTF-8'))}")
        sys.exit(1)

def mkfs(mapper,fs="ext4"):
    logging.info(f"Fromatting containers file system to {fs}")
    cmd = subprocess.Popen([f"/sbin/mkfs.{fs}", mapper], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = cmd.communicate()
    if "accounting information" not in repr(out.decode('UTF-8')):
        logging.error(f"Error in container's file system creation: {repr(err.decode('UTF-8'))}")
        sys.exit(1)

def mount(src_path, dst_path):
    subprocess.call(["mount", src_path, dst_path])

def umount(path):
    subprocess.call(["umount", path])

def ask_pass(new=False):
    if not new:
        password = getpass.getpass("LUKS password:")
        return password
    while True:
        password = getpass.getpass("LUKS password:")
        password2 = getpass.getpass("Verify LUKS password:")
        if password != password2:
            print("Error: passwords do not match", file=sys.stderr)
        else:
            break
    return password
