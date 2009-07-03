# -*- coding: utf-8 -*-
import os.path, cairo

from cStringIO import StringIO
from reportlab.platypus import PageTemplate, BaseDocTemplate, SimpleDocTemplate, Image, PageBreak
from reportlab.lib.pagesizes import *
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image as PImage

from resarmll import settings

PROFILES = {
    'purple': {
        'name': 'Purple',
        'source_rgba': (0.3, 0.3, 0.5, 0.6),
        'gradients': [
            (0, 0.3, 0.3 ,0.5, 1),
            (0.45, 0.3, 0.3 ,0.5, 0),
            (0.90, 0.3, 0.3, 0.5, 0),
            (0.93, 0.3, 0.3, 0.5, 0.8),
            (1, 0.3, 0.3, 0.5, 0.8),
        ],
    },
    'orange': {
        'name': 'Orange',
        'source_rgba': (1, 0.8, 0, 0.6),
        'gradients': [
            (0, 1, 0.5 ,0, 1),
            (0.45, 1, 0.7 ,0, 0),
            (0.90, 1, 0.5, 0, 0),
            (0.93, 1, 0.5, 0, 1),
            (1, 1, 0.5, 0, 1),
        ],
    },
    'green': {
        'name': 'Green',
        'source_rgba': (0, 0, 1, 0.6),
        'gradients': [
            (0, 0, 0.7 ,0.4, 1),
            (0.45, 0, 0.7 ,0.4, 0.1),
            (0.90, 0, 0.7, 0.4, 0.2),
            (0.93, 0, 0.7, 0.4, 1),
            (1, 0, 1, 0.6, 1),
        ],
    },
    'purple2': {
        'name': 'Purple2',
        'source_rgba': (0, 0.6, 0, 0.6),
        'gradients': [
            (0, 0.6, 0 ,0.6, 1),
            (0.45, 0.6, 0 ,0.6, 0),
            (0.90, 0.6, 0, 0.6, 0),
            (0.93, 0.6, 0, 0.6, 1),
            (1, 0.6, 0, 0.6, 1),
        ],
    },
    'red': {
        'name': 'Red',
        'source_rgba': (1, 0, 0, 0.6),
        'gradients': [
            (0, 1, 0 ,0, 0.7),
            (0.45, 1, 0 ,0, 0.1),
            (0.90, 1, 0, 0, 0.1),
            (0.93, 1, 0, 0, 1),
            (1, 1, 0, 0, 1),
        ],
    },
    'blue': {
        'name': 'Blue',
        'source_rgba': (0, 0, 1, 0.6),
        'gradients': [
            (0, 0, 0, 1, 0.9),
            (0.45, 0, 0 ,1, 0.1),
            (0.90, 0, 0, 1, 0.1),
            (0.93, 0, 0, 1, 1),
            (1, 0, 0, 1, 0.6),
        ],
    },
    'brown': {
        'name': 'Brown',
        'source_rgba': (0.43, 0.18, 0.03, 0.6),
        'gradients': [
            (0, 0.43, 0.18, 0.03, 0.9),
            (0.45, 0.43, 0.18, 0.03, 0.1),
            (0.90, 0.43, 0.18, 0.03, 0.1),
            (0.93, 0.43, 0.18, 0.03, 1),
            (1, 0.43, 0.18, 0.03, 0.6)
        ],
    },
    'turquoise': {
        'name': 'Turquoise',
        'source_rgba': (0.2, 0.4, 0.4, 0.6),
        'gradients': [
            (0, 0.2, 0.4, 0.4, 0.9),
            (0.45, 0.2, 0.4, 0.4, 0.1),
            (0.90, 0.2, 0.4, 0.4, 0.1),
            (0.93, 0.2, 0.4, 0.4, 1),
            (1, 0.2, 0.4, 0.4, 0.6)
        ],
    },
}
COLORS = tuple((x, PROFILES[x]['name']) for x in PROFILES)
TEXT_COLORS = {
    'default': (1, 1, 1),
    'name': (0.27, 0.27, 0.27),
    'desc': (0.27, 0.27, 0.27),
}

