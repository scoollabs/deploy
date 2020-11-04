import git
from ftplib import FTP
import sys

def upload_files(files, host, username, password):
  ftp = FTP(host)
  print('Logging in as', username, '@', host)
  ftp.login(user = username, passwd = password)
  for f in files:
    print('Uploading', f)
    ftp.storbinary('STOR ' + f, open(f, 'rb'))

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
  '.gitignore',
  '.htaccess',
  'deploy.py',
  'README.md',
]

if (len(sys.argv) == 6):
  # print(sys.argv)
  host = sys.argv[1]
  username = sys.argv[2]
  password = sys.argv[3]
  source_hash = sys.argv[4]
  target_hash = sys.argv[5]
  changed_files = get_changed_files(source_hash, target_hash)
  print(len(changed_files), 'files changed')
  upload_files(changed_files, host, username, password)
  print('Done')
else:
  print("Usage: python deploy.py <HOST> <USERNAME> <PASSWORD> <SOURCE_HASH> <TARGE_HASH>")

print()
