from   setuptools import setup, find_packages  
from   os.path import abspath, dirname, join

here = abspath(dirname(__file__))

with open(join(here, 'DESCRIPTION.rst')) as file:
    long_description = file.read()

setup(
    name                ='ngrid',
    version             ='0.1.0',
    description         ='less for data',
    long_description    =long_description,
    url                 ='https://github.com/twosigma/ngrid',
    packages            =['ngrid'],

    author              ='Two Sigma Open Source',
    author_email        ='',  # FIXME
    license             ='BSD',
    keywords            ='ngrid data setuptools',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    install_requires=['numpy', 'pandas', 'pytz', 'six'],
    extras_require = {
        'dev': [''],
        'test': [''],
    },

    package_data={
        'ngrid': [],
    },
    data_files=[],

    entry_points={
        'console_scripts': [
            'ngrid=ngrid.main:main',
        ],
    },
)

