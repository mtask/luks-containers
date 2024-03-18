## LUKS containers | lc.py

Tool to create and manage LUKS containers.

**Note that this tool is not command line injection safe. You should not, for example, allow regular user to only run this application with sudo. Main use case is on personal machine where you are the only user with sudo access.**

```
usage: lc [-h] [-i] [-s SIZE] [-qo] [-qc] [-o] [-m PATH] [-f NAME] [-pf PATH] [-hf PATH] [-c]

LUKS containers

options:
  -h, --help            show this help message and exit
  -i, --init            Initialize a new container
  -s SIZE, --size SIZE  Container size in MB
  -qo, --quick-open     Quick open container from list
  -qc, --quick-close    Quick close container from list
  -o, --open            Open container
  -m PATH, --mount-path PATH
                        PATH to mount container (default /mnt/)
  -f NAME, --file NAME  Container path. Must end with '.lc'.
  -pf PATH, --password-file PATH
                        Use password file in PATH. Password prompted if not specified.
  -hf PATH, --header-file PATH
                        Use header file or device in PATH. Does not need to exist with --init.
  -c, --close           Close container
```

### Quick start

1. Create a new container.

```bash
user@machine:~/$ sudo python3 lc.py --init --file /tmp/test.lc --size 500 
LUKS password:
Verify LUKS password:
INFO:root:Creating 500MB container image
INFO:root:Running luksFormat to /tmp/test.lc
INFO:root:Running luksOpen to /tmp/test.lc (path) - test (mapper)
INFO:root:Fromatting containers file system to ext4
INFO:root:Mounting /dev/mapper/test to /mnt
INFO:root:Container created to path /tmp/test.lc and mounted to path /mnt
```

2. Do something with the container

```bash
user@machine:~/$ sudo bash -c "echo 'secret text' > /mnt/secret.txt"
```

3. Close the container

```bash
user@machine:~/$ sudo python3 lc.py --quick-close
1) test
Select container (N): 1
INFO:root:Unmounting /mnt
INFO:root:Running luksClose to test
```

4. Re-open the container when neede

```bash
user@machine:~/$ sudo python3 lc.py --quick-open
1) test
Select container (N): 1
LUKS password:
INFO:root:Running luksOpen to /tmp/test.lc (path) - test (mapper)
INFO:root:Mounting /dev/mapper/test to /mnt
user@machine:~/$ sudo cat /mnt/secret.txt 
secret text
```

## Creating container

* With password and no header file

```
sudo python3 lc.py --init --file /tmp/test.lc --size 500
```

* With password and header file

```
sudo python3 lc.py --init --file /tmp/test.lc --size 500 --header-file /tmp/header.file
```

* With password, header file, and password file

```bash
sudo python3 lc.py --init --file /tmp/test.lc --size 500 --header-file /tmp/header.file --password-file /tmp/password.file
```

* Use `--mount-path` to specify other mount path than `/mnt/`.

## Opening containers

There are two options to open containers. One where you specify all necessary arguments. This is better suited for scripting etc.
Another option is "quick opening" where list of containers is given and you only need to select container number.

When container is created a json file is stored per container under `~/.lc/` which contains all container information (excluding password). For example:

```json
{
    "path": "/tmp/test.lc",
    "size": "500",
    "mount_path": "/mnt",
    "password_file": null,
    "header_file": null,
    "mapper": "test",
    "password": ""
}
```

JSON files' names are critical for the functionality and those should not be manually renamed.

### Opening container

**Note that creating a container will leave it open and mounted, so no need to run  --open anymore**

* With password and no header file

```bash
sudo python3 lc.py --file /tmp/test.lc --open
```

* With password and header file

```bash
sudo python3 lc.py --file /tmp/test.lc --open --header-file /tmp/header.file
```

* With password, header file, and password file

```bash
sudo python3 lc.py --open --file /tmp/test.lc --header-file /tmp/header.file --password-file /tmp/password.file
```

## Opening container - "quick"

```bash
sudo python3 lc.py --quick-open
```

## Closing container

With closing there are similar two options as with opening.

### Closing container

```bash
sudo python3 lc.py --file /tmp/test.lc --close
```

### Closing container - "quick"

```bash
sudo python3 lc.py --quick-close
```
