from Chemistry.PDB.pdb_constants import pdb_constants

"""
* pdb is list of pdb_models
* pdb_model is a list of pdb_chains objects
* pdb _chain is a list of pdb_atom objects
* atom ahs attributes such as:
    - atom_serial_number
    - atom_name
    - resname
    - resseq
    - chain_id
    ...


"""


class pdb_atom():
    """
    pdb atom object
    https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html

    COLUMNS   str     DATA  TYPE    FIELD        DEFINITION
    -------------------------------------------------------------------------------------
     1 -  6    [ 0: 6]    Record name   "ATOM  "
     7 - 11    [ 6:12]    Integer       serial       Atom  serial number.
    13 - 16    [12:16]    Atom          name         Atom name.
    17         [16:16]    Character     altLoc       Alternate location indicator.
    18 - 20    [17:20]    Residue name  resName      Residue name.
    22         [21:21]    Character     chainID      Chain identifier.
    23 - 26    [22:26]    Integer       resSeq       Residue sequence number.
    27         [26:26]    AChar         iCode        Code for insertion of residues.
    31 - 38    [38:46]    Real(8.3)     x            Orthogonal coordinates for X in Angstroms.
    39 - 46    [38:46]    Real(8.3)     y            Orthogonal coordinates for Y in Angstroms.
    47 - 54    [46:54]    Real(8.3)     z            Orthogonal coordinates for Z in Angstroms.
    55 - 60    [54:60]    Real(6.2)     occupancy    Occupancy.
    61 - 66    [60:66]    Real(6.2)     tempFactor   Temperature  factor.
    77 - 78    [76:78]    LString(2)    element      Element symbol, right-justified.
    79 - 80    [78:80]    LString(2)    charge       Charge  on the atom.
    """

    @classmethod
    def parse_record_name(cls, pdb_line):
        return pdb_line[0: 6].strip()  # record name

    @classmethod
    def parse_atom_serial_number(cls, pdb_line):
        return pdb_line[6:12].strip()  # atom serial number

    @classmethod
    def parse_atom_name(cls, pdb_line):
        return pdb_line[12:16] # atom name with type

    @classmethod
    def parse_altloc(cls, pdb_line):
        return pdb_line[16]  # alternate locatin indicator

    @classmethod
    def parse_resname(cls, pdb_line):
        return pdb_line[17:20].strip()  # residue name

    @classmethod
    def parse_chain_id(cls, pdb_line):
        return pdb_line[21]  # chain identifier

    @classmethod
    def parse_resseq(pdb_line):
        return pdb_line[22:26].strip()  # residue sequence number

    @classmethod
    def parse_icode(cls, pdb_line):
        return pdb_line[26]  # insertion code

    @classmethod
    def parse_x(cls, pdb_line):
        return float(pdb_line[30:38].strip())  # coordinates X

    @classmethod
    def parse_y(cls, pdb_line):
        return float(pdb_line[38:46].strip())  # coordinates Y

    @classmethod
    def parse_z(cls, pdb_line):
        return float(pdb_line[46:54].strip())  # coordinates Z

    @classmethod
    def parse_occupancy(cls, pdb_line):
        return float(pdb_line[54:60].strip())  # standard deviation of occupancy

    @classmethod
    def parse_tempfactor(cls, pdb_line):
        return float(pdb_line[60:66].strip())  # standard deviation of temperature

    @classmethod
    def parse_element_symbol(cls, pdb_line):
        return pdb_line[76:78].strip()  # element symbol

    @classmethod
    def parse_charge(cls, pdb_line):
        return pdb_line[78:80].strip()  # charge on the atom

    @classmethod
    def is_backbone(cls, atom_name):
        """
        returns True if atom_name  is a backbone atom of the amini accid (i.e is one of: 'N', 'CA', 'C', 'O')
        :param atom_name:
        :return:
        """
        return atom_name in ['N', 'CA', 'C', 'O']

    def __init__(self, pdb_atom_line):
        """
        parse the pdb_atom_line into the attribu
        :param pdb_atom_line:
        """
        self.pdb_const_str = pdb_constants()
        self.pdb_line = pdb_atom_line.rstrip('\n').rstrip('\r').rstrip('\n')
        pdb_line = self.pdb_line
        try:
            # TODO use class methods here
            self.record_name = pdb_line[0: 6].strip()  # record name
            self.atom_serial_number = pdb_line[6:12].strip()  # atom serial number
            self.atom_name = pdb_line[12:16].strip()  # atom name with type
            self.orig_atom_name = pdb_line[12:16]  # atom name with type nostip for str func
            self.altloc = pdb_line[16].strip()  # alternate locatin indicator
            self.resname = pdb_line[17:20].strip()  # residue name
            self.chain_id = pdb_line[21]  # chain identifier
            self.resseq = pdb_line[22:26].strip()  # residue sequence number
            self.icode = pdb_line[26]  # insertion code
            self.x = float(pdb_atom_line[30:38].strip())  # coordinates X
            self.y = float(pdb_line[38:46].strip())  # coordinates Y
            self.z = float(pdb_line[46:54].strip())  # coordinates Z
            self.occupancy = float(pdb_line[54:60].strip())  # standard deviation of occupancy
            self.tempfactor = float(pdb_line[60:66].strip())  # standard deviation of temperature
            self.element_symbol = pdb_line[76:78].strip()  # element symbol
            self.charge = pdb_line[78:80].strip()  # charge on the atom
        except Exception as e:
            print("line={}".format(pdb_atom_line))
            raise e

    def __str__(self):
        """
        gets the pdb_line back from the attributes
        :return:
        """

        _str = "{:<6}{:>5} {:>4}{:>1}{:>3}{:1}{:>1}{:>4}{:>1}{:<3}" + \
               "{:>8.3f}{:>8.3f}{:>8.3f}{:>6.2f}{:>6.2f}{:>12}{:>2}{:>2}"
        return _str.format(
            self.record_name,
            self.atom_serial_number,
            self.orig_atom_name,
            self.altloc,
            self.resname,
            " ",
            self.chain_id,
            self.resseq,
            self.icode,
            " ",
            self.x,
            self.y,
            self.z,
            self.occupancy,
            self.tempfactor,
            self.element_symbol,
            " ",
            self.charge,
        )
        # return self.pdb_line

    def get_coordinates(self):
        """
        :return: (x, y, z)
        """
        return (self.x, self.y, self.z)

    def has_the_same_residue_as(self, other_atom):
        """
        True ai both has the same resseq and icode and resname
        :param other_atom:
        :return:
        """
        return self.resseq == other_atom.resseq and self.icode == other_atom.icode and self.resname == other_atom.resname


class eqvivalent_atoms():
    """
    this class  helps to  find the eqvivalent atoms iin dimers
    """
    def is_eqvivalent_atoms(self, atom1, atom2):
        ret_val = atom1.atom_name == atom2.atom_name and \
                  atom1.resname == atom2.resname and \
                  atom1.resseq == atom2.resseq
        return ret_val

    def filter_atoms_by_name(self, atom_name, chain):
        return list(filter(lambda atm: atm.atom_name == atom_name, chain))

    def get_pairs_tupels(self, dimer_model, atom_name):

        atoms_from_chain1 = list(self.filter_atoms_by_name(atom_name, dimer_model[0]))
        atoms_from_chain2 = list(self.filter_atoms_by_name(atom_name, dimer_model[1]))
        atoms_pairs = []

        for atom1 in atoms_from_chain1:
            for atom2 in atoms_from_chain2:
                if self.is_eqvivalent_atoms(atom1, atom2):
                    atoms_pairs.append((atom1, atom2))
        return atoms_pairs
