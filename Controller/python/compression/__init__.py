from flask import Flask
from flask_cors import CORS
compression = Flask(__name__)
CORS(compression)

from compression import dictionary
from compression import invertIndexCompression