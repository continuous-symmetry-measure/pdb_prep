from Chemistry.PDB.pdb_atom import pdb_atom
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
* pdb_residue *is not* being used in the pdb object (use int in chain_utils)
* use chain_utils to preform operations on a given pdb_chain objects

"""


class pdb_chain(list):
    """
    pdb_chain is a list of pdb_atoms objects
    it has chain_id attribute
    """

    @classmethod
    def from_pdb_atoms_lines(cls, pdb_atoms_lines, ter_line=None):
        pdb_atoms = []
        for i, line in enumerate(pdb_atoms_lines):
            pdb_atoms.append(pdb_atom(line))

        return cls(pdb_atoms, ter_line)

    def __init__(self, pdb_atoms, ter_line=None):
        self.pdb_const_str = pdb_constants()
        self.chain_id = pdb_atoms[0].chain_id
        for i, pdbatom in enumerate(pdb_atoms):
            if not self.chain_id == pdbatom.chain_id:
                raise ValueError("expecting chain_id:'{}', but I got:'{}' in atom:'{}'".
                                 format(self.chain_id, pdbatom.chain_id, pdbatom.pdb_line))
            self.append(pdbatom)
        self.ter_line = ter_line

    def __str__(self):
        chain_str = "\n".join(map(str, self))
        if self.ter_line:
            chain_str += "\n" + self.ter_line
        return chain_str

    def get_number_of_atoms(self):
        return len(self)

    @classmethod
    def create_ter_line(cls, last_atom_line):
        """
        this method will create TER line according to the last atom of the chain
                COLUMNS        DATA  TYPE    FIELD           DEFINITION
        -------------------------------------------------------------------------
         1 -  6        Record name   "TER   "
         7 - 11        Integer       serial          Serial number.
        18 - 20        Residue name  resName         Residue name.
        22             Character     chainID         Chain identifier.
        23 - 26        Integer       resSeq          Residue sequence number.
        27             AChar         iCode           Insertion code.
        :param last_atom_line:
        :return:
        """
        atom = pdb_atom(last_atom_line)
        #      v    v        v
        # 12345678901234567890123456
        # TER      25      GLY     3
        #                           12345678901234567890123456
        # ATOM     24  HA3 GLY     3
        ter_serial_number = int(atom.atom_serial_number) + 1
        # TER    2100      ALA A 775

        st = "{:<5}{:>6}      {:>3} {:>1}{:>4}{:>1}"
        ter_line = st.format('TER', ter_serial_number, atom.resname, atom.chain_id,
                             atom.resseq, atom.icode)
        return ter_line


class pdb_residue(list):
    """
    pdb_residue is *not* part of the pdb object
    This class represent a residue (single amino acid)
    the pdb_residue is a list of atoms which has the following attributes:
    resname,resseq,icode
    """

    def __init__(self, residue_atoms):
        self.atoms = residue_atoms
        reslst_names = list(map(lambda a: a.resname, residue_atoms))
        reslst_seqs = list(map(lambda a: a.resseq, residue_atoms))
        if len(set(reslst_names)) > 1:
            raise ValueError("resname differ - Not a residue: {} ressec={}".format(set(reslst_names), set(reslst_seqs)))
        if len(set(reslst_seqs)) > 1:
            raise ValueError("resseq differ - Not a residue: {}".format(set(reslst_seqs)))

        self.resname = residue_atoms[0].resname
        self.resseq = int(residue_atoms[0].resseq)
        self.icode = residue_atoms[0].icode
        self.extend(residue_atoms)

    def short_str(self):
        return "{} {} {}".format(self.resname, self.resseq, self.icode)

    def __str__(self):
        chain_str = "\n".join(map(str, self))
        return "{}->\n{}".format(self.resname, self.resseq, chain_str)

    @classmethod
    def is_eqvivalent_residues(self, residue1, residue2):
        """
        the residues are eqvivalent if bothe have the same resname and resseq
        :param residue1:
        :param residue2:
        :return:
        """
        ret_val = residue1.resname == residue2.resname and \
                  residue1.resseq == residue2.resseq
        return ret_val


# noinspection PyGlobalUndefined
class chain_utils:
    """
    the chain utils is a clas which will help TODO
    """
    def __init__(self, chain):
        self.chain = chain
        self.atoms_gaps = self.get_atoms_gaps()
        self.residues_gaps = []
        self.residues = []

    def chain2residues_list(self):
        """
        expexted_number_of_residues: the expexted_number_of_residues
                                      (if we know it from othe chins in the model)
        :return: list of lists of atoms - the internal lists are residues (aminos)
        """
        chain = self.chain
        if len(chain) < 1:
            return []
        if len(self.residues) != 0:
            return self.residues  # this method alredy ran

        first_atom = chain[0]
        curr_residue = []
        for i, curr_atom in enumerate(chain):
            if first_atom.has_the_same_residue_as(curr_atom):
                curr_residue.append(curr_atom)
            else:
                self.residues.append(pdb_residue(curr_residue))
                curr_residue = [curr_atom]
                first_atom = curr_atom

        self.residues.append(pdb_residue(curr_residue))
        return self.residues

    def get_residues_gaps(self, expexted_number_of_residues=None):
        residues = self.chain2residues_list()
        if expexted_number_of_residues is None:
            expexted_number_of_residues = residues[-1].resseq
        get_resseq = lambda r: r.resseq
        resseqs = list(map(get_resseq, residues))
        expexted_resseq_list = list(range(1, expexted_number_of_residues + 1))
        resseqs_gaps = sorted(list(set(expexted_resseq_list) - set(resseqs)))
        return resseqs_gaps

    def get_atoms_gaps(self):
        """TODO"""
        return []

    # def get_chain_gaps(self, expexted_number_of_residues=None):
    #     """TODO"""
    #     chain = self.chain
    #     self.residues_gaps = self.get_residues_gaps()

    def remove_residues_by_resseqs(self, resseqs_list):
        """remove residues  of the chain acoording to resseqs list"""
        not_with_resseq = lambda a: a.resseq not in list(map(str, resseqs_list))
        chain = pdb_chain(list(filter(not_with_resseq, self.chain)))
        chain.ter_line = self.chain.ter_line
        return chain

    def remove_atoms_by_atom_resseq_and_name(self, atoms_to_remove):
        """

        :param atoms_to_remove: [(resname,resseq,atom_name), (resname,resseq,atom_name)...]
        :return:
        """
        global _chain
        atoms_indexes_to_delete = []
        chain = self.chain
        for ai, atom in enumerate(chain):

            if (atom.resname, atom.resseq, atom.atom_name) in atoms_to_remove:
                # print  ("{:>22} will be deleted from chain {}".format(
                #     str((atom.resname,atom.resseq,atom.atom_name)),self.chain.chain_id))
                atoms_indexes_to_delete.append(ai)
                # else:
                # print("{:>22} not missing chain {}".format(
                #     str((atom.resname, atom.resseq, atom.atom_name)),self.chain.chain_id))
            atoms = [atom for ai, atom in enumerate(chain) if ai not in atoms_indexes_to_delete]
            _chain = pdb_chain(atoms, ter_line=pdb_chain.create_ter_line(str(atoms[-1])))
        return _chain

    def fix_atoms_serial_number(self, start=1):
        """fix_atoms_serial_number TODO _Tests"""
        index = start
        for i, stom in enumerate(self.chain):
            self.chain[i].atom_serial_number = index
            index += 1
