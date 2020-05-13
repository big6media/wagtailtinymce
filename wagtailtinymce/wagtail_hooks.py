# Copyright (c) 2016, Isotoma Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Isotoma Limited nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ISOTOMA LIMITED BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import json

from django import __version__ as DJANGO_VERSION
from django.templatetags.static import static
from django.utils import translation
from django.utils.html import escape
from django.utils.html import format_html
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from wagtail import __version__ as WAGTAIL_VERSION
from wagtail.core.whitelist import attribute_rule, check_url, allow_without_attributes

if DJANGO_VERSION >= '2.0':
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse

if WAGTAIL_VERSION >= '2.0':
    from wagtail.admin.templatetags.wagtailadmin_tags import hook_output
    from wagtail.core import hooks
    from wagtail.admin.rich_text.converters.editor_html import WhitelistRule
else:
    from wagtail.wagtailadmin.templatetags.wagtailadmin_tags import hook_output
    from wagtail.wagtailcore import hooks


def to_js_primitive(string):
    return mark_safe(json.dumps(escape(string)))


@hooks.register('insert_editor_css')
def insert_editor_css():
    css_files = [
        'wagtailtinymce/css/icons.css'
    ]
    css_includes = format_html_join(
        '\n',
        '<link rel="stylesheet" href="{0}">',
        ((static(filename),) for filename in css_files),
    )
    return css_includes + hook_output('insert_tinymce_css')


def _format_js_includes(js_files):
    return format_html_join(
        '\n',
        '<script src="{0}"></script>',
        ((static(filename),) for filename in js_files)
    )


@hooks.register('insert_editor_js')
def insert_editor_js():
    preload = format_html(
        '<script>'
        '(function() {{'
        '    "use strict";'
        '    window.tinymce = window.tinymce || {{}};'
        '    window.tinymce.base = window.tinymce.baseURL = {};'
        '    window.tinymce.suffix = "";'
        '   }}());'
        '</script>',
        to_js_primitive(static('wagtailtinymce/js/vendor/tinymce')),
    )
    js_includes = _format_js_includes([
        'wagtailtinymce/js/vendor/tinymce/jquery.tinymce.min.js',
        'wagtailtinymce/js/vendor/tinymce/tinymce.min.js',
        'wagtailtinymce/js/tinymce-editor.js',
        'wagtailtinymce/js/removeptags.js',
    ])
    return preload + js_includes + hook_output('insert_tinymce_js')


@hooks.register('insert_tinymce_js')
def images_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtailimage", {}, {});
            window.chooserUrls.imageChooserSelectFormat = {};
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtailimage.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
        to_js_primitive(reverse('wagtailimages:chooser_select_format', args=['00000000']))
    )
    js_includes = _format_js_includes([
        'wagtailimages/js/image-chooser-modal.js',
        'wagtailimages/js/image-chooser.js'
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def embeds_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtailembeds", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtailembeds.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )
    js_includes = _format_js_includes([
        'wagtailembeds/js/embed-chooser-modal.js',
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def links_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtaillink", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtaillink.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )
    js_includes = _format_js_includes([
        'wagtailadmin/js/page-chooser.js',
        'wagtailadmin/js/page-chooser-modal.js',
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def docs_richtexteditor_js():
    preload = format_html(
        """
        <script>
            registerMCEPlugin("wagtaildoclink", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtaildoclink.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )

    js_includes = _format_js_includes([
        'wagtaildocs/js/document-chooser.js',
        'wagtaildocs/js/document-chooser-modal.js',
    ])
    return preload + js_includes


@hooks.register('insert_tinymce_js')
def header_richtexteditor_js():
    return format_html(
        """
        <script>
            registerMCEPlugin("wagtailheaderlink", {}, {});
        </script>
        """,
        to_js_primitive(static('wagtailtinymce/js/tinymce-plugins/wagtailheaderlink.js')),
        to_js_primitive(translation.to_locale(translation.get_language())),
    )


@hooks.register('register_rich_text_features')
def whitelister_element_rules(features):
    common = {
        'style': True,
        'width': True,
        'margin-left': True,
        'margin-right': True,
        'padding-left': True,
        'padding-right': True,
        'height': True,
        'text-align': True,
        'vertical-align': True,
        'valign': True,
    }

    style_rule = attribute_rule(common)

    table_rule = attribute_rule(dict(common, **{
        'border': True,
        'cellpadding': True,
        'cellspacing': True,
        'class': True,
    }))
    cell_rule = attribute_rule(dict(common, **{
        'colspan': True,
        'scope': True,
        'rowspan': True,
    }))

    iframe_rule = attribute_rule({
        'width': True,
        'height': True,
        'frameborder': True,
        'marginheight': True,
        'src': True,
    })

    form_rule = attribute_rule({
        'action': True,
        'method': True,
        'style': True,
        'src': True,
    })

    input_rule = attribute_rule({
        'type': True,
        'src': True,
        'value': True,
        'name': True,
        'alt': True,
        'border': True,
    })

    features.register_converter_rule('editorhtml', 'table', [
        WhitelistRule('table', table_rule),
        WhitelistRule('tbody', allow_without_attributes),
        WhitelistRule('tr', cell_rule),
        WhitelistRule('td', cell_rule),
        WhitelistRule('th', style_rule),
        WhitelistRule('colgroup', allow_without_attributes),
        WhitelistRule('col', allow_without_attributes),
    ])

    features.register_converter_rule('editorhtml', 'headers', [
        WhitelistRule('h2', style_rule),
        WhitelistRule('h3', style_rule),
        WhitelistRule('h4', style_rule),
        WhitelistRule('h5', style_rule),
        WhitelistRule('h6', style_rule),
    ])

    features.register_converter_rule('editorhtml', 'misc', [
        WhitelistRule('blockquote', style_rule),
        WhitelistRule('sub', style_rule),
        WhitelistRule('sup', style_rule),
        WhitelistRule('pre', style_rule),
        WhitelistRule('figcaption', style_rule),
        WhitelistRule('figure', style_rule),
        WhitelistRule('code', style_rule),
    ])

    features.register_converter_rule('editorhtml', 'big6_base', [
        WhitelistRule('a', attribute_rule({'href': check_url, 'target': True, 'class': True})),
        WhitelistRule('img', attribute_rule({'src': True, 'width': True, 'height': True,
                                             'alt': True, 'class': True, })),
        WhitelistRule('pre', style_rule),
        WhitelistRule('div', style_rule),
        WhitelistRule('span', style_rule),
        WhitelistRule('p', style_rule),
    ])

    features.register_converter_rule('editorhtml', 'iframe', [
        WhitelistRule('iframe', iframe_rule),
    ])

    features.register_converter_rule('editorhtml', 'form', [
        WhitelistRule('form', form_rule),
        WhitelistRule('input', input_rule),
    ])

    features.default_features.append('table')
    features.default_features.append('headers')
    features.default_features.append('misc')
    features.default_features.append('big6_base')
    features.default_features.append('iframe')
    features.default_features.append('form')
