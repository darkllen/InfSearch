from flask import Flask
from flask_cors import CORS
parse = Flask(__name__)
CORS(parse)

from parse import helpParse