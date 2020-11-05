# deploy

![](deploy.png)

## Requirement

This needs python (we use Python 3, and we haven't tested it in Python 2x) and GitPython to be installed.

```shell
> pip install gitpython
```

## Install

Copy the deploy.py to your git repo directory. Please add more to excluded files, the files you don't want to be deployed. For example, the READMEs and other files not necessarily needed in the server.

## Usage

Setup deploy.json config file for your FTP credentials and start commit hash.

```json
{
  "host": "127.0.0.1",
  "username": "test@localhost.com",
  "password": "password",
  "target_hash": "HEAD",
  "source_hash": "ea33526d1909c3d78e333cf77ecf45383aa45640"
}
```

Run

```shell
> python deploy.py
```

This will upload changes from ea33526d1909c3d78e333cf77ecf45383aa45640 to HEAD to your FTP hosted locally with FTP username test@localhost and password "password".
