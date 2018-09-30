from Chemistry.PDB.pdb_chain import chain_utils


class simple_siever():
    """this is simple_siever"""

    def __init__(self, *args):
        self.args_str = "+".join(list(*args))

    def __str__(self):
        if len(self.args_str) > 0:
            return "{}:{}".format(self.__class__.__name__, self.args_str)
        else:
            return "{}".format(self.__class__.__name__)

    def sieve(self, pdb, fix_atoms_serial_number=False):
        return pdb

    @classmethod
    def from_string(self, siever_str):
        args = siever_str.split("+")
        self.__class__(*args)

    @classmethod
    def help(cls):
        return " {} :\n {}\n".format(cls.__name__, cls.__doc__)


class atom_names_siever(simple_siever):
    """siever atoms by name from PDB"""

    def __init__(self, *args):
        super().__init__(*args)
        self.atom_names = list(args)

    def is_match(self, atom, prefix_name):
        return atom.atom_name.startswith(prefix_name)

    def sieve(self, pdb, fix_atoms_serial_number=False):
        _pdb = pdb
        atoms_to_remove = []
        for mi, model in enumerate(_pdb):
            for ci, chain in enumerate(model):
                for ai, atom in enumerate(chain):
                    for prefix_name in self.atom_names:
                        if self.is_match(atom, prefix_name):
                            atoms_to_remove.append(ai)
                for ai in reversed(atoms_to_remove):
                    del _pdb[mi][ci][ai]
                atoms_to_remove = []
                if fix_atoms_serial_number:
                    chinnutils = chain_utils(chain)
                    chinnutils.fix_atoms_serial_number()
                    _pdb[mi][ci] = chinnutils.chain
        return _pdb


class atom_hydrogen_siever(atom_names_siever):
    """siever atoms by name from PDB"""

    def __init__(self, *args):
        super().__init__('H', *args)
