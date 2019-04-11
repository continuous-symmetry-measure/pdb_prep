# Installation instructions (on centos7):
Those preparations are required:
- Fulfill installation prerequisites
- Create the virtual environment for python (not mandatory)
- Install click 

# Installation prerequisites
1. Install git - As root:```yum install git```
2. Install python3 - based on [those instructions](https://linuxize.com/post/how-to-install-python-3-on-centos-7/)
   - As root: ```yum install centos-release-scl```
   - As root: ```yum install rh-python36```
		
## Creating virtual environment for python (not mandatory)

virtualenv is a tool to create isolated Python environments. 
virtualenv creates a folder which contains all the necessary executables to use the packages that a Python project would need.
```bash
## set enviroment 
python3 -m venv pdb_prep_env
```
## installing ```pdb_prep```
Click is a Python package for creating beautiful command line interfaces.
if yo created virtualenv load it:
``` bash 
source     "$venv_dir/bin/activate" 
```
Update pip and install pdb_prep:
```bash
pip install --upgrade pip
pip install pdb_prep
```
