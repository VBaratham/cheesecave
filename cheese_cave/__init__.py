from flask import Flask

app = Flask(__name__)
from cheese_cave import views
