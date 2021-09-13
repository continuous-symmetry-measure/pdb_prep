![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)
![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)


# General
Symmetry of proteins, an important source of their elegant structures and unique functions, is not as perfect as it may seem.
This program prepares protein files given in PDB format from either X-RAY or NMR measurements for a continuous symmetry measure (CSM) calculation. See http://wwpdb.org for more details on the PDB file format and the protein data bank. 
See https://telem.openu.ac.il/csm/ for more information on the CSM methodology.


Many PDB files contain inconsistent errors in the forms of missing residues or missing atoms. In addition, they may report on low resolution or low level Rfree values as well as extra data not required for the symmetry evaluation (e.g., ligands). Several steps are involved in the preparation procedure:  
1. The files are split into three categories according to their resolution and R_free grade as defined by FirstGlance in Jmol (https://bioinformatics.org/firstglance/fgij/notes.htm#grading):
   
   a.	Reliable  – PDB files with a resolution of up to 2.0 and an R_free grade of C (Average at this resolution). 
        The user can change the thresholds.
        
   b.	Reliable_r_grade – PDB files with a resolution of up to 2.0 and no R_free data
   
   c.	Others – PDB files with bad resolution or R_free grade below the threshold.
    
Reliable files are further processed according to the following stages:
     
2.	Removing non-coordinates lines from the atom section. 
3.	Removing ligands  and solvent lines at the end of peptides. HETATOM lines in the middle of a peptide are retained. 
4.	Cleaning gaps in the sequence according to REMARK 470 (missing residues) and REMARK 465 (missing atoms):     
    a.	If a   backbone atom is missing - the whole amino acid is deleted.     
    b.	If a   side chain atom is missing – the side chain is removed.     
    c.	For   homomers – gap on one peptide causes the removal of the related atoms from   all other peptides.     
5.	Retaining the first location in cases of alternate locations. 
6.	Removing hydrogen atoms (optional). 
7.	Ignoring PDB files for which the asymmetric unit does not represent a biological structure  (e.g., when the matrix in REMARK 350 is different from the identity matrix). 
8.	For homomers, checking that all peptides are of the same length.

 
# Usage:

## Help:
```
$ pdb_prep  --help
Usage: pdb_prep [OPTIONS] COMMAND [ARGS]...

  pdb preprations need help? try : pdb_prep COMMAND --help

Options:
  --help  Show this message and exit.

Commands:
  nmr   This procedure prepares protein files in...
  xray  This procedure prepares protein files in...
```


## NMR help:
```
$ pdb_prep nmr  --help
Usage: pdb_prep.py nmr [OPTIONS]

  This procedure prepares protein files in pdb format from NMR measurements for
  a CSM calculation according to the following stage:
  1.  Removing non-coordinates lines from the atom section.
  2.  Removing ligands and solvent lines at the end of peptides.
      HETATOM lines in the middle of a peptide are retained.
  3.  Cleaning gaps in the sequence according to REMARK 470 (missing residues)
      and REMARK 465 (missing atoms):
        a.  If a backbone atom is missing - the whole amino acid is deleted.
        b.  If a side chain atom is missing – the side chain is removed.
        c.  For homomers – gap on one peptide causes the removal of the related
            atoms from all other peptides.
  4.  Retaining the first location in cases of alternate location.
  5.  Removing hydrogen atoms (optional).
  6.  Ignoring pdb files for which the asymmetric unit does not represent a
        biological structure (e.g., non unit matrix in REMARK 350).
    7.  For homomers, checking that all peptides are of the same length.

Options:
  --pdb-dir TEXT                  The input pdb directory containing PDB files
                                  [default: .]
  --pdb-file TEXT                 Input pdb file (use this or the --pdb-dir
                                  option!)
  --with-hydrogens / --no-hydrogens
                                  Leave hydrogen atoms and hetatms from the
                                  files - default --no-hydrogens
  --ptype [homomer|heteromer|monomer]
                                  Protein stoichiometry (defualt: homomer)
  --parse-rem350 / --ignore-rem350
                                  Parse or ignore remark 350  - default
                                  --parse-rem350
  --bio-molecule-chains INTEGER   Number of peptides in remark 350
  --output-dir TEXT               Output dir  [default: output.{time}]
  --output-text / --output-json   Output report in text or json  - default
                                  --output-text
  --verbose                       Verbose mode  [default: False]
  --help                          Show this message and exit.
```

## X-ray help 
```
$ pdb_prep xray --help
Usage: pdb_prep.py xray [OPTIONS]

  This procedure prepares protein files in pdb format from X-RAY measurements for a
  CSM calculation according.
  At first, the files are split into three categories according to their resolution
  and R_free grade:
      a.  Reliable  – PDB files with a resolution of up to 2.0 and an R_free grade of C
          (Average at this resolution). Thresholds can be changed.
      b.  Reliable_r_grade – PDB files with a resolution of up to 2.0 and no R_free data
      c.  Others – PDB files with bad resolution or R_free grade

  Reliable files are further processed according to the following stages:
      1.  Removing non-coordinates lines from the atom section.
      2.  Removing ligands and solvent lines at the end of peptides. HETATOM lines in the
          middle of a peptide are retained.
      3.  Cleaning gaps in the sequence according to REMARK 470 (missing residues) and REMARK
          465 (missing atoms):
          a.  If a backbone atom is missing - the whole amino acid is deleted.
          b.  If a side chain atom is missing – the side chain is removed.
          c.  For homomers – gap on one peptide causes the removal of the related atoms from
              all other peptides.
      4.  Retaining the first location in cases of alternate location.
      5.  Removing hydrogen atoms (optional).
      6.  Ignoring pdb files for which the asymmetric unit does not represent a biological structure
          (e.g., non unit matrix in REMARK 350).
      7.  For homomers, checking that all peptides are of the same length.

Options:
  --pdb-dir TEXT                  Input pdb directory containing PDB files
                                  [default: .]
  --pdb-file TEXT                 Input pdb file (use this or the --pdb-dir
                                  option!)
  --max-resolution FLOAT          Maximum allowed resolution  [default: 2.0]
  --limit-r-free-grade [A|B|C|D|E]
                                  Limit for R_free_grade:
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
                                  Leave hydrogen atoms and hetatms from the
                                  files - default --no-hydrogens
  --ptype [homomer|heteromer|monomer]
                                  Protein stoichiometry (defualt: homomer)
  --parse-rem350 / --ignore-rem350
                                  Parse or ignore remark 350  - default
                                  --parse-rem350
  --bio-molecule-chains INTEGER   Number of peptides in remark 350
  --output-dir TEXT               Output dir  [default: output.{time}]
  --output-text / --output-json   Output report in text or json  - default
                                  --output-text
  --verbose                       Verbose mode  [default: False]
  --help                          Show this message and exit.
```


# How to install?

Installation instructions can be read in [this document](./install.md)





# Contributing
If you find a bug or have an idea for a program you'd like in this package, feel free to open an issue. Even better: feel free to make a pull request!

# Known Issues
The code fails to process PDB files for which the residue sequence numbers of the different peptides is inconsistent. 


# Project Owners 
* [Prof. Inbal Tuvi-Arad](https://www.openu.ac.il/en/personalsites/InbalTuviArad.aspx)
* [Sagiv Barhoom](https://github.com/sagivba)


