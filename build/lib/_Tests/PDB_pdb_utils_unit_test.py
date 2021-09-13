import unittest

from Chemistry.PDB.pdb_obj import pdb
from Chemistry.PDB.pdb_utils import *


class Test_pdb_info(unittest.TestCase):
    def get_path(self, sub_dir=None, pdb_file_name=None):
        _path = self.pdb_dir.copy()
        if sub_dir: _path.append(sub_dir)
        _path.append(pdb_file_name)
        _file = sys.modules['__main__'].__file__
        getcwd = os.path.abspath(os.path.dirname(_file))
        full_path = os.path.join(getcwd, "_Tests", *_path)
        if not os.path.isfile(full_path):
            getcwd = os.getcwd()
            full_path = os.path.join(getcwd, "_Tests", *_path)
        return full_path

    # H:\Chemistry\code\_Tests\pdb_files\pdb_utils_files\1HFF.pdb
    # H:\\Chemistry\code\_Tests\pdb_files\pdb_utils\\1HFF.pdb
    def setUp(self):
        self.pdb_dir = ["pdb_files"]
        self.pdb_1HFF = self.get_path(pdb_file_name='1HFF.pdb')
        self.pdb_1aib = self.get_path(pdb_file_name='1aib-3.pdb')
        self.pdb_4xia = self.get_path(sub_dir="good_files", pdb_file_name='4xia.pdb')
        self.pdb_2ZVK_missingRES = self.get_path(pdb_file_name='2ZVK_missingRES.pdb')
        self.pdb_5tor = self.get_path(pdb_file_name='5tor.pdb')  # 2v2h
        self.pdb_2v2h = self.get_path(pdb_file_name='2v2h.pdb')
        self.pdb_1g2y = self.get_path(pdb_file_name='1g2y.pdb')  # unit matrix with all peptides
        self.pdb_3cwr = self.get_path(pdb_file_name='3cwr.pdb')  # unit matrix with part of the peptides
        self.pdb_3mux = self.get_path(pdb_file_name='3mux.pdb')  # not a unit matrix
        self.pdb_3mwj = self.get_path(pdb_file_name='3mwj.pdb')  # missing remark 3503

    def test_parse_remark_2__resolution_info(self):
        pdb_1HFF = pdb.from_file(self.pdb_1HFF)
        info_1HFF = pdb_info(pdb_1HFF)
        resseq = pdb_1HFF.get_resseq_as_chaindict()
        self.assertIsInstance(info_1HFF, pdb_info)
        self.assertRaises(ValueError, info_1HFF.parse_remark_2)

        pdb_4xia = pdb.from_file(self.pdb_4xia)
        info_4xia = pdb_info(pdb_4xia)
        self.assertIsInstance(info_4xia, pdb_info)
        info_4xia.parse_remark_2()
        self.assertEqual(info_4xia.Resolution_Grade, 'Good')

    def test_parse_remark_3__get_r_free_grade(self):
        pdb_1HFF = pdb.from_file(self.pdb_1HFF)
        info_1HFF = pdb_info(pdb_1HFF)
        self.assertIsInstance(info_1HFF, pdb_info)
        self.assertRaises(ValueError, info_1HFF.parse_remark_3)

        pdb_4xia = pdb.from_file(self.pdb_4xia)
        info_4xia = pdb_info(pdb_4xia)
        self.assertIsInstance(info_4xia, pdb_info)
        info_4xia.parse_remark_2()
        info_4xia.parse_remark_3()
        self.assertEqual(info_4xia.R_free_grade, 'NULL')
        self.assertEqual(info_4xia.R_value, '0.147')

        pdb_2Z = pdb.from_file(self.pdb_2ZVK_missingRES)
        info_2Z = pdb_info(pdb_2Z)
        self.assertIsInstance(info_2Z, pdb_info)
        info_2Z.parse_remark_2()
        info_2Z.parse_remark_3()
        self.assertEqual(info_2Z.Resolution_Grade, 'Good/Fair')
        self.assertEqual(info_2Z.R_value, '0.215')
        self.assertEqual(info_2Z.R_free_grade, 'Worse than average at this resolution')

    def test_parse_remark_3__get_r_free_grade_first_r_free(self):
        pdb_2v2h = pdb.from_file(self.pdb_2v2h)
        info_2v2h = pdb_info(pdb_2v2h)
        self.assertIsInstance(info_2v2h, pdb_info)
        info_2v2h.parse_remark_2()
        info_2v2h.parse_remark_3()
        self.assertEqual(info_2v2h.R_free, '0.1868')

    def test_parse_remark_350(self):
        pdb_4xia = pdb.from_file(self.pdb_4xia)
        info_4xia = pdb_info(pdb_4xia)
        self.assertIsInstance(info_4xia, pdb_info)
        info_4xia.parse_remark_350()
        self.assertEqual(info_4xia.bio_struct_identical_to_the_asymmetric_unit, False)

        pdb_1g2y = pdb.from_file(self.pdb_1g2y)
        info_1g2y = pdb_info(pdb_1g2y)
        self.assertIsInstance(info_1g2y, pdb_info)
        info_1g2y.parse_remark_350(bio_molecule_chains=4)
        self.assertEqual(info_1g2y.bio_struct_identical_to_the_asymmetric_unit, True, 'unit matrix with all peptides')

        info_1g2y = pdb_info(pdb_1g2y)
        info_1g2y.parse_remark_350(bio_molecule_chains=1)
        self.assertEqual(info_1g2y.bio_struct_identical_to_the_asymmetric_unit, False)

        pdb_3cwr = pdb.from_file(self.pdb_3cwr)
        info_3cwr = pdb_info(pdb_3cwr)
        self.assertIsInstance(info_3cwr, pdb_info)
        info_3cwr.parse_remark_350()
        self.assertEqual(info_3cwr.bio_struct_identical_to_the_asymmetric_unit, False,
                         'unit matrix with part of the peptides')

        pdb_3mux = pdb.from_file(self.pdb_3mux)
        info_3mux = pdb_info(pdb_3mux)
        self.assertIsInstance(info_3mux, pdb_info)
        info_3mux.parse_remark_350()
        self.assertEqual(info_3mux.bio_struct_identical_to_the_asymmetric_unit, False, 'not a unit matrix')

        pdb_3mwj = pdb.from_file(self.pdb_3mwj)
        info_3mwj = pdb_info(pdb_3mwj)
        self.assertIsInstance(info_3mwj, pdb_info)
        info_3mwj.parse_remark_350()
        self.assertEqual(info_3mwj.bio_struct_identical_to_the_asymmetric_unit, False, ' missing remark 350')

    def test_parse_remark_465_get_r_free_grade(self):
        pdb_5tor = pdb.from_file(self.pdb_5tor)
        info_5tor = pdb_info(pdb_5tor)
        self.assertIsInstance(info_5tor, pdb_info)
        info_5tor.parse_remark_465()
        missing_residues = info_5tor.missing_residues
        # REMARK 465   M RES C SSSEQI
        # REMARK 465     GLN B   412
        # REMARK 470

        self.assertEqual(len(missing_residues), 1)
        self.assertEqual(missing_residues[0]["resname"], "GLN")
        self.assertEqual(missing_residues[0]["chain_id"], "B")

    def test_parse_remark_470_get_r_free_grade(self):
        pdb_5tor = pdb.from_file(self.pdb_5tor)
        info_1tor = pdb_info(pdb_5tor)
        self.assertIsInstance(info_1tor, pdb_info)
        info_1tor.parse_remark_470()
        missing_atoms = info_1tor.missing_atoms
        # REMARK 470   M RES CSSEQI  ATOMS
        # REMARK 470     ALA B   1    CA
        # REMARK 470     GLN B  13    CD
        # REMARK 500
        self.assertEqual(len(missing_atoms), 2)
        self.assertEqual(missing_atoms[0]["resname"], "ALA")
        self.assertEqual(missing_atoms[1]["atom_names"], ["CD"])

    def test_is_nmr(self):
        pdb_1HFF = pdb.from_file(self.pdb_1HFF)
        info_1HFF = pdb_info(pdb_1HFF)
        self.assertIsInstance(info_1HFF, pdb_info)
        self.assertEqual(info_1HFF.is_nmr(), True)

    def test_is_homomer_1HFF(self):
        pdb_1HFF = pdb.from_file(self.pdb_1HFF)
        info_1HFF = pdb_info(pdb_1HFF)
        self.assertIsInstance(info_1HFF, pdb_info)
        self.assertEqual(info_1HFF.is_homomer(), True)

    def test_is_homomer_4xia(self):
        pdb_4xia = pdb.from_file(self.pdb_4xia)
        info_4xia = pdb_info(pdb_4xia)
        self.assertIsInstance(info_4xia, pdb_info)
        self.assertEqual(info_4xia.is_homomer(), True)

    # def test_is_homomer_1aib(self):
    #     pdb_1aib = pdb.from_file(self.pdb_1aib)
    #     info_1aib = pdb_info(pdb_1aib)
    #     self.assertIsInstance(info_1aib, pdb_info)
    #     self.assertEqual(info_1aib.is_homomer(), True)

    def test_is_homomer_2v2h(self):
        pdb_2v2h = pdb.from_file(self.pdb_2v2h)
        info_2v2h = pdb_info(pdb_2v2h)
        self.assertIsInstance(info_2v2h, pdb_info)
        self.assertEqual(info_2v2h.is_homomer(), True)
