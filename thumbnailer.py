#!/usr/bin/env python

import os
import math
from PythonMagick import _PythonMagick as pm
from verbose import *

src         = '../backup/.data/'
dst         = '../backup/.thumbs/'
dst_size    = (160, 120)
font        = 'fonts/courier.ttf'
font_size   = 12
font_color  = '#003366FF'
background  = '#FFFFFF00'

set_verbosity(5)

dst_size = pm.Geometry(dst_size[0], dst_size[1])

for (src_folder, folders, files) in os.walk(src):

    debug("Folder \"%s\"" % src_folder)

    src_folder = os.path.abspath(src_folder)
    dst_folder = os.path.abspath(os.path.join(dst, os.path.relpath(src_folder, src)))

    if not os.path.exists(dst_folder):
        debug("Create dir \"%s\"" % dst_folder)
        os.mkdir(dst_folder)    
    
    for src_name in files:
        src_path = os.path.join(src_folder, src_name)
        dst_path = os.path.join(dst_folder, src_name + '.png')

        if os.path.exists(dst_path):
            continue

        try:
            I = pm.Image(src_path+'[0]')
            src_size = I.size()
            if src_size.width > dst_size.width or src_size.height > dst_size.height:
                I.zoom(dst_size)
        except RuntimeError:
            I = None
        else:
            debug("\"%s\" is an image." % src_path)

        if not I:
            txt = ''
            fp = open(src_path, 'r')
            try:
                for i in range(int(math.ceil(dst_size.height() / font_size))-1):
                    txt += fp.readline().decode('utf-8')
            except UnicodeDecodeError:
                debug("\"%s\" is a binary file." % src_path)
            else:
                debug("\"%s\" is a text file." % src_path)
                I = pm.Image(dst_size.to_std_string(), background)
                I.font(font)
                I.fontPointsize(font_size)
                I.fillColor(font_color)
                I.annotate(txt.encode('utf-8'), pm.Geometry())

        if I:
            notice("Saving thumbnail \"%s\"" % dst_path)
            try:
                I.write(dst_path)
            except RuntimeError as e:
                error(str(e))
