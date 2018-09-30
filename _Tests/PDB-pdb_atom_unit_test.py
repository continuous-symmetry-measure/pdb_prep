import unittest

from Chemistry.PDB.pdb_atom import *


class Test_pdb_atom(unittest.TestCase):
    def setUp(self):
        self.pdb_atom_line = 'ATOM    105  CD2ATYR A 405     -54.453  39.711 107.320  0.53 14.50           C'
        self.pdb_atom_line_nl = 'ATOM    105  CD2ATYR A 405     -54.453  39.711 107.320  0.53 14.50           C\n'
        self.pdb_atom_line_nl2 = 'ATOM    105  CD2ATYR A 405     -54.453  39.711 107.320  0.53 14.50           C\n\r'

    def test_pdb_atom(self):
        pdb_line = self.pdb_atom_line
        atom = pdb_atom(pdb_line)
        self.assertEquals(atom.x, -54.453, "_Tests x")
        self.assertEquals(atom.tempfactor, 14.50, "_Tests tempfactor")
        self.assertEquals(str(atom).rstrip(), self.pdb_atom_line.rstrip())

    def test_pdb_atom_nl(self):
        pdb_line = self.pdb_atom_line_nl
        atom = pdb_atom(pdb_line)
        self.assertEquals(atom.x, -54.453, "_Tests x")
        self.assertEquals(atom.tempfactor, 14.50, "_Tests tempfactor")
        self.assertEquals(str(atom).rstrip(), self.pdb_atom_line.rstrip())

    def test_pdb_atom_nl2(self):
        pdb_line = self.pdb_atom_line_nl2
        atom = pdb_atom(pdb_line)
        self.assertEquals(atom.x, -54.453, "_Tests x")
        self.assertEquals(atom.tempfactor, 14.50, "_Tests tempfactor")
        self.assertEquals(str(atom).rstrip(), self.pdb_atom_line.rstrip())


class Test_eqvivalent_atoms(unittest.TestCase):
    def setUp(self):
        self.test_dict = {
            (
                'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00',
                'ATOM      1  N   GLY     1      -1.105  -0.257  -0.052  1.00  0.00',

            ): ('same atom', True),
            (
                'ATOM      1  C   GLY     1      -1.104  -0.267  -0.062  1.00  0.00',
                'ATOM      1  N   GLY     1      -1.105  -0.257  -0.052  1.00  0.00',

            ): ('diffrent atom_name', False),
            (
                'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00',
                'ATOM      1  N   ASU     1      -1.105  -0.257  -0.052  1.00  0.00'

            ): ('diffrent res_name', False),
            (
                'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00',
                'ATOM      1  N   GLY     3      -1.105  -0.257  -0.052  1.00  0.00',
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
