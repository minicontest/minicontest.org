from google.appengine.ext import webapp

import markdown2

register = webapp.template.create_template_register()

@register.filter
def markdown(value):
    return markdown2.markdown(value, safe_mode=True)
