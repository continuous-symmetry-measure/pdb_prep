import unittest

from Chemistry.PDB.pdb_chain import *


class Test_pdb_chain(unittest.TestCase):
    def setUp(self):
        self.pdb_lines = [
            'ATOM      1  N   MET A   1      23.781  15.112   7.639  1.00 98.81           N  ',
            'ATOM      2  CA  MET A   1      23.583  15.060   6.213  1.00 27.58           C  ',
            'ATOM      3  C   MET A   1      23.626  13.585   5.731  1.00 20.18           C  ',
            'ATOM      4  O   MET A   1      24.375  13.178   4.858  1.00 17.27           O  ',
            'ATOM      5  CB  MET A   1      24.571  16.030   5.545  1.00 19.79           C  ',
            'ATOM      6  N   VAL A   2      22.829  12.797   6.397  1.00 16.57           N  ',
            'ATOM      7  CA  VAL A   2      22.689  11.367   6.191  1.00 11.96           C  ',
            'ATOM      8  C   VAL A   2      22.163  10.806   4.869  1.00  9.16           C  ',
            'ATOM      9  O   VAL A   2      22.738   9.901   4.287  1.00  9.96           O  ',
            'ATOM     10  CB  VAL A   2      22.965  10.406   7.321  1.00 16.09           C  ',
            'ATOM     11  CG1 VAL A   2      23.078  11.158   8.633  1.00 37.18           C  ',
            'ATOM     12  CG2 VAL A   2      21.840   9.409   7.483  1.00 19.39           C  ',
            'ATOM     13  N   SER A   3      21.079  11.386   4.374  1.00 10.83           N  ',
            'ATOM     14  CA  SER A   3      20.501  10.868   3.135  1.00  8.60           C  ',
        ]
        self.ter_line = 'TER      15      SER A   3 '

    # ATOM     24  HA3 GLY     3       7.191   1.300   1.088  1.00  0.00           H
    # TER      25      GLY     3
    # TER      25  GLY

    def test_pdb_chain(self):
        chain = pdb_chain.from_pdb_atoms_lines(self.pdb_lines, self.ter_line)
        self.assertTrue(chain[0].pdb_line == self.pdb_lines[0])
        self.assertTrue(len(chain) == len(self.pdb_lines))

    def test_pdb_chain_no_ter_line(self):
        chain = pdb_chain.from_pdb_atoms_lines(self.pdb_lines, ter_line=None)
        self.assertTrue(chain[0].pdb_line == self.pdb_lines[0])
        self.assertTrue(len(chain) == len(self.pdb_lines))

    def test_pdb_create_ter_line(self):
        ter_line = pdb_chain.create_ter_line(self.pdb_lines[-1])
        self.assertEqual(ter_line, self.ter_line)


class Test_pdb_chain_utils(unittest.TestCase):
    def setUp(self):
        self.pdb_lines = [
            'ATOM      1  N   MET A   1      23.781  15.112   7.639  1.00 98.81           N  ',
            'ATOM      2  CA  MET A   1      23.583  15.060   6.213  1.00 27.58           C  ',
            'ATOM      3  C   MET A   1      23.626  13.585   5.731  1.00 20.18           C  ',
            'ATOM      4  O   MET A   1      24.375  13.178   4.858  1.00 17.27           O  ',
            'ATOM      5  CB  MET A   1      24.571  16.030   5.545  1.00 19.79           C  ',
            'ATOM      6  N   VAL A   2      22.829  12.797   6.397  1.00 16.57           N  ',
            'ATOM      7  CA  VAL A   2      22.689  11.367   6.191  1.00 11.96           C  ',
            'ATOM      8  C   VAL A   2      22.163  10.806   4.869  1.00  9.16           C  ',
            'ATOM      9  O   VAL A   2      22.738   9.901   4.287  1.00  9.96           O  ',
            'ATOM     10  CB  VAL A   2      22.965  10.406   7.321  1.00 16.09           C  ',
            'ATOM     11  CG1 VAL A   2      23.078  11.158   8.633  1.00 37.18           C  ',
            'ATOM     12  CG2 VAL A   2      21.840   9.409   7.483  1.00 19.39           C  ',
            'ATOM     13  N   SER A   3      21.079  11.386   4.374  1.00 10.83           N  ',
            'ATOM     14  CA  SER A   3      20.501  10.868   3.135  1.00  8.60           C  ',
        ]
        self.ter_line = 'TER      15      SER A   3 '
        chain = pdb_chain.from_pdb_atoms_lines(self.pdb_lines, self.ter_line)

    def test_chain2residues_list(self):
        chain = pdb_chain.from_pdb_atoms_lines(self.pdb_lines, self.ter_line)
        chain_util = chain_utils(chain)
        residues = chain_util.chain2residues_list()
        self.assertEqual(len(residues), 3)
        res_names = list(map(lambda r: r.resname, residues))
        self.assertEqual(res_names, ['MET', 'VAL', 'SER'])
        res_seqs = list(map(lambda r: r.resseq, residues))
        self.assertEqual(res_seqs, [1, 2, 3])

    def test_remove_residues(self):
        chain = pdb_chain.from_pdb_atoms_lines(self.pdb_lines, self.ter_line)
        chain_util = chain_utils(chain)
        new_chain = chain_util.remove_residues_by_resseqs([2])
        residues = chain_utils(new_chain).chain2residues_list()
        self.assertEqual(len(residues), 2)
        res_names = list(map(lambda r: r.resname, residues))
        self.assertEqual(res_names, ['MET', 'SER'])
        res_seqs = list(map(lambda r: r.resseq, residues))
        self.assertEqual(res_seqs, [1, 3])
