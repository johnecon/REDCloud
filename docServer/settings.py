import sys
import os

this_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(this_path + '/configs')) # add xtreme to our path

from configs.settings_local import *

try:
	environment = os.environ['APPLICATION_ENV']
except KeyError as e:
    environment = 'dev'

if (environment == 'dev') or ('dev' in environment):
    from configs.settings_development import *
elif environment == 'prod':
    from configs.settings_production import *