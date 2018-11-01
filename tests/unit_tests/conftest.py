import sys
import os

my_path = os.path.abspath(__file__)
sys.path.insert(0, my_path + '/../../../src/featuretoggles/')

os.environ['PREFIX'] = 'testing'