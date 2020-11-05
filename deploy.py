import git
from ftplib import FTP
import sys
import json
from pathlib import Path

def upload_files(files, host, username, password):
  ftp = FTP(host)
  print('Logging in as', username, '@', host)
  ftp.login(user = username, passwd = password)
  for f in files:
    # print('Uploading', f)
    ftp.cwd('/')
    p = Path(f)
    directory = str(p.parent).replace('\\', '/')
    filename = p.name
    ftp.cwd(directory)
    full_path = directory + '/' + filename
    ftp.storbinary('STOR /' + full_path, open(full_path, 'rb'))
    print('Uploading', f, 'OK')

def get_changed_files(source_hash, target_hash):
  repo = git.Repo('.')
  source_commit = repo.commit(source_hash)
  target_commit = repo.commit(target_hash)
  diff = source_commit.diff(target_commit)
  changed_files = []
  for f in diff:
    filename = f.b_path
    if (filename not in excluded_files):
      # print(filename)
      changed_files.append(filename)
  return changed_files

excluded_files = [
  'application/config/production/config.php',
  'application/config/production/database.php',
  'application/config/stage/config.php',
  'application/config/stage/database.php',
  'application/doc/schema.sql',
  '.gitignore',
  '.htaccess',
  'deploy.py',
  'README.md',
]

def update_config():
  repo = git.Repo('.')
  source_hash = repo.head.commit.hexsha
  config = get_config()
  config['source_hash'] = source_hash
  with open('deploy.json', 'w') as o:
    json.dump(config, o, indent = 2)

def get_config():
  config = {}
  with open('deploy.json') as f:
    config = json.load(f)
  return config

config = get_config()
changed_files = get_changed_files(config['source_hash'], config['target_hash'])
print(len(changed_files), 'files changed')
if (len(changed_files) > 0):
  upload_files(changed_files, config['host'], config['username'], config['password'])
  update_config()
  print('Done')

print()
