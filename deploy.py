import git
from ftplib import FTP
import sys
import json
from pathlib import Path
import os

def upload_files(ftp, files, default_remote_directory):
  for f in files:
    upload_file(ftp, f, default_remote_directory)

def login(host, username, password):
  ftp = FTP(host)
  print('Logging in as', username, '@', host)
  ftp.login(user = username, passwd = password)
  return ftp

def upload_file(ftp, f, default_remote_directory):
  # print('Uploading', f)
  ftp.cwd('/')
  p = Path(f)
  directory = str(p.parent).replace('\\', '/')
  remote_directory = default_remote_directory + '/' + directory
  try:
    ftp.cwd(remote_directory)
  except:
    print('Creating directory', remote_directory)
    ftp.mkd(remote_directory)
    ftp.cwd(remote_directory)
  filename = p.name
  full_path = directory + '/' + filename
  remote_full_path = remote_directory + '/' + filename
  nlist = ftp.nlst()
  if os.path.exists(full_path) and filename in nlist:
    ftp.storbinary('STOR /' + remote_full_path, open(full_path, 'rb'))
    print('Updating', f, 'OK')
  elif os.path.exists(full_path) and filename not in nlist:
    ftp.storbinary('STOR /' + remote_full_path, open(full_path, 'rb'))
    print('Adding', f, 'OK')
  elif not os.path.exists(full_path) and filename in nlist:
    ftp.delete('/' + remote_full_path)
    print('Removing', f, 'OK')
  else:
    print('Skipping', f)

def get_changed_files(source_hash, target_hash, excluded_files):
  repo = git.Repo('.')
  source_commit = repo.commit(source_hash)
  target_commit = repo.commit(target_hash)
  print('Checking diff from', source_hash, 'to', target_hash)
  diff = source_commit.diff(target_commit)
  changed_files = []
  for f in diff:
    filename = f.b_path
    if (filename not in excluded_files):
      # print(filename)
      changed_files.append(filename)
  return changed_files

def update_config():
  repo = git.Repo('.')
  source_hash = repo.head.commit.hexsha
  config = get_config()
  print('Updating source hash config to', source_hash)
  config['source_hash'] = source_hash
  with open('deploy.json', 'w') as o:
    json.dump(config, o, indent = 2)

def get_config():
  config = {}
  with open('deploy.json') as f:
    config = json.load(f)
  return config

def main():
  config = get_config()
  changed_files = get_changed_files(config['source_hash'], config['target_hash'], config['excluded_files'])
  print(len(changed_files), 'files changed')
  if (len(changed_files) > 0):
    ftp = login(config['host'], config['username'], config['password'])
    upload_files(ftp, changed_files, config['default_remote_directory'])
    update_config()
    print('Done')

  print()

main()
