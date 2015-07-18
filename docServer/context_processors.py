from django.conf import settings

def debug_mode(context):
  return {'debug_mode': settings.TEMPLATE_DEBUG}