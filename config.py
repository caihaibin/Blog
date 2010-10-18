import os

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

SETTINGS = {
    'title': 'James Cai Hai Bin',
    'description': "Google App Engine-Based Blog",
    'author': 'Cai Hai Bin',
    'email': 'james_027@yahoo.com',
    'url': 'http://jamesgae.appspot.com',    
    'items_per_page': 5,
    # Enable/disable Google Analytics
    # Set to your tracking code (UA-xxxxxx-x), or False to disable
    'google_analytics': 'UA-11833477-1',
    # Enable/disable Disqus-based commenting for posts
    # Set to your Disqus short name, or False to disable
    'disqus': 'jamescaihaibin',
    
}