def get_path_png(id):
    return settings.BADGE_PNG_DEST_DIR+str(id)+'.png'

def get_path_big_png(id):
    return settings.BADGE_BIG_PNG_DEST_DIR+str(id)+'.png'

def get_path_big_png_portrait(id):
    return settings.BADGE_BIG_PNG_DEST_DIR+str(id)+'p.png'

def get_path_pdf(id):
    return settings.BADGE_PDF_DEST_DIR+str(id)+'.pdf'

def get_path_pdf_printer(id):
    return settings.BADGE_PRINTER_PDF_DEST_DIR+str(id)+'.pdf'

def get_path_pdf_printer_portrait(id):
    return settings.BADGE_PRINTER_PDF_DEST_DIR+str(id)+'p.pdf'


class myImageReader:
    def __init__(self, fileName):
        self.fileName = fileName
        self._image = None
        self._width = None
        self._height = None
        self._transparent = None
        self._data = None
        if _isPILImage(fileName):
            self._image = fileName
            self.fp = fileName.fp
            try:
                self.fileName = self._image.fileName
            except AttributeError:
                self.fileName = 'PILIMAGE_%d' % id(self)

class cairoContext(cairo.Context):

    def use_font(self, font):
        """
        Set the font from a string. E.g. 'sans 10' or 'sans italic bold 12'
        only restriction is that the font name should be the first option and
        the font size as last argument
        """
        font = font.split()
        self.select_font_face(font[0],
            'italic' in font and cairo.FONT_SLANT_ITALIC or cairo.FONT_SLANT_NORMAL,
            'bold' in font and cairo.FONT_WEIGHT_BOLD or cairo.FONT_WEIGHT_NORMAL)
        self.set_font_size(float(font[-1]))

    def write_text_top_left(text, slant, ):
        pass

    def write_text_top_center():
        pass

    def write_text_top_right(self, text, x, y, font, vspace=0, hspace=0):
        self.save()
        self.use_font(font)
        xb,yb,ww,hh,xa,ya = self.text_extents(text)
        x = x-ww-xb-vspace
        y = y+hh+hspace
        self.move_to(x, y)
        self.show_text(text)
        self.restore()

    def write_text_middle_left(self, text, x, y, font, vspace=0, hspace=0):
        self.save()
        self.use_font(font)
        xb,yb,ww,hh,xa,ya = self.text_extents(text)
        x = x+vspace
        y = y+(hh/2)+hspace
        self.move_to(x, y)
        self.show_text(text)
        self.restore()

    def write_text_middle_center(self, text, x, y, font, vspace=0, hspace=0):
        self.save()
        self.use_font(font)
        xb,yb,ww,hh,xa,ya = self.text_extents(text)
        x = x-(ww/2)-xb-vspace
        y = y+(hh/2)+hspace
        self.move_to(x, y)
        self.show_text(text)
        self.restore()

    def write_text_middle_right(self, text, x, y, font, vspace=0, hspace=0):
        self.save()
        self.use_font(font)
        xb,yb,ww,hh,xa,ya = self.text_extents(text)
        x = x-ww-xb-vspace
        y = y+(hh/2)+hspace
        self.move_to(x, y)
        self.show_text(text)
        self.restore()

    def write_text_bot_left():
        pass

    def write_text_bot_center(self, text, x, y, font, vspace=0, hspace=0):
        self.save()
        self.use_font(font)
        xb,yb,ww,hh,xa,ya = self.text_extents(text)
        x = x-(ww/2)-xb-vspace
        y = y-hspace
        self.move_to(x, y)
        self.show_text(text)
        self.restore()

    def write_text_bot_right(self, text, x, y, font, vspace=0, hspace=0):
        self.save()
        self.use_font(font)
        xb,yb,ww,hh,xa,ya = self.text_extents(text)
        x = x-ww-xb-vspace
        y = y-hspace
        self.move_to(x, y)
        self.show_text(text)
        self.restore()

    def adjust_font_to_fit(self, text, font, max_x, max_y):
        self.save()
        self.use_font(font)
        font_size = float(font.split()[-1])
        while font_size > 0:
            self.set_font_size(font_size)
            xb,yb,ww,hh,xa,ya = self.text_extents(text)
            if ww < max_x and hh < max_y:
                break
            font_size -= 1.0
        self.restore()
        return " ".join(font.split()[:-1] + [str(font_size) ])

