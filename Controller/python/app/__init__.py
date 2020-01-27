from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

from app import Info
from app import createDictionary
from app import search