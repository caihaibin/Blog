import datetime

from django import forms
from google.appengine.ext.db import djangoforms
from google.appengine.ext import webapp
from google.appengine.api import memcache

from models import blog
import view


def get_unpublish_list():
                
    unpublish = memcache.get('unpublish_list')
    if unpublish is not None:
        return unpublish
        
    unpublish = blog.Post.all()
    unpublish.filter('publish = ', False)
    memcache.set('unpublish_list', unpublish)
    return unpublish

class PostForm2(djangoforms.ModelForm):
    class Meta:
        model = blog.Post
        exclude = ['excerpt_html', 'body_html', 'pub_date', 'author']
    def clean_slug(self):
        data = self.cleaned_data['slug']
        data = data if not data == '' else blog.slugify(self.cleaned_data['title'])
        return data
    
class PostForm(forms.Form):
    title = forms.CharField()
    slug = forms.CharField(required=False, help_text="(leave blank to auto-generate)")
    tags = forms.CharField(help_text = "(seperate tags with spaces)")
    excerpt = forms.CharField(required=False, widget=forms.Textarea)
    body = forms.CharField(widget=forms.Textarea)
    publish = forms.BooleanField(required=False)
     
    def save(self, post=None, commit=True):
        data = self.cleaned_data
        if not post: post = blog.Post()
        post.title = data['title']
        post.slug = data['slug'] if not data['slug'] == '' else blog.slugify(data['title'])
        post.tags = data['tags'].split()
        post.excerpt = data['excerpt'] if not data['excerpt'] == '' else None
        post.body = data['body']
        post.publish = data['publish']
        post.populate_html_fields()
        if commit: post.put()
        return post        
        
class CreatePostHandler(webapp.RequestHandler):

    def get(self):
        page = view.Page() 
        form = PostForm(auto_id="item_form_%s")
        template_values = {
            'form': form,
            'unpublish': get_unpublish_list(),
            }
        page.render(self, 'templates/post_form.html', template_values)

    def post(self):
        template_values = {}
        form = PostForm(self.request.POST, auto_id="item_form_%s")
        if self.request.get('submit') == 'Submit':
            if form.is_valid():
                new_post = form.save()
                memcache.delete('unpublish')
                if new_post.publish:
                    self.redirect(new_post.get_absolute_url())
                else:
                    self.redirect('/admin/post/create')
        else:
            if form.is_valid():
                new_post = form.save(commit=False)                
                template_values['post'] = new_post                
        template_values['form'] = form            
        template_values['unpublish'] = get_unpublish_list()
        page = view.Page()
        page.render(self, 'templates/post_form.html', template_values)

class EditPostHandler(webapp.RequestHandler):

    def get(self, year, month, day, slug):
        year = int(year)
        month = int(month)
        day = int(day)

        # Build the time span to check for the given slug
        start_date = datetime.datetime(year, month, day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to check for slug uniqueness in the specified time span
        query = blog.Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.filter('slug = ', slug)

        post = query.get()

        if post == None:
            page = view.Page()
            page.render_error(self, 404)
        else:
            action_url = post.get_edit_url()            
            form = PostForm(initial={'title':post.title,
                                    'slug':post.slug,
                                    'tags':" ".join(post.tags),
                                    'excerpt':post.excerpt,
                                    'body':post.body,
                                    'publish':post.publish})
            
            #form = PostForm2(instance=post)
            template_values = {
                'action': action_url,
                'post': post,
                'form': form,
                'unpublish': get_unpublish_list()
                }

            page = view.Page()
            page.render(self, 'templates/post_form.html', template_values)

    def post(self, year, month, day, slug):
        template_values = {}
        year = int(year)
        month = int(month)
        day = int(day)

        # Build the time span to check for the given slug
        start_date = datetime.datetime(year, month, day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to check for slug uniqueness in the specified time span
        query = blog.Post.all()
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.filter('slug = ', slug)

        post = query.get()
        
        if post == None:
            page = view.Page()
            page.render_error(self, 404)
        else:
            action_url = post.get_edit_url()        
            form = PostForm(self.request.POST)
            #form = PostForm2(self.request.POST, instance=post)
            if self.request.get('submit') == 'Submit':
                if form.is_valid():
                    post = form.save(post=post)
                    if post.publish:
                        memcache.delete('unpublish')
                        self.redirect(post.get_absolute_url())
                    else:
                        self.redirect('/admin/post/create')
            else:                
                if form.is_valid():
                    post = form.save(post=post, commit=False)
                template_values['action'] = action_url
                template_values['post'] = post
                template_values['form'] = form
            template_values['unpublish'] = get_unpublish_list()
            page = view.Page()
            page.render(self, 'templates/post_form.html', template_values)

class ClearCacheHandler(webapp.RequestHandler):

    def get(self):
        memcache.flush_all()

class UpdateHandler(webapp.RequestHandler):
    def get(self):
        query = blog.Post.all()[0]
        if not query.publish:
            query = blog.Post.all()
            for post in query:
                post.publish = True
                post.put()
        self.redirect('/')