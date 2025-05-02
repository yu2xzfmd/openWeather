import sys
import site

site.addsitedir('/home/pi/Server/openWeather/venv/lib/python3.11/site-packages')
sys.path.insert(0, '/home/pi/Server/openWeather')

from app import app as application
