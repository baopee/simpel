# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 11:27:37 2018

@author: stephan
"""

# -*- coding: utf-8 -*-
#setup.py
"""
Spyder Editor

This is a temporary script file.
"""

import sys
from cx_Freeze import setup, Executable, hooks

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["numpy","sys",'matplotlib.backends.backend_tkagg'], "excludes": ["PyQt4", "Tkinter"],
                     'include_files': ['SimPel_splashicon.png']}
binincludes = ['libexpat.so.1']
binpaths = ['/lib/x86_64-linux-gnu']

def load_scipy_patched(finder, module):
    """the scipy module loads items within itself in a way that causes
        problems without the entire package and a number of other subpackages
        being present."""
    finder.IncludePackage("scipy._lib")  # Changed include from scipy.lib to scipy._lib
    finder.IncludePackage("scipy.misc")
    finder.IncludePackage("scipy.sparse")

hooks.load_scipy = load_scipy_patched

# GUI applications require a different base on Windows (the default is for a
# console application).



base = None
if sys.platform == "win32":
    base = "Win32GUI"


target = Executable(
    base = base,
    icon = "SimPel_icon.png",
    script="SimPel2018.py",
    targetName = "SimPel2018", 
    )

setup(  name = "SimPel2018",
        version = "1.0.0",
        description = "Simulation of PELDOR/DEER traces",
        options = {"build_exe": build_exe_options},
        #executables = [Executable("SimPel2016.py", base=base)])
        executables = [target])
