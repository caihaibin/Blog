#!/usr/bin/env python
#

import config
import os
import sys


from google.appengine.dist import use_library
use_library('django', '1.1')

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'externals'))



import wsgiref.handlers

from google.appengine.ext import webapp
from handlers import blog, do_openid_login, admin, error
from handlers import andy, replace


def main():
    
    application = webapp.WSGIApplication([        
        ('/', blog.IndexHandler),
        ('/blog/rss2', blog.RSS2Handler),
        ('/blog/tag/([-\w]+)', blog.TagHandler),
        ('/blog/(\d{4})', blog.YearHandler),
        ('/blog/(\d{4})/(\d{2})', blog.MonthHandler),
        ('/blog/(\d{4})/(\d{2})/(\d{2})', blog.DayHandler),
        ('/blog/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', blog.PostHandler),
        ('/admin/clear-cache', admin.ClearCacheHandler),
        ('/admin/post/create', admin.CreatePostHandler),
        ('/admin/post/edit/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', admin.EditPostHandler),
        ('/admin/update', admin.UpdateHandler),
        # Demo Purpose
        ('/qqtimer', andy.ExportHandler),
        ('/qqtimer/player/([-\w]+)', andy.PlayerHandler),
        ('/qqtimer/stat/([-\w]+)', andy.StatHandler),
        ('/qqtimer/stat/([-\w]+)/delete', andy.StatDeleteHandler),
        ('/replace', replace.IndexHandler),
        ('/replace/replace/([-\w]+)', replace.ReplaceHandler),
        ('/replace/result/([-\w]+)', replace.ResultHandler),
        # If we make it this far then the page we are looking
        # for does not exist
        ('/.*', error.Error404Handler),
        ],
        debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
