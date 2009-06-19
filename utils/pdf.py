# -*- coding: utf-8 -*-
import trml2pdf

from django.template import Context, loader

from resarmll import settings

def gen_pdf(tmpl, ctx):
    if len(settings.TEMPLATE_DIRS) > 0:
        ctx['img_path'] = "%s/images/" % (settings.TEMPLATE_DIRS[0])
    t = loader.get_template(tmpl)
    return trml2pdf.parseString(t.render(Context(ctx)).encode('utf-8'))
