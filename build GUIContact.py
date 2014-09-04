from distutils.core import setup
import py2exe,sys
from distutils.filelist import findall
import os
import matplotlib
import glob


sys.argv.append('py2exe')

import os 
import sys 
from glob import glob
sys.stdout = open('screen.txt','w',0) 
sys.stderr = open('errors.txt','w',0) 

sys.path.insert(0, "../Filters") 
sys.path.insert(0, "../SysFiles") 

def rmdir_recursive(dir, keep=[]): 
    """Remove a directory, and all its contents if it is not already empty.""" 

    print >>sys.__stdout__,'> Removing files in directory :' + dir + ',keeping protected files...' 
    print '> Removing files in directory :' + dir + ',keeping protected files...' 
    for name in os.listdir(dir): 
        if name not in keep: 
            full_name = os.path.join(dir, name) 
            # on Windows, if we don't have write permission we can't remove 
            # the file/directory either, so turn that on 
            if not os.access(full_name, os.W_OK): 
                os.chmod(full_name, 0600) 
            if os.path.isdir(full_name): 
                rmdir_recursive(full_name, keep=keep) 
            else: 
                os.remove(full_name) 
        else: 
            print >>sys.__stdout__,'> keeping ' + name + ' in ' + dir 
            print '> keeping ' + name + ' in ' + dir 
    if keep == []: 
        print >>sys.__stdout__,'> Removing directory :' + dir + 'because no file asked to be kept.' 
        print '> Removing directory :' + dir + 'because no file asked to be kept.' 
        os.rmdir(dir) 

try: 
    rmdir_recursive('./dist', keep=".svn") 
except: 
    print >>sys.__stdout__,'./dist: nothing to remove.' 
    print './dist: nothing to remove.' 
              


opts = { 
    'py2exe': { "compressed": 1, 
                "optimize": 1, 
                #"ascii": 1, 
                "includes":["sip"],
                "bundle_files": 3, 
               'packages' : ["matplotlib.backends.backend_qt4agg", 
#                              # "matplotlib.numerix.fft", 
#                              # "matplotlib.numerix.linear_algebra", 
#                              # "matplotlib.numerix.random_array", 
#                              # "matplotlib.numerix.ma" 
                             ], 
                'excludes': ['_tkinter',
                             'Patterns',
                #             '_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg', 
                #             '_fltkagg', '_gtk', '_gtkcairo','_backend_gdk', 
                #             '_gobject','_gtkagg','_tkinter','glade','pango', 
                #             'QtCore','QtGui' 
                             ], 
                'dll_excludes': ['tk84.dll', 
                                 'tcl84.dll', 
                                  'MSVCP90.dll',
                                'libgdk_pixbuf-2.0-0.dll', 
                                'libgdk-win32-2.0-0.dll', 
                #                 'libgobject-2.0-0.dll', 
                #                 'libgtk-win32-2.0-0.dll', 
                #                 'libglib-2.0-0.dll', 
                #                 'libcairo-2.dll', 
                #                 'libpango-1.0-0.dll', 
                #                 'libpangowin32-1.0-0.dll', 
                #                 'libpangocairo-1.0-0.dll', 
                #                 'libglade-2.0-0.dll', 
                #                 'libgmodule-2.0-0.dll', 
                #                 'libgthread-2.0-0.dll', 
                #                 'tk84.dll', 
                #                 'tcl84.dll', 
                                  ] 
              } 
       } 

# Save matplotlib-data to mpl-data ( It is located in the matplotlib\mpl-data 
# folder and the compiled programs will look for it in \mpl-data 
import matplotlib 
data_files = matplotlib.get_py2exe_datafiles()
allpngs=glob('images/*.png')
print "Allpngs "+str(allpngs)
# data_files.extend([('images', ['images/new.png','images/save.png','images/saveas.png',
                        # 'images/open.png','images/exit.png','images/plus.png','images/refresh.png',
                        # 'images/minus.png','images/exportgds.png','images/exportcats.png',
                        # 'images/curve.png','images/copy.png','images/paste.png','images/selectall.png',
                        # 'images/mainIcon.png']),
data_files.extend([('images', allpngs),
                   ('ressources', ["ressources/lib_glyphs.gds"]),
                   ('plugins', ["plugins/Patterns.py","plugins/EbeamSettings.py"]),
            ])

from GUIContact import progname, progversion
setup(name=progname, 
      version=progversion, 
      author='Daniel Rueffer', 
      windows=[{'script' : 'GUIContact.py', 
                'icon_resources':[(1,'images/mainIcon.ico')], 
#                 # 'other_resources':[(24,1,manifest)], 
               }], 
      options=opts,
      data_files=data_files,
      zipfile = None, 
#      data_files=data_files
      
      ) 

#some cleanup 
rmdir_recursive('./dist/tcl') 
rmdir_recursive('./build') 
print "---Done---" 

# # opts = {
  # # 'py2exe': { "includes" : ["matplotlib.backends.backend_qt4agg","sip"],
# # 'packages' : ['matplotlib', 'pytz'],

                # # 'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',       "matplotlib.numerix.fft",
                              # # "matplotlib.backends.backend_gtkagg",
                               # # "matplotlib.numerix.linear_algebra", "matplotlib.numerix.random_array",
                             # # '_fltkagg', '_gtk','_gtkcairo' ],
                # # 'dll_excludes': ['MSVCP90.dll','libgdk-win32-2.0-0.dll',
                                 # # 'libgobject-2.0-0.dll'],
                                 # # "bundle_files":1
              # # }
       # # }

# opts = {
  # 'py2exe': { "includes" : ["sip"],
                # 'dll_excludes': ['MSVCP90.dll','libgdk_pixbuf-2.0-0.dll','libgdk-win32-2.0-0.dll'],
                                 # "bundle_files":1
              # }
       # }


# # Save matplotlib-data to mpl-data ( It is located in the matplotmpl-datalib\
# # folder and the compiled programs will look for it in \mpl-data
# # note: using matplotlib.get_mpldata_info
# matplotlibdata_files = [(r'mpl-data', glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\*.*')),
                    # # Because matplotlibrc does not have an extension, glob does not find it (at least I think that's why)
                    # # So add it manually here:
                  # (r'mpl-data', [r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
                  # (r'mpl-data\images',glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
                  # (r'mpl-data\fonts',glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))]


# setup(windows=['Calibration App.py'], options = opts,
        # data_files=matplotlibdata_files,
        # zipfile=None)