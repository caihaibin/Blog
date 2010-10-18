from  BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch
from google.appengine.ext import db, webapp
from django import forms
from handlers import words_list
import view, re

class Site(db.Model):
    content = db.BlobProperty()
    
class SiteForm(forms.Form):
    url = forms.URLField()
    
    def get(self):        
        data = urlfetch.fetch(self.cleaned_data['url'])
        site = Site(content=data.content)
        site.put()
        return site

class IndexHandler(webapp.RequestHandler):
    def get(self):
        form = SiteForm()
        page = view.Page()
        template_values = {'form': form, }
        page.render(self, 'templates/replace/form.html', template_values)
        
    def post(self):
        page = view.Page()
        form = SiteForm(self.request.POST)
        if form.is_valid():
            site = form.get()
            self.redirect('/replace/replace/%s' % site.key())
            # site = form.get()
            # template_values = {'site': site.content,}
            # page.render(self, 'templates/replace/replace.html')
            
class ReplaceHandler(webapp.RequestHandler):
    def get(self, site_key):
        form = SiteForm()
        page = view.Page()
        site = Site.get(site_key)
        content = site.content.lower()
        found = []
        parse = None
        
        
        # for word in words_list.words_list:
            #compile = re.compile(r"""\b%s\b""" % word, re.IGNORECASE)
            # search = compile.findall(content)
            # if search:
                # found.append((word, len(search)))
                
            # count = content.count(word)
            # if count > 0:
                # found.append((word, count))
                
        soup = BeautifulSoup(content)
        found = soup.findAll(text=re.compile(r'\b(%s)\b' % ('|'.join(re.escape(s) for s in words_list.words_list.keys())), re.IGNORECASE))
            # for word in words_list.words_list:
                # find_result = soup.findAll(text=word)
                # if find_result:
                    # found.append((word, len(find_result)))
            

                
        template_values = {'form': form, 'site': site, 'found': found, 'parse': parse, }
        page.render(self, 'templates/replace/replace.html', template_values)
        
class ResultHandler(webapp.RequestHandler):
    def get(self, site_key):
        page = view.Page()
        site = Site.get(site_key)
        content = site.content.lower()
        found = []
        for k, v in words_list.words_list.items():
            if not content.find(k.lower()) == -1:
                    found.append((k, v))
        template_values = {'site': site, 'found': found,}
        page.render(self, 'templates/replace/result.html', template_values)
            
        
        