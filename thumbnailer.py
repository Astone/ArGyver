#!/usr/bin/env python

import os
import math
from PythonMagick import _PythonMagick as pm

src = '../backup/.data/'
dst = '../backup/.thumbs/'
dst_size = pm.Geometry(160, 120)
font_size = 12

for (src_folder, folders, files) in os.walk(src):

    print src_folder

    src_folder = os.path.abspath(src_folder)
    dst_folder = os.path.abspath(os.path.join(dst, os.path.relpath(src_folder, src)))

    if not os.path.exists(dst_folder):
        os.mkdir(dst_folder)    
    
    for src_name in files:
        src_path = os.path.join(src_folder, src_name)
        dst_path = os.path.join(dst_folder, src_name)

	if os.path.exists(dst_path+'.txt') or os.path.exists(dst_path+'.png'):
            continue

        txt = ''
        fp = open(src_path, 'r')
        try:
            for i in range(int(math.ceil(dst_size.height() / font_size))-1):
                txt += fp.readline().decode('utf-8')
        except UnicodeDecodeError:
            I = None 
#        else:
#            I = pm.Image(dst_size.to_std_string(), '#FFFFFF00')
#            I.strokeColor = '#000000FF'
#            I.draw( pm.DrawableText( 10 , 10 , 'PythonMagick Drawings ...' ) )
        if not I:
            try:
                I = pm.Image(src_path+'[0]')
            except RuntimeError:
                I = None

        if I:
            src_size = I.size()
            if src_size.width > dst_size.width or src_size.height > dst_size.height:
                I.zoom(dst_size)
            I.write(dst_path+'.png')
#        except RuntimeError:
#            I = None

        if not I:
            fp = open(dst_path+'.txt', 'w')
            fp.write(txt.encode('utf-8'))
            fp.close()
