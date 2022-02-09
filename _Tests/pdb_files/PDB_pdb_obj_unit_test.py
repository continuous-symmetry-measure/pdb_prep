import os
import sys
import unittest

from Chemistry.PDB.pdb_obj import pdb
from Chemistry.PDB.pdb_obj import pdb_file_parser


class Test_pdb_file_parser(unittest.TestCase):
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

    def test_init(self):
        file_name = self.get_path('one_peptide.pdb')
        parser = pdb_file_parser.from_file(file_name)
        self.assertIsInstance(parser, pdb_file_parser)

    def test_parse_remarks(self):
        file_name = self.get_path('one_peptide.pdb')
        parser = pdb_file_parser.from_file(file_name)
        remarks = parser.parse_remarks()
        self.assertEqual(len(remarks), 1)
        self.assertEqual(len(remarks[99]), 2)
        self.assertEqual(remarks[99].remark_number, '99')

    def test_get_models_lines(self):
        file_name = self.get_path('one_peptide.pdb')
        parser = pdb_file_parser.from_file(file_name)
        model_lines = parser.get_models_lines()
        self.assertEqual(len(model_lines), 26)
        self.assertEqual(model_lines[0],
                         'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00           N1+')
        self.assertEqual(model_lines[23],
                         'ATOM     24  HA3 GLY     3       7.191   1.300   1.088  1.00  0.00           H')
        self.assertEqual(model_lines[24],
                         'TER      25      GLY     3')
        self.assertEqual(model_lines[25], 'END')

    def test_get_next_model_lines(self):
        one_peptide = self.get_path('one_peptide.pdb')
        parser = pdb_file_parser.from_file(one_peptide)
        (model_number, model_lines) = parser.get_next_model_lines()
        self.assertEqual(model_number, '1')
        self.assertEqual(model_lines[0],
                         'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00           N1+')
        self.assertEqual(model_lines[23],
                         'ATOM     24  HA3 GLY     3       7.191   1.300   1.088  1.00  0.00           H')
        self.assertEqual(model_lines[24],
                         'TER      25      GLY     3')
        self.assertEqual(model_number, '1')

        # two_model_peptides
        two_model_peptides = self.get_path('two_model_peptides.pdb')
        parser = pdb_file_parser.from_file(two_model_peptides)
        # model 1
        (model_number, model_lines) = parser.get_next_model_lines()
        self.assertEqual(model_number, '1')
        self.assertEqual(model_lines[1],
                         'ATOM      2  CA  GLY     1       0.112   0.550   0.170  1.00  0.00           C')
        (model_number, pdb_model_lines) = parser.get_next_model_lines()
        self.assertEqual(model_number, '2')
        self.assertEqual(model_lines[1],
                         'ATOM      2  CA  GLY     1       0.112   0.550   0.170  1.00  0.00           C')

        (model_number, pdb_model_lines) = parser.get_next_model_lines()
        self.assertEqual(model_number, None)
        self.assertEqual(pdb_model_lines, None)


class Test_pdb(unittest.TestCase):
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
        self.one_peptide = self.get_path('one_peptide.pdb')
        self.two_model_peptides = self.get_path('two_model_peptides.pdb')
        self.two_peptides_no_model = self.get_path('two_peptides_no_model.pdb')
        self.pdb_1HFF = self.get_path('1HFF.pdb')
        self.pdb_1aib = self.get_path(os.path.join('distance', '1aib-3.pdb'))
        self.two_peptides_no_model = self.get_path('two_peptides_no_model.pdb')
        self.with_hetatm = self.get_path('1xy1.pdb')

    def test_one_peptide(self):
        mypdb = pdb.from_file(self.one_peptide)
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(mypdb.get_number_of_models(), 1)

    def test_two_model_peptides(self):
        mypdb = pdb.from_file(self.two_model_peptides)
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(mypdb.get_number_of_models(), 2)

    def test_two_peptides_no_model(self):
        mypdb = pdb.from_file(self.two_peptides_no_model)
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(mypdb.get_number_of_models(), 1)

    def test_1HFF(self):
        mypdb = pdb.from_file(self.pdb_1HFF)
        models_numbers = list(map(lambda m: m.model_number, mypdb))
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(models_numbers, list(map(str, range(1, 56))))

    def test_1aib(self):
        mypdb = pdb.from_file(self.pdb_1aib)
        chains_ids = list(map(lambda m: m.chain_id, mypdb[0]))
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(chains_ids, ['A', 'B'])
        self.assertEqual(set(mypdb.remarks.keys()), set([99]))

    def test_two_model_peptides(self):
        mypdb = pdb.from_file(self.two_model_peptides)
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(mypdb.get_number_of_models(), 2)
        model = mypdb[0]
        self.assertEqual(model.get_number_of_chains(), 1)

    def test_with_hetatm(self):
        mypdb = pdb.from_file(self.with_hetatm, include_hetatm=True)
        self.assertIsInstance(mypdb, pdb)
        self.assertEqual(mypdb.get_number_of_models(), 1)
        self.assertEqual(mypdb[0].get_number_of_chains(), 2)
