from flask import Flask
from flask_cors import CORS
creation = Flask(__name__)
CORS(creation)

from creation import createInvertIndex
from creation import create2WordsIndex
from creation import createCoordIndex
from creation import createGramIndex
from creation import createPermutationIndex
from creation import createTrieIndex
from creation import createInvertIndexByParts
from creation import createDict
