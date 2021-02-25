from cx_Freeze import setup, Executable 

#from distutils.core import setup
#import py2exe 
#setup(console=['SoF-http-cl.py'])

setup(name = "find_tex_flags" , 
      version = "0.1" , 
      description = "True Texture Flags Revealer" , 
      executables = [Executable("dump_tex_lump.py")]) 