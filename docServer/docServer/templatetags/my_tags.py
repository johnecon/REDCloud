from __future__ import absolute_import
from django.contrib.staticfiles.storage import staticfiles_storage
from require.conf import settings as require_settings
from require.helpers import resolve_require_url, resolve_require_module
from django import template
from rest_framework.renderers import JSONRenderer
from docServer.serializers import ProjectSerializer

register = template.Library()


@register.simple_tag
def require_custom(module, script=''):
	"""
	Inserts a script tag to load the named module, which is relative to the REQUIRE_BASE_URL setting.

	If the module is configured in REQUIRE_STANDALONE_MODULES, and REQUIRE_DEBUG is False, then
	then the standalone built version of the module will be loaded instead, bypassing require.js
	for extra load performance.
	"""
	if not require_settings.REQUIRE_DEBUG and module in require_settings.REQUIRE_STANDALONE_MODULES:
		result = """<script src="{module}"></script>""".format(
			module = staticfiles_storage.url(resolve_require_module(require_settings.REQUIRE_STANDALONE_MODULES[module]["out"])),
		)
	else:
		result = """<script src="{src}" data-main="{module}"></script>""".format(
			src = staticfiles_storage.url(resolve_require_url(require_settings.REQUIRE_JS)),
			module = staticfiles_storage.url(resolve_require_module(module)),
	)
	if script != '':
		result = """{result}<script>{script}</script>""".format(result=result,script=script)
	return result


@register.inclusion_tag('admin/project/submit_line.html', takes_context=True)
def project_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (
            context['has_add_permission'] and not is_popup and
            (not save_as or context['add'])
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx


@register.filter
def serialize(obj):
    return JSONRenderer().render(ProjectSerializer(obj).data)