class BadgeGenerator:
    def __init__(self, id, name, badge_text, badge_text_alt, badge_color, desc, fingerprint, email):
        self.user_id = id
        self.user_name = name.strip()
        self.user_badge_text = badge_text.strip()
        self.user_badge_alt_text = badge_text_alt.strip()
        self.user_badge_color = badge_color
        self.user_desc = desc.strip()
        self.user_fingerprint = fingerprint.strip()
        self.email = email
        if self.user_fingerprint == '':
            self.email = ''
        self.organisation_text = settings.BADGE_CITY

    def create_big_png(self):
        # image de fond
        self.bg = settings.BADGE_BIG_BG_IMAGE
        # destination file
        self.dest = settings.DOCUMENT_ROOT + get_path_big_png(self.user_id)
        # dimension du badge
        self.dimx, self.dimy = 1050, 637
        # footer height
        self.footer_height = 45

        # various fonts
        self.organisation_font = "Sans 50"
        self.user_badge_font = "Sans bold 56"
        self.user_badge_alt_font = "Sans italic 46"
        self.fingerprint_font = "Sans 30"
        self.user_name_font = "Sans bold 70"
        self.user_desc_font = "Sans bold 80"
        self.email_font = "Sans 40"

        # positions
        self.organisation_x, self.organisation_y = self.dimx-10, 30
        self.organisation_padding_x, self.organisation_padding_y = 8, 6
        self.user_badge_x, self.user_badge_y = 10, 30
        self.user_badge_padding_x, self.user_badge_padding_y = 10, 0
        self.user_badge_alt_x, self.user_badge_alt_y = 10,100
        self.user_badge_alt_padding_x, self.user_badge_alt_padding_y = 10, 0
        self.fingerprint_x, self.fingerprint_y = self.dimx/2, self.dimy-22
        self.user_name_x, self.user_name_y = self.dimx/2, self.dimy/2
        self.user_name_padding_x, self.user_name_padding_y = 20, 0
        self.user_desc_x, self.user_desc_y = self.dimx/2, self.dimy-70
        self.user_desc_padding_x, self.user_desc_padding_y = 20, 0
        self.email_x, self.email_y = self.dimx-10, 100
        self.email_padding_x, self.email_padding_y = 8, 10

        self.create()

    def create_png(self):
        # image de fond
        self.bg = settings.BADGE_BG_IMAGE
        # destination file
        self.dest = settings.DOCUMENT_ROOT + get_path_png(self.user_id)
        # dimension du badge
        self.dimx, self.dimy = 319, 195
        # footer height
        self.footer_height = 15

        # various fonts
        self.organisation_font = "Sans 16"
        self.user_badge_font = "Sans bold 20"
        self.user_badge_alt_font = "Sans italic 16"
        self.fingerprint_font = "Sans 9"
        self.user_name_font = "Sans bold 30"
        self.user_desc_font = "Sans bold 39"
        self.email_font = "Sans 13"

        # positions
        self.organisation_x, self.organisation_y = self.dimx, 15
        self.organisation_padding_x, self.organisation_padding_y = 3, 2
        self.user_badge_x, self.user_badge_y = 0, 15
        self.user_badge_padding_x, self.user_badge_padding_y = 5, 0
        self.user_badge_alt_x, self.user_badge_alt_y = 0,40
        self.user_badge_alt_padding_x, self.user_badge_alt_padding_y = 5, 0
        self.fingerprint_x, self.fingerprint_y = self.dimx/2, self.dimy-9
        self.user_name_x, self.user_name_y = self.dimx/2, self.dimy/2
        self.user_name_padding_x, self.user_name_padding_y = 10, 0
        self.user_desc_x, self.user_desc_y = self.dimx/2, self.dimy-25
        self.user_desc_padding_x, self.user_desc_padding_y = 10, 0
        self.email_x, self.email_y = self.dimx, 40
        self.email_padding_x, self.email_padding_y = 5, 5

        self.create()

    def create(self):
        # picking background
        f = open(self.bg,'rb')
        s = cairo.ImageSurface.create_from_png(f)
        f.close()

        # setup drawing area
        cr = cairoContext(s)
        # setting default color
        _r, _g, _b = TEXT_COLORS['default']
        cr.set_source_rgba(_r, _g, _b)
        cr.paint_with_alpha(0.8)

        # badge type
        if PROFILES.has_key(self.user_badge_color):
            profile = PROFILES[self.user_badge_color]
        else:
            profile = PROFILES[PROFILES.keys().pop()]

        # coloring badge
        _r, _g, _b, _a = profile['source_rgba']
        cr.set_source_rgba(_r, _g, _b, _a)
        linear = cairo.LinearGradient(0, 0, 0, self.dimy)
        for g in profile['gradients']:
            _s, _r, _g, _b, _a = g
            linear.add_color_stop_rgba(_s, _r, _g, _b, _a)
        cr.set_source(linear)

        # header layer
        cr.rectangle(0, 0, self.dimx, self.dimy)
        cr.fill()

        # footer layer
        cr.rectangle(0, self.dimy-self.footer_height, self.dimx, self.dimy)
        cr.fill()
        cr.set_source_rgb(1, 1, 1)

        # organisation title
        cr.write_text_middle_right(self.organisation_text, self.organisation_x,
                self.organisation_y, self.organisation_font,
                self.organisation_padding_x, self.organisation_padding_y)
        # badge type
        cr.write_text_middle_left(self.user_badge_text, self.user_badge_x,
                self.user_badge_y, self.user_badge_font,
                self.user_badge_padding_x, self.user_badge_padding_x)
        # badge type (alternative)
        cr.write_text_middle_left(self.user_badge_alt_text,
                self.user_badge_alt_x, self.user_badge_alt_y,
                self.user_badge_alt_font, self.user_badge_alt_padding_x,
                self.user_badge_alt_padding_x)
        # organisation title
        cr.write_text_middle_right(self.organisation_text, self.organisation_x,
                self.organisation_y, self.organisation_font,
                self.organisation_padding_x, self.organisation_padding_y)
        # badge type
        cr.write_text_middle_left(self.user_badge_text, self.user_badge_x,
                self.user_badge_y, self.user_badge_font,
                self.user_badge_padding_x, self.user_badge_padding_x)
        # badge type (alternative)
        cr.write_text_middle_left(self.user_badge_alt_text,
                self.user_badge_alt_x, self.user_badge_alt_y,
                self.user_badge_alt_font, self.user_badge_alt_padding_x,
                self.user_badge_alt_padding_x)
        # fingerprint PGP/GPG
        cr.write_text_middle_center(self.user_fingerprint, self.fingerprint_x,
                self.fingerprint_y, self.fingerprint_font)
        # email (if fingerprint)
        font = cr.adjust_font_to_fit(self.email, self.email_font,
                self.dimx*0.7-self.email_padding_x, self.dimy)
        cr.write_text_middle_right(self.email, self.email_x,
                self.email_y, font,
                self.email_padding_x, self.email_padding_y)
        # user name
        _r, _g, _b = TEXT_COLORS['name']
        cr.set_source_rgba(_r, _g, _b)
        font = cr.adjust_font_to_fit(self.user_name, self.user_name_font,
                self.dimx-self.user_name_padding_x, self.dimy)
        cr.write_text_middle_center(self.user_name, self.user_name_x,
                self.user_name_y, font)
        # user description
        _r, _g, _b = TEXT_COLORS['desc']
        cr.set_source_rgba(_r, _g, _b)
        font = cr.adjust_font_to_fit(self.user_desc, self.user_desc_font,
                self.dimx-self.user_desc_padding_x, self.dimy)
        cr.write_text_bot_center(self.user_desc, self.user_desc_x,
                self.user_desc_y, font)
        # writing file
        s.write_to_png(self.dest)


    def create_pdf(self):
        img = settings.DOCUMENT_ROOT + get_path_big_png(self.user_id)
        if os.path.isfile(img):
            pdf = settings.DOCUMENT_ROOT + get_path_pdf(self.user_id)
            sdoc = SimpleDocTemplate(pdf, pagesize=A4)
            elems = []
            w = settings.BADGE_WIDTH_MM*mm
            h = settings.BADGE_HEIGHT_MM*mm
            elems.append(Image(img, w, h))
            sdoc.build(elems)

    def create_pdf_printer(self):
        img = settings.DOCUMENT_ROOT + get_path_big_png(self.user_id)
        if os.path.isfile(img):
            pdf = settings.DOCUMENT_ROOT + get_path_pdf_printer(self.user_id)
            w = settings.BADGE_PRINTER_WIDTH_MM*mm
            h = settings.BADGE_PRINTER_HEIGHT_MM*mm
            sdoc = SimpleDocTemplate(pdf, pagesize=landscape((w,h)))
            elems = []
            elems.append(PageBreak())
            sdoc.build(elems, onFirstPage=self.create_pdf_printer_firstPage)

    def create_pdf_printer_firstPage(self, canvas, doc):
        w = settings.BADGE_PRINTER_WIDTH_MM*mm
        h = settings.BADGE_PRINTER_HEIGHT_MM*mm
        img = settings.DOCUMENT_ROOT + get_path_big_png(self.user_id)
        canvas.saveState()
        canvas.drawImage(img, 0, 0, w, h)
        canvas.restoreState()

    def create_pdf_printer_portrait(self):
        img = settings.DOCUMENT_ROOT + get_path_big_png(self.user_id)
        if os.path.isfile(img):
            pdf = settings.DOCUMENT_ROOT + get_path_pdf_printer_portrait(self.user_id)
            w = settings.BADGE_PRINTER_HEIGHT_MM*mm
            h = settings.BADGE_PRINTER_WIDTH_MM*mm
            sdoc = SimpleDocTemplate(pdf, pagesize=portrait((w,h)))
            elems = []
            elems.append(PageBreak())
            sdoc.build(elems, onFirstPage=self.create_pdf_printer_firstPage_portrait)

    def create_pdf_printer_firstPage_portrait(self, canvas, doc):
        w = settings.BADGE_PRINTER_HEIGHT_MM*mm
        h = settings.BADGE_PRINTER_WIDTH_MM*mm
        img = settings.DOCUMENT_ROOT + get_path_big_png_portrait(self.user_id)
        canvas.saveState()
        canvas.drawImage(img, 0, 0, w, h)
        canvas.restoreState()

    def create_all(self):
        self.create_png()
        self.create_big_png()
        # create a rotated image
        img = PImage.open(settings.DOCUMENT_ROOT + get_path_big_png(self.user_id)).rotate(90)
        img.save(settings.DOCUMENT_ROOT + get_path_big_png_portrait(self.user_id))
        self.create_pdf()
        self.create_pdf_printer()
        self.create_pdf_printer_portrait()

    #def masspdfbadge(self, ids):
        #top = 5*mm
        #left = 10*mm
        #vspace = 10*mm
        #hspace = 4*mm

        #w = config.badgesettings()['width']*mm
        #h = config.badgesettings()['height']*mm

        #tmp = StringIO()
        #c = canvas.Canvas(tmp, pagesize=A4, pageCompression=0)
        #c.setAuthor('RMLL organisation')
        #c.setTitle('Mass Badges Generator')

        #imgs = []
        #for id in ids:
            #f = config.getroot()+'/www/badges/'+str(id)+'.png'
            #if os.path.isfile(f):
                #imgs.append(f)
        #n = 0
        #for img in imgs:
            #xx = left + (n % 2)*w + (n % 2)*vspace
            #yy = top + (n/2)*hspace + (n/2)*h
            #c.drawInlineImage(PImage.open(img), x=xx, y=yy, width=w, height=h)
            #n += 1
            #if n==10:
                #n = 0
                #c.showPage()

        #c.showPage()
        #c.save()
        #tmp.seek(0)

        #return tmp.read()
