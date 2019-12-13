import decimal
import json
import re
import sys

from Chemistry.PDB.pdb_chain import chain_utils


def get_experimental_method(file_name):
    with open(file_name) as f:
        exp_methods = ('X-RAY DIFFRACTION', 'FIBER DIFFRACTION',
                       'NEUTRON DIFFRACTION', 'ELECTRON CRYSTALLOGRAPHY', 'ELECTRON MICROSCOPY',
                       'SOLID-STATE NMR', 'SOLUTION NMR', 'SOLUTION SCATTERING')
        line = f.readline()
        while line:
            if line.startswith('EXPDTA'):
                for exp in exp_methods:
                    if exp in line:
                        return exp
            line = f.readline()
    return 'UNKNOWN_EXPERIMENTAL_METHOD'

class pdb_info():
    """
     general information from the pdb object:
        file_name
	    number_fo_models
	    number_fo_remarks
            for each model - models_info:
                model_number
                number_of_chains
                atoms_per_chain (list of numbers)

    """

    def __init__(self, pdb, ignore_remarks=[],output_type='text'):
        self._pdb = pdb
        self.ignore_remarks = ignore_remarks
        self.output_type=output_type
        # self.models_table_data=[]
        self.R_value_list = []
        self.R_free_list = []
        self.R_free_grade = 'NULL'
        self.B_value = 'NULL'
        self.R_free = 'NULL'
        self.R_value = 'NULL'
        self.Resolution = None
        self.Resolution_Grade = None
        self.bio_struct_identical_to_the_asymmetric_unit = None
        self._is_nmr = None
        str_FREE_R = r"^FREE R VALUE(\s+|\s+\(.+\)\s+):\s*(\d+\.\d+|NULL)"
        str_R_value = r"R VALUE\s+\(.+\)\s+:\s*(\d+\.\d+|NULL)"
        str_B_factor = r"MEAN B VALUE\s+\(.+:\s+([-+]?\d*\.\d+|NULL)"

        self.pattern_FREE_R = re.compile(str_FREE_R)
        self.pattern_R_value = re.compile(str_R_value)
        self.pattern_B_factor = re.compile(str_B_factor)
        self.missing_atoms = []
        self.missing_residues = []
        self.ranges = {
            (sys.float_info.min, 1.6): "EXCELLENT",
            (1.6, 1.8): "EXCELLENT/VERY GOOD",
            (1.8, 2.0): "VERY GOOD",
            (2.0, 2.3): "VERY GOOD/GOOD",
            (2.3, 2.6): "GOOD",
            (2.6, 2.9): "GOOD/FAIR",
            (2.9, 3.2): "FAIR",
            (3.2, 3.5): "FAIR/POOR",
            (3.5, sys.float_info.max): "POOR",
        }
        self.r_free_dict = {
            # Resolution : (GoodQ	Median	BadQ),
            '1.0': ('0.135', '0.150', '0.165'),
            '1.1': ('0.145', '0.162', '0.185'),
            '1.2': ('0.155', '0.175', '0.195'),
            '1.3': ('0.162', '0.185', '0.210'),
            '1.4': ('0.185', '0.200', '0.220'),
            '1.5': ('0.190', '0.210', '0.228'),
            '1.6': ('0.195', '0.215', '0.232'),
            '1.7': ('0.200', '0.220', '0.235'),
            '1.8': ('0.210', '0.228', '0.245'),
            '1.9': ('0.215', '0.232', '0.250'),
            '2.0': ('0.220', '0.240', '0.260'),
            '2.1': ('0.228', '0.245', '0.263'),
            '2.2': ('0.232', '0.250', '0.266'),
            '2.3': ('0.238', '0.254', '0.272'),
            '2.4': ('0.242', '0.258', '0.275'),
            '2.5': ('0.245', '0.265', '0.280'),
            '2.6': ('0.248', '0.268', '0.285'),
            '2.7': ('0.250', '0.270', '0.290'),
            '2.8': ('0.255', '0.273', '0.293'),
            '2.9': ('0.257', '0.276', '0.295'),
            '3.0': ('0.260', '0.280', '0.297'),
            '3.1': ('0.265', '0.285', '0.308'),
            '3.2': ('0.268', '0.290', '0.310'),
            '3.3': ('0.270', '0.295', '0.315'),
            '3.4': ('0.273', '0.300', '0.320'),
            '3.5': ('0.275', '0.305', '0.330'),
            '4.0': ('0.280', '0.310', '0.350'),
        }

    def _calc_resolution_grade(self, resolution):
        resolution = float(resolution)

        for k in self.ranges:
            rs_min, rs_max = k
            if rs_min <= float(resolution) < rs_max:
                return self.ranges[k]

    def _round(self, string_of_number, n='0.1'):
        """
        Rounded the input number (resolution) to n_th digit decimal. (here 0.1)
            deal_round("1.46", 0.1)=>
            deal_round("1.45", 0.1)=>
            deal_round("1.44", 0.1)=>
        :param string_of_number:
        :param n:
        :return: float
        """

        # VERY IMPORTANT!
        # Here number is a string. It is better to use string type of number!
        # For example, Decimal instance is created from the string '1.45',
        # and is converted straight to base-10.
        dec_val = decimal.Decimal(str(string_of_number))  #### here, number is string type
        str_acc = str(n)  #### n = 0.1 or 0.01 or 0.001. Here, n = 0.1
        dec_num = decimal.Decimal(dec_val.quantize(decimal.Decimal(str_acc), rounding=decimal.ROUND_HALF_UP))
        return float(dec_num)

    def _calc_r_free_grade(self):
        """
                            Free R Value	Grade
                            <= (GoodQ - 0.02)	                                MUCH BETTER THAN AVERAGE at this res
        GoodQ (best 25%)    > (GoodQ - 0.02)       and <= ((GoodQ + Median)/2)  BETTER THAN AVERAGE at this resolution
        Median              > ((GoodQ + Median)/2) and <= ((Median + BadQ)/2)	AVERAGE at this resolution
        BadQ (worst 25%)    > ((Median + BadQ)/2)  and <= (BadQ + 0.02)	        WORSE THAN AVERAGE at this resolution
                            > (BadQ + 0.02)                                     UNRELIABLE
        """
        if self.R_free.upper() == "NULL":
            return "NULL"
        r_free = float(self.R_free)

        if 1.0 <= float(self.Resolution) <= 3.5:
            resolution_key = str("{:1.1f}".format(self._round(self.Resolution, 0.1)))
            tpl = self.r_free_dict[resolution_key]
            GoodQ, Median, BadQ = float(tpl[0]), float(tpl[1]), float(tpl[2])

            if r_free <= (GoodQ - 0.02):
                return r_free_grade_vlaues("MUCH BETTER THAN AVERAGE at this resolution")

            if (GoodQ - 0.02) < r_free <= ((GoodQ + Median) / 2):
                return r_free_grade_vlaues("BETTER THAN AVERAGE at this resolution")

            if ((GoodQ + Median) / 2) < r_free <= ((Median + BadQ) / 2):
                return r_free_grade_vlaues("AVERAGE at this resolution")

            if ((Median + BadQ) / 2) < r_free <= (BadQ + 0.02):
                return r_free_grade_vlaues("WORSE THAN AVERAGE at this resolution")

            if (BadQ + 0.02) < r_free:
                return r_free_grade_vlaues("UNRELIABLE")

        else:
            msg = "pdb file: {}  r_free error  R_free={};  could not {}"
            raise ValueError(msg.format(self._pdb.file_name, self._calc_r_free_grade.__name__))

    def _check_remark_exists(self, remark_number, caller):
        if remark_number not in self._pdb.remarks:
            msg = "pdb file: {} missing remark {} - could not {}"
            raise ValueError(msg.format(self._pdb.file_name, remark_number, caller))

    def parse_remark_2(self):
        """
        REMARK   2
        REMARK   2 RESOLUTION.    2.30 ANGSTROMS.
        :return:
        """
        self._check_remark_exists(2, self.parse_remark_2.__name__)
        _pdb = self._pdb

        remarak_2 = _pdb.remarks[2]
        for line in filter(lambda s: s.startswith("RESOLUTION."), remarak_2):
            try:
                resln = re.search(r'[-+]?\d*\.\d+', line).group()
                resln_grade = self._calc_resolution_grade(resln)
                self.Resolution = resln
                self.Resolution_Grade = resln_grade
                return
            except:
                pass
        msg = "pdb file: {} missing RESOLUTION info on remark 2 - could not {}"
        raise ValueError(msg.format(_pdb.file_name, self.parse_remark_2.__name__))

    def parse_remark_3(self):
        """
        REMARK   3
        REMARK   3 REFINEMENT.
        REMARK   3   PROGRAM     : PROLSQ
        REMARK   3   AUTHORS     : KONNERT,HENDRICKSON
        REMARK   3
        REMARK   3  DATA USED IN REFINEMENT.
        REMARK   3   RESOLUTION RANGE HIGH (ANGSTROMS) : 2.30
        REMARK   3   RESOLUTION RANGE LOW  (ANGSTROMS) : 6.00
        REMARK   3   DATA CUTOFF            (SIGMA(F)) : NULL
        REMARK   3   COMPLETENESS FOR RANGE        (%) : NULL
        REMARK   3   NUMBER OF REFLECTIONS             : 41617
        REMARK   3
        REMARK   3  FIT TO DATA USED IN REFINEMENT.
        REMARK   3   CROSS-VALIDATION METHOD          : NULL
        REMARK   3   FREE R VALUE TEST SET SELECTION  : NULL
        REMARK   3   R VALUE     (WORKING + TEST SET) : 0.147
        REMARK   3   R VALUE            (WORKING SET) : NULL
        REMARK   3   FREE R VALUE                     : NULL
        REMARK   3   FREE R VALUE TEST SET SIZE   (%) : NULL
        REMARK   3   FREE R VALUE TEST SET COUNT      : NULL
        REMARK   3
        REMARK   3  FIT/AGREEMENT OF MODEL WITH ALL DATA.
        REMARK   3   R VALUE   (WORKING + TEST SET, NO CUTOFF) : NULL
        REMARK   3   R VALUE          (WORKING SET, NO CUTOFF) : NULL
        REMARK   3   FREE R VALUE                  (NO CUTOFF) : NULL
        REMARK   3   FREE R VALUE TEST SET SIZE (%, NO CUTOFF) : NULL
        REMARK   3   FREE R VALUE TEST SET COUNT   (NO CUTOFF) : NULL
        REMARK   3   TOTAL NUMBER OF REFLECTIONS   (NO CUTOFF) : NULL
        REMARK   3
        REMARK   3  NUMBER OF NON-HYDROGEN ATOMS USED IN REFINEMENT.
        REMARK   3   PROTEIN ATOMS            : 6054
        REMARK   3   NUCLEIC ACID ATOMS       : 0
        REMARK   3   HETEROGEN ATOMS          : 26
        REMARK   3   SOLVENT ATOMS            : 538
        REMARK   3
        REMARK   3  B VALUES.
        REMARK   3   FROM WILSON PLOT           (A**2) : NULL
        REMARK   3   MEAN B VALUE      (OVERALL, A**2) : NULL
        REMARK   3   OVERALL ANISOTROPIC B VALUE.
        REMARK   3    B11 (A**2) : NULL
        REMARK   3    B22 (A**2) : NULL
        REMARK   3    B33 (A**2) : NULL
        REMARK   3    B12 (A**2) : NULL
        REMARK   3    B13 (A**2) : NULL
        REMARK   3    B23 (A**2) : NULL
        REMARK   3
        REMARK   3  ESTIMATED COORDINATE ERROR.
        REMARK   3   ESD FROM LUZZATI PLOT        (A) : NULL
        REMARK   3   ESD FROM SIGMAA              (A) : NULL
        REMARK   3   LOW RESOLUTION CUTOFF        (A) : NULL
        REMARK   3
        REMARK   3  RMS DEVIATIONS FROM IDEAL VALUES.
        REMARK   3   DISTANCE RESTRAINTS.                    RMS    SIGMA
        REMARK   3    BOND LENGTH                     (A) : 0.020 ; 0.025
        REMARK   3    ANGLE DISTANCE                  (A) : 0.046 ; 0.040
        REMARK   3    INTRAPLANAR 1-4 DISTANCE        (A) : 0.053 ; 0.050
        REMARK   3    H-BOND OR METAL COORDINATION    (A) : NULL  ; NULL
        REMARK   3
        REMARK   3   PLANE RESTRAINT                  (A) : 0.015 ; 0.020
        REMARK   3   CHIRAL-CENTER RESTRAINT       (A**3) : 0.150 ; 0.150
        REMARK   3
        REMARK   3   NON-BONDED CONTACT RESTRAINTS.
        REMARK   3    SINGLE TORSION                  (A) : 0.160 ; 0.200
        REMARK   3    MULTIPLE TORSION                (A) : 0.220 ; 0.200
        REMARK   3    H-BOND (X...Y)                  (A) : NULL  ; NULL
        REMARK   3    H-BOND (X-H...Y)                (A) : NULL  ; NULL
        REMARK   3
        REMARK   3   CONFORMATIONAL TORSION ANGLE RESTRAINTS.
        REMARK   3    SPECIFIED                 (DEGREES) : NULL  ; NULL
        REMARK   3    PLANAR                    (DEGREES) : NULL  ; NULL
        REMARK   3    STAGGERED                 (DEGREES) : 15.700; 15.000
        REMARK   3    TRANSVERSE                (DEGREES) : NULL  ; NULL
        REMARK   3
        REMARK   3  ISOTROPIC THERMAL FACTOR RESTRAINTS.    RMS    SIGMA
        REMARK   3   MAIN-CHAIN BOND               (A**2) : 0.910 ; 1.500
        REMARK   3   MAIN-CHAIN ANGLE              (A**2) : 1.460 ; 2.000
        REMARK   3   SIDE-CHAIN BOND               (A**2) : 1.950 ; 2.000
        REMARK   3   SIDE-CHAIN ANGLE              (A**2) : 2.980 ; 3.000
        REMARK   3
        REMARK   3  OTHER REFINEMENT REMARKS:
        REMARK   3  THE CD-NE-CZ ANGLE OF ARG A 158 DEVIATES SIGNIFICANTLY FROM
        REMARK   3  THE EXPECTED VALUE AND IS LIKELY TO BE INCORRECT.
        :return:
        """
        self._check_remark_exists(3, self.parse_remark_3.__name__)
        _pdb = self._pdb

        remarak_3 = _pdb.remarks[3]
        is_rb_line = lambda s: 'FREE R VALUE' in s or 'R VALUE' in s or 'MEAN B VALUE' in s
        for line in filter(is_rb_line, remarak_3):
            self._get_b_value(line)
            self._get_r_free(line)
            self._get_r_value(line)

        self.R_value = min(self.R_value_list)
        self.R_free = self.R_free_list[0]
        # self.R_free = min(self.R_free_list)
        self.R_free_grade = self._calc_r_free_grade()

    def parse_remark_210(self):
        """
        REMARK 210
        REMARK 210 EXPERIMENTAL DETAILS
        REMARK 210  EXPERIMENT TYPE                : NMR
        REMARK 210  TEMPERATURE           (KELVIN) : 30; 30
        REMARK 210  PH                             : 7.5; 7.5
        REMARK 210  IONIC STRENGTH                 : ~0.1; ~0.1
        REMARK 210  PRESSURE                       : AMBIENT; AMBIENT
        REMARK 210  SAMPLE CONTENTS                : 0.75 MM [U-99% 13C; U-99% 15N]
        REMARK 210                                   INFLUENZA M2 V27A MUTANT-1, 95%
        REMARK 210                                   H2O/5% D2O; 0.70 MM [U-100% 13C;
        REMARK 210                                   U-100% 15N; U-80% 2H] INFLUENZA
        REMARK 210                                   M2 V27A MUTANT-2, 95% H2O/5% D2O
        REMARK 210
        REMARK 210  NMR EXPERIMENTS CONDUCTED      : 2D 1H-15N TROSY; 3D TROSY HNCO;
        REMARK 210                                   3D TROSY HNCA; 3D TROSY HN(CO)CA;
        REMARK 210                                   3D TROSY HNCACB; 3D 1H-15N NOESY
        REMARK 210                                   TROSY; 3D 1H-13C NOESY TROSY; 2D
        REMARK 210                                   1H-13C HSQC
        REMARK 210  SPECTROMETER FIELD STRENGTH    : 600 MHZ
        REMARK 210  SPECTROMETER MODEL             : AVANCE
        REMARK 210  SPECTROMETER MANUFACTURER      : BRUKER
        REMARK 210
        REMARK 210  STRUCTURE DETERMINATION.
        REMARK 210   SOFTWARE USED                 : X-PLOR_NIH 2.24
        REMARK 210   METHOD USED                   : SIMULATED ANNEALING, MOLECULAR
        REMARK 210                                   DYNAMICS
        REMARK 210
        REMARK 210 CONFORMERS, NUMBER CALCULATED   : 75
        REMARK 210 CONFORMERS, NUMBER SUBMITTED    : 15
        REMARK 210 CONFORMERS, SELECTION CRITERIA  : STRUCTURES WITH THE LOWEST ENERGY
        REMARK 210
        REMARK 210 BEST REPRESENTATIVE CONFORMER IN THIS ENSEMBLE : 1
        REMARK 210
        REMARK 210 REMARK: NULL

        """
        self._check_remark_exists(210, self.parse_remark_210.__name__)
        _pdb = self._pdb

        remarak_210 = _pdb.remarks[210]
        if len(list(filter(lambda s: s.startswith("NMR."), remarak_210))) > 0:
            self._is_nmr = True

    def parse_remark_350(self):
        """
        REMARK 350
        REMARK 350 COORDINATES FOR A COMPLETE MULTIMER REPRESENTING THE KNOWN
        REMARK 350 BIOLOGICALLY SIGNIFICANT OLIGOMERIZATION STATE OF THE
        REMARK 350 MOLECULE CAN BE GENERATED BY APPLYING BIOMT TRANSFORMATIONS
        REMARK 350 GIVEN BELOW.  BOTH NON-CRYSTALLOGRAPHIC AND
        REMARK 350 CRYSTALLOGRAPHIC OPERATIONS ARE GIVEN.
        REMARK 350
        REMARK 350 BIOMOLECULE: 1
        REMARK 350 AUTHOR DETERMINED BIOLOGICAL UNIT: TRIMERIC
        REMARK 350 SOFTWARE DETERMINED QUATERNARY STRUCTURE: TRIMERIC
        REMARK 350 SOFTWARE USED: PISA
        REMARK 350 TOTAL BURIED SURFACE AREA: 10090 ANGSTROM**2
        REMARK 350 SURFACE AREA OF THE COMPLEX: 29300 ANGSTROM**2
        REMARK 350 CHANGE IN SOLVENT FREE ENERGY: -81.0 KCAL/MOL
        REMARK 350 APPLY THE FOLLOWING TO CHAINS: A, B, C
        REMARK 350 BIOMT1   1  1.000000  0.000000  0.000000        0.00000
        REMARK 350 BIOMT2   1  0.000000  1.000000  0.000000        0.00000
        REMARK 350 BIOMT3   1  0.000000  0.000000  1.000000        0.00000
        REMARK 350
        REMARK 350 BIOMOLECULE: 2
        REMARK 350 SOFTWARE DETERMINED QUATERNARY STRUCTURE: HEXAMERIC
        REMARK 350 SOFTWARE USED: PISA
        REMARK 350 TOTAL BURIED SURFACE AREA: 26200 ANGSTROM**2
        REMARK 350 SURFACE AREA OF THE COMPLEX: 52360 ANGSTROM**2
        REMARK 350 CHANGE IN SOLVENT FREE ENERGY: -155.0 KCAL/MOL
        REMARK 350 APPLY THE FOLLOWING TO CHAINS: A, B, C
        REMARK 350 BIOMT1   1  1.000000  0.000000  0.000000        0.00000
        REMARK 350 BIOMT2   1  0.000000  1.000000  0.000000        0.00000
        REMARK 350 BIOMT3   1  0.000000  0.000000  1.000000        0.00000
        REMARK 350 BIOMT1   2 -1.000000  0.000000  0.000000        0.00000
        REMARK 350 BIOMT2   2  0.000000  1.000000  0.000000        0.00000
        REMARK 350 BIOMT3   2  0.000000  0.000000 -1.000000        0.00000

        """
        try:
            self._check_remark_exists(350, self.parse_remark_350.__name__)
        except ValueError as e:
            print("pdb file: {} -remark 350 is missing, undefined  biomolecule".format(self._pdb.file_name))
        _pdb = self._pdb
        remarak_350 = _pdb.remarks[350]
        is_boilogical_struct_defined = False
        for i, line in enumerate(remarak_350):
            if line.startswith('BIOMOLECULE'):
                i = i + 1
                is_boilogical_struct_defined = True
                continue
            if is_boilogical_struct_defined and line.startswith('APPLY THE FOLLOWING TO CHAINS'):
                break

                # BIOMT1   1  1.000000  0.000000  0.000000        0.00000
                # BIOMT2   1  0.000000  1.000000  0.000000        0.00000
                # BIOMT3   1  0.000000  0.000000  1.000000        0.00000
        biomt_lines = [
            'BIOMT1   1  1.000000  0.000000  0.000000        0.00000',
            'BIOMT2   1  0.000000  1.000000  0.000000        0.00000',
            'BIOMT3   1  0.000000  0.000000  1.000000        0.00000'
        ]
        i += 1
        is_last_index = lambda i: len(remarak_350) - 1 == i
        is_identity_matrix = lambda m: biomt_lines[0] == m[0] and biomt_lines[1] == m[1] and biomt_lines[2] == m[2]
        # will set to tru only if the lines are identity_matrix:
        #     we have only 3 BIOMT lines with  identity_matrix of 3X3
        #     the third line of thm identity_matrix: is the last or
        #      the forth line is not BIOMT line
        if is_identity_matrix(remarak_350[i:i + 3]) and is_last_index(i + 2):
            self.bio_struct_identical_to_the_asymmetric_unit = True
        elif is_identity_matrix(remarak_350[i:i + 3]) and not remarak_350[i + 3].startswith('BIOMT'):
            self.bio_struct_identical_to_the_asymmetric_unit = True
        else:
            self.bio_struct_identical_to_the_asymmetric_unit = False

    def parse_remark_465(self):
        """
        REMARK 465 MISSING RESIDUES
        REMARK 465 THE FOLLOWING RESIDUES WERE NOT LOCATED IN THE
        REMARK 465 EXPERIMENT. (M=MODEL NUMBER; RES=RESIDUE NAME; C=CHAIN
        REMARK 465 IDENTIFIER; SSSEQ=SEQUENCE NUMBER; I=INSERTION CODE.)
        REMARK 465
        REMARK 465   M RES C SSSEQI
        REMARK 465     GLN B   412
        :return:
        """
        global i
        self._check_remark_exists(465, self.parse_remark_465.__name__)
        _pdb = self._pdb
        remarak_465 = _pdb.remarks[465]
        for i, line in enumerate(remarak_465):
            if line == 'M RES C SSSEQI':
                i = i + 1
                break
        for line in remarak_465[i:]:
            resname, chian_id, resseq = line.split()
            self.missing_residues.append(
                {
                    "resname": resname.strip(),
                    "chain_id": chian_id.strip(),
                    "resseq": resseq.strip(),
                })

    def parse_remark_470(self):
        """
        REMARK 470 MISSING ATOM
        REMARK 470 THE FOLLOWING RESIDUES HAVE MISSING ATOMS (M=MODEL NUMBER;
        REMARK 470 RES=RESIDUE NAME; C=CHAIN IDENTIFIER; SSEQ=SEQUENCE NUMBER;
        REMARK 470 I=INSERTION CODE):
        REMARK 470   M RES CSSEQI  ATOMS
        REMARK 470     LYS A  22    CE   NZ
        REMARK 470     LYS A  65    CD   CE   NZ
        REMARK 470     GLU A 167    CG   CD   OE1  OE2
        REMARK 470     LEU A 231    CG   CD1  CD2
        REMARK 470     SER B   2    OG
        REMARK 470     LYS B  22    CE   NZ
        REMARK 470     LEU B  64    CG   CD1  CD2
        REMARK 470     GLU B 228    CG   CD   OE1  OE2
        REMARK 470     LYS C  22    CE   NZ
        REMARK 470     LYS C  65    CG   CD   CE   NZ
        REMARK 470     GLU C  71    CG   CD   OE1  OE2
        """
        global i
        self._check_remark_exists(470, self.parse_remark_470.__name__)
        _pdb = self._pdb
        remarak_470 = _pdb.remarks[470]
        for i, line in enumerate(remarak_470):
            if line == 'M RES CSSEQI  ATOMS':
                i = i + 1
                break
        for line in remarak_470[i:]:
            tmp = line.split()
            resname, chian_id, resseq = tmp[0:3]
            atom_names = tmp[3:]
            self.missing_atoms.append(
                {
                    "resname": resname.strip(),
                    "chain_id": chian_id.strip(),
                    "resseq": resseq.strip(),
                    "atom_names": atom_names
                })

    def _get_b_value(self, remark_3_line):
        # extracting the average B value
        match_B_val = re.search(self.pattern_B_factor, remark_3_line)
        if match_B_val:
            self.B_value = match_B_val.group(1)

    def _get_r_free(self, remark_3_line):
        # extracting the R_free value
        match_R_free = re.search(self.pattern_FREE_R, remark_3_line)
        if match_R_free:
            value = match_R_free.group(2)
            self.R_free_list.append(value)

    def _get_r_value(self, remark_3_line):
        # extracting the R_value_Working_set
        match_R_work = re.search(self.pattern_R_value, remark_3_line)
        if match_R_work:
            value = match_R_work.group(1)
            self.R_value_list.append(value)

    def is_nmr(self):
        if self._is_nmr is not None:
            return self._is_nmr
        _pdb = self._pdb
        strp_ends = lambda s, e: s.strip().endswith(e)
        extdta_nmr = lambda s: strp_ends(s, 'NMR')
        remark_2_nmr = lambda s: strp_ends(s, 'RESOLUTION. NOT APPLICABLE')
        if len(list(filter(extdta_nmr, _pdb.extdta))) > 0:
            return True
        # REMARK   2 RESOLUTION. NOT APPLICABLE
        elif 2 in _pdb.remarks and len(list(filter(remark_2_nmr, _pdb.remarks[2]))) > 0:
            return True
        return False

    def is_homomer(self, is_verbose=False):
        _pdb = self._pdb
        if len(_pdb.seqres) > 0:
            chaindict = _pdb.get_resseq_as_chaindict()
            to_seq_str = lambda lst: "-".join(lst)
            first_chain_str = to_seq_str(chaindict[min(chaindict)])
            for chain_id, chain in chaindict.items():
                if not to_seq_str(chain) == first_chain_str:
                    if is_verbose:
                        print("--- NOT_HOMOMER:{}\n{}:{}\n{}:{}\n---\n".format(
                            _pdb.file_name, min(chaindict), first_chain_str, chain_id, to_seq_str(chain)))
                    return False
            return True
        else:
            raise ValueError(" missing SEQRES data")

    def gaps_report(self):
        pass

    def info_report(self, models_table_data=[]):
        info = self._pdb.info()
        report = Report(self._pdb, models_table_data)

        rem_header = lambda rn: "\tremark {:>4d}:".format(rn)
        rem_ignore_msg = lambda rn: "\tremark {} will be ignore as you requested".format(rn)

        remark_number = 2
        try:

            if remark_number in self.ignore_remarks:
                raise RuntimeWarning(rem_ignore_msg(remark_number))
            self.parse_remark_2()
            resolution = "Resolution = {}".format(self.Resolution)
            resolution_grade = "Resolution_Grade = {}\n".format(self.Resolution_Grade)
            remark_info = ""
            remark_info += rem_header(remark_number)
            remark_info += "\t\t" + resolution + "\t" + resolution_grade
            report.add_remark_info(remark_number, remark_info)
        except Exception as e:
            remark_info = "\tremark {:>4d}:\tno info :{}".format(remark_number, e)
            report.add_remark_info(remark_number, remark_info)

        remark_number = 3
        try:

            if remark_number in self.ignore_remarks:
                raise RuntimeWarning(rem_ignore_msg(remark_number))
            self.parse_remark_3()
            remark_info = ""
            remark_info += rem_header(remark_number)
            remark_info += "\t\tR_value = {}".format(self.R_value)
            remark_info += "\t\tR_free  = {}".format(self.R_free)
            remark_info += "\t\tR_free_grade = {}".format(self.R_free_grade)
            report.add_remark_info(remark_number, remark_info)
        except Exception as e:
            remark_info = "\tremark {}:\tno info :{}".format(remark_number, e)
            report.add_remark_info(remark_number, remark_info)

        remark_number = 350
        try:

            if remark_number in self.ignore_remarks:
                raise RuntimeWarning(rem_ignore_msg(remark_number))
            self.parse_remark_350()
            remark_info = ""
            remark_info += rem_header(remark_number)
            remark_info += "\t\tbio_struct_identical_to_the_asymmetric_unit = {}".format(
                self.bio_struct_identical_to_the_asymmetric_unit)
            report.add_remark_info(remark_number, remark_info)
        except Exception as e:
            remark_info = "\tremark {}:\tno info :{}".format(remark_number, e)
            report.add_remark_info(remark_number, remark_info)

        if self.output_type=='text': return str(report)
        elif self.output_type == 'json': return report.to_json()
        else: return str(report)

