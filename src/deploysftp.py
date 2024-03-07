import git
import sys
import json
import os
import pysftp
from pathlib import Path

def upload_files(sftp, files, default_remote_directory):
    for f in files:
        upload_file(sftp, f, default_remote_directory)

def upload_file(sftp, f, default_remote_directory):
    # print('Uploading', f)
    p = Path(f)
    directory = str(p.parent).replace('\\', '/')
    remote_directory = default_remote_directory + '/' + directory
    try:
        sftp.chdir(remote_directory)
    except FileNotFoundError:
        print('Creating directory', remote_directory)
        sftp.makedirs(remote_directory)
        sftp.chdir(remote_directory)
    filename = p.name
    full_path = directory + '/' + filename
    remote_full_path = remote_directory + '/' + filename
    if sftp.exists(remote_full_path):
        sftp.put(full_path)
        print('Updating', f, 'OK')
    else:
        sftp.put(full_path)
        print('Adding', f, 'OK')

def get_changed_files(source_hash, target_hash, excluded_files):
    repo = git.Repo('.')
    source_commit = repo.commit(source_hash)
    target_commit = repo.commit(target_hash)
    print('Checking diff from', source_hash, 'to', target_hash)
    diff = source_commit.diff(target_commit)
    changed_files = []
    for f in diff:
        filename = f.b_path
        if filename not in excluded_files:
            # print(filename)
            changed_files.append(filename)
    return changed_files

def update_config(config_file):
    repo = git.Repo('.')
    source_hash = repo.head.commit.hexsha
    config = get_config(config_file)
    print('Updating source hash config to', source_hash)
    config['source_hash'] = source_hash
    with open(config_file, 'w') as o:
        json.dump(config, o, indent=2)

def get_config(config_file):
    config = {}
    with open(config_file) as f:
        config = json.load(f)
    return config

def main():
    config_file = 'deploy.json'
    if len(sys.argv) == 2:
        config_file = sys.argv[1]

    config = get_config(config_file)
    changed_files = get_changed_files(config['source_hash'], config['target_hash'], config['excluded_files'])
    print(len(changed_files), 'files changed')
    if len(changed_files) > 0:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(host=config['host'], username=config['username'], password=config['password'], cnopts=cnopts) as sftp:
            upload_files(sftp, changed_files, config['default_remote_directory'])
            update_config(config_file)
            print('Done')

    print()

main()
