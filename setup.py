from distutils.core import setup, Extension
module1 = Extension('gameMath',
                    sources = ['interpolate.c'],
                    include_dirs = ['/usr/include'],
                    libraries = ['m'])
setup (name = 'gameMath',
        version = '1.0',
        description = 'game math',
        ext_modules = [module1])
