![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)
![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)


# General
The Protein Data Bank (PDB) is an archive of experimentally determined three-dimensional structures of biological macromolecules that serves a global community of researchers, educators, and students.
The data contained in the archive include atomic coordinates, crystallographic structure factors, and NMR experimental data. Aside from coordinates, each deposition also includes the names of molecules, primary and secondary structure information, sequence database references, where appropriate, and ligand and biological assembly information, details about data collection and structure solution, and bibliographic citations.
This comprehensive guide describes the "PDB format" used by the members of the worldwide Protein Data Bank (wwPDB; Berman, H.M., Henrick, K. and Nakamura, H. Announcing the worldwide Protein Data Bank. Nat Struct Biol 10, 980 (2003)). Questions should be sent to info@wwpdb.org

Information about file formats and data dictionaries can be found at http://wwpdb.org.



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
Usage: pdb_prep.py xray [OPTIONS]

  This procedure prepares protein files in pdb format from X-RAY measurements for a CSM calculation according.
  At first, the files are split into three categories according to their resolution and R_free grade:
  a.  Reliable  – PDB files with a resolution of up to 2.0 and an R_free grade of C (Average at this resolution).
         Thresholds can be changed.
  b.  Reliable_r_grade – PDB files with a resolution of up to 2.0 and no R_free data
  c.  Others – PDB files with bad resolution or R_free grade

  Reliable files are further processed according to the following stages: 1.
  Removing non-coordinates lines from the atom section. 2.  Removing ligands
  and solvent lines at the end of peptides. HETATOM lines in the middle of a
  peptide are retained. 3.  Cleaning gaps in the sequence according to
  REMARK 470 (missing residues) and REMARK 465 (missing atoms):     a.  If a
  backbone atom is missing - the whole amino acid is deleted.     b.  If a
  side chain atom is missing – the side chain is removed.     c.  For
  homomers – gap on one peptide causes the removal of the related atoms from
  all other peptides.     4.  Retaining the first location in cases of
  alternate location. 5.  Removing hydrogen atoms (optional). 6.  Ignoring
  pdb files for which the asymmetric unit does not represent a biological
  structure     (e.g., non unit matrix in REMARK 350). 7.  For homomers,
  checking that all peptides are of the same length.

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
  --is-homomer / --is-hetromer    process the file as homomer or hetromer
                                  [default: True]
  --output-dir TEXT               output dir  [default: output.{time}]
  --verbose                       verbose mode  [default: False]
  --help                          Show this message and exit.

```













# Program steps:
TODO
foreach file in the  folders:TODO
In each case, the following actions were carried out:
## Step 1 - Eliminate "noise" using the information from the atoms reords
### Sieving of hydrogen atoms
This is an optional step of the process
in this step we itereting over the __pdb_chains__ in the __pdb__ objects and filtering the hydrogen atoms
### Treatment of alternate location indicator
if the altloc attribute of the __pdb_atom__ is 'A' or not defined (empty string), then it is set to None value,
else the atome is remoed from the __pdb_chain__



## Step 2 - handling residues gaps in the chains of each model
### handling residues gaps as they appear in notice 465
TODO
### handling residues gaps according to residues  sequences
TODO: *will be implemented in the future*
## Step 3 - handling the gaps of atoms
-  handling the gaps of atoms as stated in remark 470

# Print summary report

# implementaion
## data structures
The  data structures are packaged in __Chemistry.PDB__
* __pdb__ is a __list__ of pdb_models
  pdb has the following attributes:
    - remarks - a __dict__ (key-value) of __pdb_remark__ objects
    - file_name

* __pdb_model__ is a __list__ of __pdb_chains__ objects
  pdb_model one  attribute:
    - model_numbel- string of the model identifier

* __pdb_chain__ is a __list__ of __pdb_atom__ objects
	- chain_id

* __pdb_atom__ is a simple object
  pdb_atom has attributes such as:
    - atom_serial_number
    - atom_name
    - resname
    - resseq
    - chain_id...
the input record format is line with the following data:
        ```
        COLUMNS        DATA  TYPE    FIELD        DEFINITION
         1 -  6        Record name   "ATOM  "
         7 - 11        Integer       serial       Atom  serial number.
        13 - 16        Atom          name         Atom name.
        17             Character     altLoc       Alternate location indicator.
        18 - 20        Residue name  resName      Residue name.
        22             Character     chainID      Chain identifier.
        23 - 26        Integer       resSeq       Residue sequence number.
        27             AChar         iCode        Code for insertion of residues.
        31 - 38        Real(8.3)     x            Orthogonal coordinates for X in Angstroms.
        39 - 46        Real(8.3)     y            Orthogonal coordinates for Y in Angstroms.
        47 - 54        Real(8.3)     z            Orthogonal coordinates for Z in Angstroms.
        55 - 60        Real(6.2)     occupancy    Occupancy.
        61 - 66        Real(6.2)     tempFactor   Temperature  factor.
        77 - 78        LString(2)    element      Element symbol, right-justified.
        79 - 80        LString(2)    charge       Charge  on the atom.
        ```
* __pdb_remark__ is a __list__ of remark lines
  pdb_remark has the folloeing attributes:
	- remark_number

## How to clean hydrogen atoms
TODO
## Handling atloc
TODO
## Clearing gaps in amino acids as shown in post 465
TODO
## Cleaning gaps of amino acids according to sequences
TODO
## Clearing gaps of atoms as shown in post 470
TODO
## Issuing the final report
TODO
