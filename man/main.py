import os
from flask import Flask
import re
app = Flask(__name__)


def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
  return not bool(search(strg))

@app.route("/<command>")
def man(command):
  if " " in command or not special_match(command):
    return "invalid command"
  return os.popen("man " + command).read()

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5001)
