from distutils.core import setup
import setuptools

setup(
    name='pdb_prep',
    version='0.0.8.3',
    packages=['_Tests', 'Chemistry', 'Chemistry.PDB', 'Geometry', 'PDB_Distance', 'PDB_Prep', 'Utils'],
    install_requires=['click'],
    url='https://sagivba.github.io/pdb_prep/',
    author='Sagiv Barhoom',
    author_email='sagivba@gmail.com',
    description='pdb utils',
    test_suite='discover_tests',
    license = 'BSD 2-Clause',
    keywords='pdb-files chemistry RSCB proteins',
	entry_points={
        'console_scripts': [
            'pdb_prep = pdb_prep:cli',
        ]
    },
)
a = setuptools.__doc__
