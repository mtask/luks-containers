## lc | LUKS containers

Tool to create LUKS containers.

**NOTE! This tool is NOT command line injection safe. It uses supbrocess command with `shell=True`. You should not, for example, give non-root(sudo) users sudo access only to this command as they could use it to gain full sudo access.**

```
usage: lc [-h] [-i] [-o PATH] [-m PATH] [-p] [-pf PATH] [-hf PATH] [-c PATH]
          [-u PATH]

LUKS containers

options:
  -h, --help            show this help message and exit

Create containers:
  -i, --init            Initialize a new container

Open container:
  -o PATH, --open PATH  Open container in PATH
  -m PATH, --mount PATH
                        PATH to mount container
  -p, --password        Use password
  -pf PATH, --password-file PATH
                        Use password file in PATH
  -hf PATH, --header-file PATH
                        Use header file in PATH

Close container:
  -c PATH, --close PATH
                        Close container in PATH
  -u PATH, --umount PATH
                        Mount PATH to container (if mounted)
```

## Creating containers

* Run `-i`/`--init` to create container. All information is prompted.

```bash
$ sudo ./lc.py --init
Give directory path for the container: /tmp/
Give name for the container: test
Give size for the container(MB): 1000
Use password file [N/y]: 
LUKS password:
Verify LUKS password:
Use detached header [N/y]: 
INFO:root:Creating 1000MB container image
INFO:root:Running luksFormat to /tmp/test.lc
INFO:root:Running luksOpen to /tmp/test.lc (path) - test (mapper)
INFO:root:Fromatting containers file system to ext4
INFO:root:Running luksClose to test
INFO:root:Container created to path /tmp/test.lc
```

```bash
$ file /tmp/test.lc 
/tmp/test.lc: LUKS encrypted file, ver 2, ...
```

Container is closed after creation.

## Open and mount container

* Use `-o`/`--open` to open and mount containers.
* Add `-hf`/`--header-file <PATH>` if you used header file in initialization.
* Add `-pf`/`--password-file <PATH>` if you used password file in initialization.

```bash
$ sudo python3 lc.py --open /tmp/test.lc --password --mount /mnt/
LUKS password:
INFO:root:Running luksOpen to /tmp/test.lc (path) - test (mapper)
```

## Close and unmount container

* Use `-c`/`--close` to close and unmount containers.

```bash
$ sudo python3 lc.py --close /tmp/test.lc --umount /mnt/
INFO:root:Running luksClose to test
```
