from google.appengine.ext import db, webapp

from django import forms

import datetime, decimal, view

def strtotime(ms):
    s=float(ms)/1000
    ms = (round(s - math.floor(s),2))*100
    m,s=divmod(s,60)
    h,m=divmod(m,60)
    d,h=divmod(h,24)
    return datetime.time(h, m, s, ms)
    
class Player(db.Model):
    email = db.EmailProperty()
    password = db.StringProperty()
    
    def get_graph_data(self):
        stats = Stat.all().ancestor(self).filter('puzzle =', '3x3x3').filter('mode =', 'Normal').fetch(10)
        return [(stat.best_time, stat.avg5, stat.avg12, stat.start) for stat in stats]
        
class Stat(db.Model):
    start = db.DateTimeProperty()
    puzzle = db.StringProperty()
    mode = db.StringProperty()
    times = db.ListProperty(float)
    best_time = db.FloatProperty()
    worst_time = db.FloatProperty()    
    avg5 = db.FloatProperty()
    avg12 = db.FloatProperty()    
    avg5_sd = db.FloatProperty()
    avg12_sd = db.FloatProperty()
    # best_time = db.TimeProperty()
    # worst_time = db.TimeProperty()    
    # avg5 = db.TimeProperty()
    # avg12 = db.TimeProperty()    
    # avg5_sd = db.TimeProperty()
    # avg12_sd = db.TimeProperty()
    scrambles = db.ListProperty(str)
    comments = db.ListProperty(str)
    
class PlayerForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)    
    
    def clean_password(self):
        data = self.cleaned_data
        if 'email' in data:
            player = Player.get_by_key_name(data['email'])
            if player:
                if not player.password == data['password']:
                    raise forms.ValidationError('Password mismatch')
        return data['password']
                
    def login(self):
        data = self.cleaned_data        
        player = Player.get_by_key_name(data['email'])                
        if not player:
            player = Player(key_name=data['email'],
                email = data['email'],
                password = data['password'])
            player.put()
        return player
            
PUZZLE_MODE = (("Normal","Normal"),
    ("One Handed","One Handed"),
    ("Blind Folded","Blind Folded"),
    ("Fewest Moves","Fewest Moves"),
    )
class ExportForm(forms.Form):
    start = forms.DateTimeField(widget=forms.HiddenInput)
    puzzle = forms.CharField(widget=forms.HiddenInput)
    mode = forms.ChoiceField(choices=PUZZLE_MODE)
    times = forms.CharField(widget=forms.HiddenInput)
    best_time = forms.FloatField(widget=forms.HiddenInput)
    worst_time = forms.FloatField(widget=forms.HiddenInput)
    avg5 = forms.FloatField(widget=forms.HiddenInput)
    avg12 = forms.FloatField(widget=forms.HiddenInput)
    avg5_sd = forms.FloatField(widget=forms.HiddenInput)
    avg12_sd = forms.FloatField(widget=forms.HiddenInput)
    scrambles = forms.CharField(widget=forms.HiddenInput)
    comments = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def save(self, player):
        data = self.cleaned_data
        data['times'] = [round(decimal.Decimal(time)/1000,2) for time in data['times'].split(',')]
        data['scrambles'] = data['scrambles'].split(',')
        data['comments'] = data['comments'].split(',')
        stat = Stat(parent=player,
            start = data['start'],
            puzzle = data['puzzle'],
            mode = data['mode'],
            times = data['times'],
            best_time = round(data['best_time']/1000,2),
            worst_time = round(data['worst_time']/1000,2),
            avg5 = round(data['avg5']/1000,2),
            avg12 = round(data['avg12']/1000,2),
            avg5_sd = data['avg5_sd'],
            avg12_sd = data['avg12_sd'],
            scrambles = data['scrambles'],
            comments = data['comments'])
        
        # stat.best_time = strtotime(data['best_time'])
        # stat.worst_time = strtotime(data['worst_time'])
        stat.put()
        return stat
        
PUZZLES = (('SELECT', 'Seleact a puzzle'),
    ('2x2x2','2x2x2'),
    ('3x3x3','3x3x3'),
    ('4x4x4','4x4x4'),
    ('5x5x5','5x5x5'),
    ('6x6x6','6x6x6'),
    ('7x7x7','7x7x7'),
    ('Clock','Clock'),
    ('Megaminx','Megaminx'),
    ('pyraminx','Pyraminx'),
    ('Square-1','Square-1'),)
        
class GraphForm(forms.Form):
    puzzle = forms.ChoiceField(choices=PUZZLES)
    mode = forms.ChoiceField(choices=PUZZLE_MODE)
    
    def get_graph_data(self, user):
        data = self.cleaned_data
        stats = Stat.all().ancestor(user).filter('puzzle =', data['puzzle']).filter('mode =', data['mode']).fetch(10)
        return [(stat.best_time, stat.avg5, stat.avg12, stat.start) for stat in stats]
        

class ExportHandler(webapp.RequestHandler):
    def get(self):
        page = view.Page()
        page.render(self, 'templates/andy/index.html')
    def post(self):
        page = view.Page()
        
        stat, player = None, None
        check = PlayerForm(self.request.POST)
        if check.is_valid():
            player = check.login()
            check = None
            
        
        form = ExportForm(self.request.POST)
        if player and not check:
            if form.is_valid():
                stat = form.save(player)
                form = None
                self.redirect('/qqtimer/stat/%s' % stat.key())
        
        
            
        template_values = {
            'check':check,            
            'form':form,}
        page.render(self, 'templates/andy/result.html', template_values)
        
        
class PlayerHandler(webapp.RequestHandler):
    def get(self, email):
        page = view.Page()
        player = Player.get(email)
        stats = Stat.all().ancestor(player)
        form = GraphForm()        
        puzzle, mode = '3x3x3', 'Normal'
        graph_data = player.get_graph_data()
        
        if self.request.GET:            
            form = GraphForm(self.request.GET)
            if form.is_valid():
                puzzle, mode = form.cleaned_data['puzzle'], form.cleaned_data['mode']
                graph_data = form.get_graph_data(player)              
        
        
        
        
        template_values = {'email':email, 'player':player,
            'stats':stats, 'graph_data':graph_data,
            'puzzle': puzzle, 'mode':mode,
            'form':form,}
        page.render(self, 'templates/andy/user.html', template_values)
        
    
        
class StatHandler(webapp.RequestHandler):
    def get(self, stat):
        page = view.Page()
        stat = Stat.get(stat)
        player = stat.parent()
        template_values = {'stat': stat,
            'player': player,
            }
        page.render(self, 'templates/andy/stat.html', template_values)
        
class StatDeleteHandler(webapp.RequestHandler):
    def get(self, stat):
        page = view.Page()
        stat = Stat.get(stat)
        temp_stat = stat
        player = stat.parent()
        stat.delete()
        template_values = {'temp_stat': temp_stat,
            'player':player,}
        page.render(self, 'templates/andy/stat_delete.html', template_values)