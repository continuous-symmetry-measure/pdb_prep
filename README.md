![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)
![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)


# General
Symmetry of proteins, an important source of their elegant structures and unique functions, is not as perfect as it may seem.
This program prepares protein files given in PDB format from either X-RAY or NMR measurements for a continuous symmetry measure (CSM) calculation. See http://wwpdb.org for more details on the PDB file format and the protein data bank. 
See https://telem.openu.ac.il/csm/ for more information on the CSM methodology.


Many PDB files contain inconsistent errors in the forms of missing residues or missing atoms. In addition, they may report on low resolution or low level Rfree values as well as extra data not required for the symmetry evaluation (e.g., ligands). Several steps are involved in the preparation procedure:  
1. The files are split into three categories according to their resolution and R_free grade as defined by FirstGlance in Jmol (https://bioinformatics.org/firstglance/fgij/notes.htm#grading):
    a.	Reliable  – PDB files with a resolution of up to 2.0 and an R_free grade of C (Average at this resolution). The user can change the thresholds.
    b.	Reliable_r_grade – PDB files with a resolution of up to 2.0 and no R_free data
    c.	Others – PDB files with bad resolution or R_free grade below the threshold.
    
Reliable files are further processed according to the following stages:
     
1.	Removing non-coordinates lines from the atom section. 
2.	Removing ligands  and solvent lines at the end of peptides. HETATOM lines in the middle of a peptide are retained. 
3.	Cleaning gaps in the sequence according to REMARK 470 (missing residues) and REMARK 465 (missing atoms):     
    a.	If a   backbone atom is missing - the whole amino acid is deleted.     
    b.	If a   side chain atom is missing – the side chain is removed.     
    c.	For   homomers – gap on one peptide causes the removal of the related atoms from   all other peptides.     
4.	Retaining the first location in cases of alternate locations. 
5.	Removing hydrogen atoms (optional). 
6.	Ignoring PDB files for which the asymmetric unit does not represent a biological structure  (e.g., when the matrix in REMARK 350 is different from the identity matrix). 
7.	For homomers, checking that all peptides are of the same length.


# PDB files structure
Every PDB file is presented in a number of lines.
Each line in the PDB entry file consists of 80 columns.
The last character in each PDB entry should be an end-of- line (\n) indicator.
Each line in the PDB file is self-identifying.
The first six columns of every line contains a record name, that is left-justified and separated by a blank.
The record name must be an exact match to one of the stated record names in the http://wwpdb.org formatting guide.
The PDB file may also be viewed as a collection of record types.
Each record type consists of one or more lines.
Each record type is further divided into fields.

In the **pdb_prep** tool we are using only the following record types:
REMARK, MODEL, ATOM, HETATOM, TER



##  The motivation to create this program
TODO

# The purpose of the program
Sieve PDB files that are not suitable for calculating CSM and prepare PDB files that are appropriate by cleaning and handling gaps.

# Usage:

## Help:
```
$ pdb_prep.py  --help
Usage: pdb_prep.py [OPTIONS] COMMAND [ARGS]...

  pdb preprations need help? try : pdb_prep COMMAND --help

Options:
  --help  Show this message and exit.

Commands:
  nmr   This procedure prepares protein files in...
  xray  This procedure prepares protein files in...
```

## nmr help:
```
$ pdb_prep.py nmr  --help
Usage: pdb_prep.py nmr [OPTIONS]

  This procedure prepares protein files in pdb format from NMR measurements for a CSM calculation according
  to the following stage:
      1.  Removing non-coordinates lines from the atom section.
      2.  Removing ligands and solvent lines at the end of peptides. HETATOM lines in the middle of a peptide are
          retained.
      3.  Cleaning gaps in the sequence according to REMARK 470 (missing residues) and
          REMARK 465 (missing atoms):
          a.  If a backbone atom is missing - the whole amino acid is deleted.
          b.  If a side chain atom is missing – the side chain is removed.
          c.  For homomers – gap on one peptide causes the removal of the related atoms from all other peptides.
      4.  Retaining the first location in cases of alternate location.
      5.  Removing hydrogen atoms (optional).
      6.  Ignoring pdb files for which the asymmetric unit does not represent a biological structure
          (e.g., non unit matrix in REMARK 350).
      7.  For homomers, checking that all peptides are of the same length.

Options:
  --pdb-dir TEXT                  the input pdb directory containing PDB files
                                  [default: .]
  --pdb-file TEXT                 input pdb file (use this or the --pdb-dir
                                  option!)
  --with-hydrogens / --no-hydrogens
                                  sieve hydrogen atoms and hetatms from the
                                  files  [default: False]
  --is-homomer / --is-hetromer    process the file as homomer or hetromer
                                  [default: True]
  --output-dir TEXT               output dir  [default: output.{time}]
  --verbose                       verbose mode  [default: False]
  --help                          Show this message and exit.
```

## xray help
```
$ pdb_prep.py xray --help
    This procedure prepares protein files in pdb format from X-RAY measurements for a CSM calculation according. 
    At first, the files are split into three categories according to their resolution and R_free grade:
    a.  Reliable  – PDB files with a resolution of up to 2.0 and an R_free grade of C (Average at this resolution). 
           Thresholds can be changed.
    b.  Reliable_r_grade – PDB files with a resolution of up to 2.0 and no R_free data
    c.  Others – PDB files with bad resolution or R_free grade
    
    Reliable files are further processed according to the following stages:
    1.  Removing non-coordinates lines from the atom section.
    2.  Removing ligands and solvent lines at the end of peptides. HETATOM lines in the middle of a peptide are retained.
    3.  Cleaning gaps in the sequence according to REMARK 470 (missing residues) and REMARK 465 (missing atoms):
        a.  If a backbone atom is missing - the whole amino acid is deleted.
        b.  If a side chain atom is missing – the side chain is removed.
        c.  For homomers – gap on one peptide causes the removal of the related atoms from all other peptides.
        4.  Retaining the first location in cases of alternate location.
    5.  Removing hydrogen atoms (optional).
    6.  Ignoring pdb files for which the asymmetric unit does not represent a biological structure
        (e.g., non unit matrix in REMARK 350).
    7.  For homomers, checking that all peptides are of the same length.

Options:
  --pdb-dir TEXT                  input pdb directory containing PDB files
                                  [default: .]
  --pdb-file TEXT                 input pdb file (use this or the --pdb-dir
                                  option!)
  --max-resolution FLOAT          maximum allowed resolution  [default: 2.0]
  --limit-r-free-grade [A|B|C|D|E]
                                  limit for R_free_grade:
                                  A - MUCH BETTER THAN
                                  AVERAGE at this resolution
                                  B - BETTER THAN
                                  AVERAGE at this resolution
                                  C - AVERAGE at
                                  this resolution
                                  D - WORSE THAN AVERAGE at
                                  this resolution
                                  E - UNRELIABLE  [default: C]
  --with-hydrogens / --no-hydrogens
                                  sieve hydrogen atoms and hetatms from the
                                  files  [default: False]
  --is-homomer / --is-heteromer    process the file as homomer or heteromer
                                  [default: True]
  --output-dir TEXT               output dir  [default: output.{time}]
  --verbose                       verbose mode  [default: False]
  --help                          Show this message and exit.

```






# Contributing
If you find a bug or have an idea for a program you'd like in this package, feel free to open an issue. Even better: feel free to make a pull request!

# Known Issues
The code fails to process PDB files for which the residue sequence numbers of the different peptides is inconsistent. 


# Project Owners 
* Dr. Inbal Tuvi-Arad (https://www.openu.ac.il/en/personalsites/InbalTuviArad.aspx)
* Sagiv Barhoom (https://github.com/sagivba)


