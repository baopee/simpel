# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sys,os
block_cipher = None



def resource_path(relative_path):    
    try:       
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

    

a = Analysis([resource_path('SimPel2018.py')],
             binaries=[],
             datas =[],
             pathex =['/home/spatz/Downloads/SimPel_Python'],
             hiddenimports=['scipy._lib',
             'scipy._lib.messagestream',
			'scipy.misc',
			'scipy.sparse'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
             
a.datas += [('SimPel_icon.png', resource_path('SimPel_icon.png'),'Data') ]      
a.datas += [('SimPel_splashicon.png', resource_path('SimPel_splashicon.png'),'Data') ]  
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          exclude_binaries=False,
          name='SimPel2018',
          debug=False,
          strip=False,
          upx=True,
          icon = resource_path('SimPel_icon.png'),
          console=True )
