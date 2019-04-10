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
This is a short bash script you can use to create python virtualenv.
virtualenv is a tool to create isolated Python environments. virtualenv creates a folder which contains all the necessary executables to use the packages that a Python project would need.
```bash
# set enviroment variables
export verion="0.0.8.2"                   # pdb_prep current verion can be found 
                                          # in the setup file
export installation_dir="$HOME/pdb_prep"  # change $HOME to your installation path
export venv_dir="$installation_dir/$version/venv"
export source_dir="$installation_dir/src"
export git_url="https://github.com/sagivba/pdb_prep.git"
# create dirctory for this version
mkdir -p   "$venv_dir" 
cd         "$venv_dir"
virtualenv "$venv_dir" || exit 1;
```
## installing ```click```
Click is a Python package for creating beautiful command line interfaces.
if yo created virtualenv load it:
``` bash 
source     "$venv_dir/bin/activate" || exit 2
```
Update pip and install pdb_prep:
```bash
pip install --upgrade pip
pip install pdb_prep
```
