```
usage: lc [-h] [-i] [-s SIZE] [-o] [-m PATH] -f NAME [-pf PATH] [-hf PATH]
          [-c]

LUKS containers

options:
  -h, --help            show this help message and exit
  -i, --init            Initialize a new container
  -s SIZE, --size SIZE  Container size in MB
  -o, --open            Open container
  -m PATH, --mount-path PATH
                        PATH to mount container (default /mnt/)
  -f NAME, --file NAME  Container path. Must end with '.lc'.
  -pf PATH, --password-file PATH
                        Use password file in PATH. Password prompted if not
                        specified.
  -hf PATH, --header-file PATH
                        Use header file or device in PATH. Does not need to
                        exist with --init.
  -c, --close           Close container
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

## Opening container

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

## Closing container

```bash
sudo python3 lc.py --file /tmp/test.lc --close
```

