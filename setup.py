from distutils.core import setup

import setuptools

from version import __VERSION__

setup(
    name='pdb_prep',
    version=__VERSION__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['click'],
    url='https://sagivba.github.io/pdb_prep/',
    author='Sagiv Barhoom',
    author_email='sagivba@gmail.com',
    description='pdb utils',
    test_suite='discover_tests',
    license='BSD 2-Clause',
    py_modules=['pdb_prep', 'pdb_info', 'pdb_prep_all', 'pdb_distance', 'version'],
    keywords='pdb-files chemistry RSCB proteins',
    entry_points={
        'console_scripts': [
            'pdb_prep = pdb_prep:cli',
            'pdb_prep_all = pdb_prep_all:pdb_prep_all',
            'pdb_info = pdb_info:cli',
            'pdb_distance = pdb_distance:cli',
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)
a = setuptools.__doc__
