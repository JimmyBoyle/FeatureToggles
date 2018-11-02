import sys
import os

my_path = os.path.abspath(__file__)
sys.path.insert(0, my_path + '/../../../src/featuretoggles/')
print sys.path
os.environ['PREFIX'] = 'testing'