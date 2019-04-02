from distutils.core import setup

import setuptools

setup(
    name='pdb_prep',
    version='0.0.8.3',
    packages=setuptools.find_packages(),
    install_requires=['click'],
    url='https://sagivba.github.io/pdb_prep/',
    author='Sagiv Barhoom',
    author_email='sagivba@gmail.com',
    description='pdb utils',
    test_suite='discover_tests',
    license='BSD 2-Clause',
    py_modules=['pdb_prep'],
    keywords='pdb-files chemistry RSCB proteins',
    entry_points={
        'console_scripts': [
            'pdb_prep.py = pdb_prep:cli',
            'pdb_info.py = pdb_info:cli',
            'pdb_distance.py = pdb_distance:cli',
        ]
    },
)
a = setuptools.__doc__
