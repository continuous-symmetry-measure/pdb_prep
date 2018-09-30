import difflib

from Chemistry.PDB.pdb_chain import chain_utils


class chains_diff():
    def __init__(self, chain_a, chain_b):
        self.residues_list_a = chain_utils(chain_a).chain2residues_list()
        self.residues_list_b = chain_utils(chain_b).chain2residues_list()
        self.df = None

    def get_resedius_for_diff(self, residues_list):
        return list(map(lambda r: r.resname, residues_list))

    def compare_chains(self):
        lines_a = self.get_resedius_for_diff(self.residues_list_a)
        lines_b = self.get_resedius_for_diff(self.residues_list_b)
        self.df = difflib.unified_diff(lines_a, lines_b, lineterm='')
        return self.df