class Report:
    def __init__(self, pdb, models_table_data=[]):
        self._pdb = pdb
        info = self._pdb.info()
        self.info = info
        self.models_table_data=models_table_data
        self._str_order = ["file_name", "number_of_models", "number_fo_remarks", "caveats"]
        self.remarks_info = []


    def add_remark_info(self, remark_number, remark_info):
        self.remarks_info.append({"remark_number": remark_number, "remark_info": remark_info})

    def __str__(self):
        d = self.to_dict()
        report = ""
        report += "file_name: {}\n".format(d["file_name"])
        report += "\tnumber_of_models: {}".format(d["number_of_models"])
        report += "\t\tnumber_of_remarks: {}\n".format(d["number_of_remarks"])
        if "caveats" in d:
            report += "\tcaveats:\n\t"
            report += "\n\t".join(d["caveats"])
        report += "\tremarks_info:\n"
        for ri in d["remarks_info"]:
            report += "\t\t - " + ri["remark_info"] + "\n"
        report += "\tmodels_info:\n"
        for mi in d["models_info"]:
            report += "\t\tmodel_number: {}".format(mi["model_number"])
            report += "\t\tnumber_of_chains: {}\n".format(mi["number_of_chains"])
        for line in self.models_table_data:
            report +="\t  {:>10} {:>10} {:>10} {:>10}\n".format(line[0], line[1], line[2], line[3])
        return report

    def to_dict(self):
        data = {}
        for k in ["file_name", "number_of_models"]:
            data[k] = self.info[k]
        try:
            data["number_of_remarks"] = len(list(self.remarks_info))
        except e as  Exception:
            data["number_of_remarks"] = 0

        data["models_info"] = []
        for mi in self.info["models_info"]:
            data["models_info"].append({
                "model_number": mi["model_number"],
                "number_of_chains": mi["number_of_chains"]
            })

        if self._pdb.has_caveats():
            data["caveats"] = self._pdb.caveats
        data["remarks_info"] = list(sorted(self.remarks_info, key=lambda rem: rem["remark_number"]))
        if len(self.models_table_data)>0:
            data["models_table_data"]=self.models_table_data
        return data

    def to_json(self):
        ret_val = json.dumps(self.to_dict(), sort_keys=True, indent=4)
        return ret_val


