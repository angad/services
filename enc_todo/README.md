## Encrypted TODO List

Uses your public key to locally encrypt the task message and store it on the server.

To retrieve the task, it gets the encrypted task from the server and decrypts it 
with your private key. 

Only your public key is transmitted to the server to identify as a unique user
and to retrieve your tasks.

TODO: support password protected keys



    python enctodo.py --help
    usage: enctodo.py [-h] [--pub-key PUBKEY] [--priv-key PRIVKEY] [--list] [task]

    Store tasks

    positional arguments:
      task                task
    
    optional arguments:
      -h, --help          show this help message and exit
      --pub-key PUBKEY    location of your public key
      --priv-key PRIVKEY  location of your private key
      --list              list all tasks
    
