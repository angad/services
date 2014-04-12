import random
from flask import Flask
app = Flask(__name__)

@app.route("/")
def r():
  return str(random.random())

if __name__ == "__main__":
  app.run()
