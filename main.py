import os

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users

template.register_template_library('extrafilters')

class Challenge(db.Model):
    title = db.StringProperty(default='')
    description = db.TextProperty(default='')
    created_by = db.UserProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    approved = db.BooleanProperty(default=False)
    modified_at = db.DateTimeProperty(auto_now=True)

class Entry(db.Model):
    title = db.StringProperty(default='')
    description = db.TextProperty(default='')
    author = db.UserProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    modified_at = db.DateTimeProperty(auto_now=True)
    user_homepage_url = db.LinkProperty()
    user_download_url = db.LinkProperty()
    user_vcs_url = db.LinkProperty()
    challenge = db.ReferenceProperty()

class RequestHandler(webapp.RequestHandler):
    def render_template(self, template_name, template_values):
        path = os.path.join(os.path.dirname(__file__), template_name)
        html = template.render(path, template_values)
        self.response.out.write(html)

class MainPage(RequestHandler):
    def get(self):
        self.render_template('frontpage.html', {})

class ChallengeListPage(RequestHandler):
    def get(self):
        challenges = Challenge.all().filter('approved ==', True).order('approved').order('-modified_at').fetch(10)
        self.render_template('challenges.html', {
            'challenges': challenges
        })

class ChallengePage(RequestHandler):
    def get(self, challenge_id):
        challenge = Challenge.get_by_id(int(challenge_id))
        entries = Entry.all().filter('challenge = ', challenge.key()).fetch(10)
        moderation_status = ''
        if not challenge.approved:
            moderation_status = 'Awaiting Moderator Approval'
        self.render_template('challenge.html', {
            'challenge': challenge,
            'entries': entries,
            'moderation_status': moderation_status
        })

class EnterChallengePage(RequestHandler):
    def get(self, challenge_id):
        challenge = Challenge.get_by_id(int(challenge_id))
        self.render_template('enterchallenge.html', {
            'challenge': challenge,
            'user': users.get_current_user(),
        })

class NewChallengePage(RequestHandler):
    def get(self):
        self.render_template('newchallenge.html', {
            'user': users.get_current_user()
        })

class SubmitChallengePage(RequestHandler):
    def post(self):
        challenge = Challenge()
        challenge.title = self.request.get('challenge-title')
        challenge.description = self.request.get('challenge-description')
        challenge.created_by = users.get_current_user()
        challenge.save()
        self.redirect('/challenges/' + str(challenge.key().id()))

class AdminQueuePage(RequestHandler):
    def get(self):
        challenges = Challenge.all().filter('approved ==', False).order('approved').order('modified_at').fetch(10)
        self.render_template('adminqueue.html', {
            'challenges': challenges
        })

class AdminChallengeAcceptPage(RequestHandler):
    def post(self, challenge_id):
        challenge = Challenge.get_by_id(int(challenge_id))
        challenge.approved = True
        challenge.save()

class AdminChallengeRejectPage(RequestHandler):
    def post(self, challenge_id):
        challenge = Challenge.get_by_id(int(challenge_id))
        challenge.delete()

application = webapp.WSGIApplication([
    (r'^/$',                             MainPage),
    (r'^/top$',                          MainPage), # while / is static
    (r'^/challenges/?$',                 ChallengeListPage),
    (r'^/challenges/(\d+)$',             ChallengePage),
    (r'^/challenges/(\d+)/enter/?$',     EnterChallengePage),
    (r'^/challenges/new/?$',             NewChallengePage),
    (r'^/challenges/submit/?$',          SubmitChallengePage),
    (r'^/admin/queue/?$',                AdminQueuePage),
    (r'^/admin/challenge/accept/(\d+)$', AdminChallengeAcceptPage),
    (r'^/admin/challenge/reject/(\d+)$', AdminChallengeRejectPage),
], debug=os.environ['SERVER_SOFTWARE'].startswith('Development'))
run_wsgi_app(application)
