import unittest

from Chemistry.PDB.pdb_atom import *


class Test_pdb_atom(unittest.TestCase):
    def setUp(self):
        self.pdb_atom_line = 'ATOM    105  CD2ATYR A 405     -54.453  39.711 107.320  0.53 14.50           C'
        self.pdb_atom_line_nl = 'ATOM    105  CD2ATYR A 405     -54.453  39.711 107.320  0.53 14.50           C\n'
        self.pdb_atom_line_nl2 = 'ATOM    105  CD2ATYR A 405     -54.453  39.711 107.320  0.53 14.50           C\n\r'
        self.pdb_atom_with_long_resseq='ATOM  15287  O   LEU B1024      10.643  -8.357 -25.347  1.00 51.11           O'

    def test_pdb_atom(self):
        pdb_line = self.pdb_atom_line
        atom = pdb_atom(pdb_line)
        self.assertEqual(atom.x, -54.453, "_Tests x")
        self.assertEqual(atom.tempfactor, 14.50, "_Tests tempfactor")
        self.assertEqual(str(atom).rstrip(), self.pdb_atom_line.rstrip())

    def test_pdb_atom_nl(self):
        pdb_line = self.pdb_atom_line_nl
        atom = pdb_atom(pdb_line)
        self.assertEqual(atom.x, -54.453, "_Tests x")
        self.assertEqual(atom.tempfactor, 14.50, "_Tests tempfactor")
        self.assertEqual(str(atom).rstrip(), self.pdb_atom_line.rstrip())

    def test_pdb_atom_nl2(self):
        pdb_line = self.pdb_atom_line_nl2
        atom = pdb_atom(pdb_line)
        self.assertEqual(atom.x, -54.453, "_Tests x")
        self.assertEqual(atom.tempfactor, 14.50, "_Tests tempfactor")
        self.assertEqual(str(atom).rstrip(), self.pdb_atom_line.rstrip())

    def test_atom_with_long_resseq(self):
        pdb_line = self.pdb_atom_with_long_resseq
        atom = pdb_atom(pdb_line)
        self.assertEqual(atom.x, 10.643, "_Tests x")
        self.assertEqual(atom.resseq, '1024', "_Tests tempfactor")
        self.assertEqual(str(atom).rstrip(), self.pdb_atom_with_long_resseq.rstrip())

class Test_eqvivalent_atoms(unittest.TestCase):
    def setUp(self):
        self.test_dict = {
            (
                'ATOM     42  OG1 THR A  20      -1.399  42.633 -13.704  1.00 17.85           O  ',
                'ATOM     42  OG1 THR A  20      -1.399  42.633 -13.704  1.00 17.85           O  ',

            ): ('same atom', True),
            (
                'ATOM     42  OG1 THR A  20      -1.399  42.633 -13.704  1.00 17.85           O ',
                'ATOM     42  C   THR A  20      -1.399  42.633 -13.704  1.00 17.85           O  ',

            ): ('diffrent atom_name', False),
            (
                'ATOM     42  OG1 THR A  20      -1.399  42.633 -13.704  1.00 17.85           O  ',
                'ATOM     42  OG1 GLY A  20      -1.399  42.633 -13.704  1.00 17.85           O  '

            ): ('diffrent res_name', False),
            (
                'ATOM     42  OG1 THR A  20      -1.399  42.633 -13.704  1.00 17.85           O  ',
                'ATOM     42  OG1 THR A  2i      -1.399  42.633 -13.704  1.00 17.85           O  ',
            ): ('diffrent resseq', False),
        }

    def test_is_eqvivalent_atoms(self):
        eqviv_atoms = eqvivalent_atoms()
        for test_data, test_result in self.test_dict.items():
            atom1 = pdb_atom(test_data[0])
            atom2 = pdb_atom(test_data[1])
            (test_name, expected_result) = test_result[0], test_result[1]
            result = eqviv_atoms.is_eqvivalent_atoms(atom1, atom2)
            self.assertEqual(result, expected_result, test_name)