class r_free_grade_vlaues():
    def __init__(self, text_value):
        values = r_free_grade_vlaues.get_struct()

        if text_value not in map(lambda v: v['text'], values):
            raise ValueError("not valid value:{}".format(text_value))
        for v in values:
            if v['text'] == text_value:
                self.val = v
                break

    def __str__(self):
        return self.val["text"]

    def _convert(self, other):
        if type(other) is str:
            return r_free_grade_vlaues(other)
        return other

    def __ge__(self, other):
        """ A is better then B"""
        return self.val["value"] <= self._convert(other).val["value"]

    def __le__(self, other):
        """ A is better then B"""
        return self.val["value"] >= self._convert(other).val["value"]

    def __eq__(self, other):
        """ A is better then B"""
        return self.val["value"] == self._convert(other).val["value"]

    @classmethod
    def get_struct(cls):
        return [
            {'text': "MUCH BETTER THAN AVERAGE at this resolution", "value": "A"},
            {'text': "BETTER THAN AVERAGE at this resolution", "value": "B"},
            {'text': "AVERAGE at this resolution", "value": "C"},
            {'text': "WORSE THAN AVERAGE at this resolution", "value": "D"},
            {'text': "UNRELIABLE", "value": "E"},
        ]

    @classmethod
    def for_help_msg(cls):
        lst = cls.get_struct()
        values = []
        s = ""
        for x in sorted(lst, key=lambda d: d["value"]):
            values.append(x["value"])
            s += "\t\t{} - {}\n".format(x["value"], x["text"])
        return s, values

    @classmethod
    def from_value(cls, value):
        lst = cls.get_struct()
        for x in sorted(lst, key=lambda d: d["value"]):
            if x["value"] == value:
                return cls(x["text"])


