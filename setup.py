from setuptools import setup, find_packages
import codecs
import os

import gtimesheet

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="gtimesheet",

    # There are various approaches to referencing the version. For a discussion,
    # see http://packaging.python.org/en/latest/tutorial.html#version
    version=gtimesheet.__version__,

    description="gTimeLog and Timesheet integration",
    long_description=long_description,

    # The project URL.
    url='https://bitbucket.org/sirex/gtimesheet',

    # Author details
    author='Mantas Zimnickas',
    author_email='sirexas@gmail.com',

    # Choose your license
    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],

    # What does your project relate to?
    keywords='timetracking',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages.
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),

    # List run-time dependencies here. These will be installed by pip when your
    # project is installed.
    install_requires = [
        'gtimelog',
        'dataset',
        'docopt',
        'pathlib',
        'arrow',
        'matplotlib',
        'isoweek',
    ],

    # If there are data files included in your packages that need to be
    # installed, specify them here. If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'gtimesheet=gtimesheet.tools:gtimesheet',
        ],
    },
)
