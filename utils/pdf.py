# -*- coding: utf-8 -*-
import trml2pdf

from django.template import Context, loader

from resarmll import settings

def gen_pdf(tmpl, ctx):
    if len(settings.TEMPLATE_DIRS) > 0:
        ctx['img_path'] = "%s/images/" % (settings.TEMPLATE_DIRS[0])
    t = loader.get_template(tmpl)
    buffer = t.render(Context(ctx)).encode('utf-8')
    # no comment
    buffer = buffer.replace('è', 'e')
    buffer = buffer.replace('ô', 'o')
    buffer = buffer.replace('ä', 'a')
    buffer = buffer.replace('ü', 'u')
    return trml2pdf.parseString(buffer)