class pdb_utils():
    @classmethod
    def to_json(cls, pdb_object):
        data = {}
        models = []
        for model in pdb_object:
            chains = []
            for chain in model:
                atoms = []
                for atom in chain:
                    atom_data = atom.__dict__
                    for k in ["pdb_const_str", "pdb_line"]:
                        del atom_data[k]
                    atoms.append(atom_data)
                chains.append(atoms)
            models.append(chains)
        data["models"] = models

        return json.dumps(data, separators=(',', ':'))

    @classmethod
    def remove_residues_from_every_chain(cls, missing_residues_per_chain_id, _pdb):
        """
        TODO documentation
        :param missing_residues_per_chain_id:
        :param _pdb:
        :return:
        """
        missing_residues = []
        for chain_id, mis_res_list in missing_residues_per_chain_id.items():
            missing_residues.extend(mis_res_list)

        for mi, model in enumerate(_pdb):
            for ci, chain in enumerate(model):
                chainuils = chain_utils(chain)
                _pdb[mi][ci] = chainuils.remove_residues_by_resseqs(missing_residues)
        return _pdb

    @classmethod
    def remove_atoms_from_every_chain(cls, atoms_to_remove, _pdb):
        """
        TODO documentation
        :param atoms_to_remove: [(resname, resseq,atom_name)]
        :param _pdb:
        :return:
        """
        for mi, model in enumerate(_pdb):
            for ci, chain in enumerate(model):
                chainuils = chain_utils(chain)
                _pdb[mi][ci] = chainuils.remove_atoms_by_atom_resseq_and_name(atoms_to_remove)
        return _pdb

    @classmethod
    def clean_alternate_location(cls, _pdb):
        pdb_new = _pdb
        remove_list = []
        for mi, model in enumerate(_pdb):
            for ci, chain in enumerate(model):
                for ai, atom in enumerate(chain):
                    if atom.altloc is None:
                        continue
                    if len(atom.altloc) == 0:
                        continue
                    if atom.altloc == 'A':
                        pdb_new[mi][ci][ai].altloc = ' '.strip()
                        pdb_line = list(pdb_new[mi][ci][ai].pdb_line)
                        pdb_line[16] = ' '
                        pdb_new[mi][ci][ai].pdb_line = "".join(pdb_line)
                        continue
                    if atom.altloc != 'A':
                        remove_list.append((mi, ci, ai))
                        continue
        for mi, ci, ai in reversed(remove_list):
            del pdb_new[mi][ci][ai]
        return pdb_new
