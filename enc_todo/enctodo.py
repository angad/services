import requests
import argparse
import json
import sys
from os import listdir
from os.path import isfile, join, expanduser
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode 

server_url = "http://e.mewster.com/"
register_url = server_url + "register"
new_task_url = server_url + "new"
list_tasks_url = server_url + "list"


def find_rsa_key():
  '''
  finds public private key pair in ~/.ssh
  return path to the first public key 
  '''
  home_path = expanduser('~')
  SSH_PATH = home_path + "/.ssh/"
  key_files = [ f for f in listdir(SSH_PATH) if isfile(join(SSH_PATH,f)) ]
  for key_file in key_files:
    if key_file[-3:] == "pub":
      if isfile(join(SSH_PATH, key_file[:-4])):
        pubkey = join(SSH_PATH, key_file)
        privkey = join(SSH_PATH, key_file[:-4])
        if validate_keypair(pubkey, privkey):
          return pubkey, privkey
  return -1, -1


def validate_keypair(public_key_loc, private_key_loc):
  message = "atestmessage"
  try:
    encrypted = encrypt_RSA(public_key_loc, message)
    decrypted = decrypt_RSA(private_key_loc, encrypted)
    if decrypted == message:
      return True
  except (ValueError, IOError) as e:
    sys.stderr.write(str(e) + "\n") 
    return False


def encrypt_RSA(public_key_loc, message):
  '''
  param: public_key_loc Path to public key
  param: message String to be encrypted
  return base64 encoded encrypted string
  '''
  key = open(public_key_loc, "r").read()
  rsakey = RSA.importKey(key)
  rsakey = PKCS1_OAEP.new(rsakey)
  encrypted = rsakey.encrypt(message)
  return encrypted.encode('base64')


def decrypt_RSA(private_key_loc, package):
  '''
  param: public_key_loc Path to your private key
  param: package String to be decrypted
  return decrypted string
  '''
  key = open(private_key_loc, "r").read() 
  rsakey = RSA.importKey(key) 
  rsakey = PKCS1_OAEP.new(rsakey) 
  decrypted = rsakey.decrypt(b64decode(package)) 
  return decrypted


def register(pubkey):
  pubkey = open(pubkey, "r").read()
  r = requests.post(register_url, data={'pubkey':pubkey})
  if r.status_code == requests.codes.ok:
    f = open(expanduser('~') + "/.enctodo", "w")
    f.write("")
    f.close()


def create_task(task, pubkey):
  pubkey = open(pubkey, "r").read()
  r = requests.post(new_task_url, data={'pubkey': pubkey, 'task': task})
  return r.status_code == requests.codes.ok


def list_tasks(pubkey, privkey):
  pubkey = open(pubkey, "r").read()
  r = requests.post(list_tasks_url, data={'pubkey': pubkey})
  try:
    tasks = json.loads(r.text)
  except ValueError:
    sys.stderr.write("Error in retrieving list")
    return
  for task in tasks:
    print decrypt_RSA(privkey, task['task'])

def main():
  parser = argparse.ArgumentParser(description='Store tasks')
  parser.add_argument('task', metavar='task', nargs='?', type=str,
                     help='task')
  parser.add_argument('--pub-key', dest='pubkey', action='store',
                     help='location of your public key')
  parser.add_argument('--priv-key', dest='privkey', action='store',
                     help='location of your private key')
  parser.add_argument('--list', dest='list_tasks', action='store_true',
                     help='list all tasks')

  args = parser.parse_args()
  keypair_error = "Supported key pair not found. \n"
 
  home_path = expanduser('~')
  enctodo_path = "/.enctodo"

  if args.pubkey and not args.privkey:
    if not validate_keypair(args.pubkey, args.pubkey[:-4]):
      sys.stderr.write(keypair_error)
      sys.exit(1)
    else:
        args.privkey = args.pubkey[:-4]

  if not args.pubkey and args.privkey:
    if not validate_keypair(args.privkey + ".pub", args.privkey):
      sys.stderr.write(keypair_error)
      sys.exit(1)
    else:
      args.pubkey = args.privkey + ".pub"

  if args.pubkey and args.privkey:
    if not validate_keypair(args.pubkey, args.privkey):
      sys.stderr.write(keypair_error)
      sys.exit(1)
  
  if not args.pubkey and not args.privkey:
    args.pubkey, args.privkey = find_rsa_key()
    if args.pubkey == -1:
      sys.stderr.write(keypair_error)
      sys.exit(1)

  if not isfile(home_path + enctodo_path):
    register(args.pubkey)

  if args.task:
    task = encrypt_RSA(args.pubkey, args.task)
    if create_task(task, args.pubkey):
      sys.exit(0)
    else:
      sys.exit(1)

  if args.list_tasks:
    list_tasks(args.pubkey, args.privkey)


if __name__=='__main__':
  main()
