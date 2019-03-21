from distutils.core import setup

setup(
    name='pdb_prep',
    version='0.0.8.2',
    packages=['_Tests', 'Chemistry','Chemistry.PDB', 'Geometry', 'PDB_Distance','PDB_Prep','Utils'],
    url='',
    install_requires=['click'],
    author='Sagiv Barhoom',
    author_email='sagivba@gmail.com',
    description='pdb utils'
)
