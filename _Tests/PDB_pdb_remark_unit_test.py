import os
import sys
import unittest

from Chemistry.PDB.pdb_remark import *


class Test_pdb_remark(unittest.TestCase):
    """
    remark partiicular parser _Tests (2,3  ,465) are in pdb_info
    """

    def get_path(self, pdb_file_name):
        _file = sys.modules['__main__'].__file__
        getcwd = os.path.abspath(os.path.dirname(_file))
        full_path = os.path.join(getcwd, "_Tests", self.pdb_dir, pdb_file_name)
        if not os.path.isfile(full_path):
            getcwd = os.getcwd()
            full_path = os.path.join(getcwd, "_Tests", self.pdb_dir, pdb_file_name)
        return full_path

    def setUp(self):
        self.pdb_dir = "pdb_files"
        self.pdb_1tor = self.get_path(os.path.join('pdb_prep', '1tor.pdb'))
        self.two_peptides_no_model = self.get_path('two_peptides_no_model.pdb')
        self.pdb_1xy1 = self.get_path('1xy1.pdb')
        self.remark2_lines = [
            'REMARK   2',
            'REMARK   2 RESOLUTION.    1.04 ANGSTROMS.'
        ]

    def test_from_lines(self):
        file = self.pdb_1xy1
        remarks = []
        with open(file) as f:
            pdb_file_lines = f.readlines()
            remarks = pdb_remarks_dict.from_lines(pdb_file_lines)
            self.assertIsInstance(remarks, dict)
            remark_2 = remarks[2]
            self.assertIsInstance(remark_2, pdb_remark)
            self.assertEqual(int(remark_2.remark_number), 2)
