import unittest
import os
from Chemistry.PDB.pdb_model import pdb_model


class Test_pdb_model(unittest.TestCase):
    def setUp(self):
        self.model_lines1 = [
            'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00           N1+',
            'ATOM      2  CA  GLY     1       0.112   0.550   0.170  1.00  0.00           C',
            'ATOM      3  C   GLY     1       1.240  -0.152  -0.119  1.00  0.00           C',
            'ATOM      4  O   GLY     1       1.176  -1.323  -0.521  1.00  0.00           O',
            'ATOM      5  H1  GLY     1      -0.933  -1.171   0.368  1.00  0.00           H',
            'ATOM      6  H2  GLY     1      -1.221  -0.423  -1.054  1.00  0.00           H',
            'ATOM      7  H3  GLY     1      -1.924   0.172   0.330  1.00  0.00           H',
            'ATOM      8  HA2 GLY     1       0.107   1.445  -0.451  1.00  0.00           H',
            'ATOM      9  HA3 GLY     1       0.177   0.840   1.218  1.00  0.00           H',
            'ATOM     10  N   GLY     2       2.371   0.492   0.057  1.00  0.00           N',
            'ATOM     11  CA  GLY     2       3.674  -0.160  -0.222  1.00  0.00           C',
            'ATOM     12  C   GLY     2       4.711   0.684   0.027  1.00  0.00           C',
            'ATOM     13  O   GLY     2       4.510   1.838   0.434  1.00  0.00           O',
            'ATOM     14  H   GLY     2       2.354   1.437   0.384  1.00  0.00           H',
            'ATOM     15  HA2 GLY     2       3.809  -1.046   0.397  1.00  0.00           H',
            'ATOM     16  HA3 GLY     2       3.738  -0.441  -1.272  1.00  0.00           H',
            'ATOM     17  N   GLY     3       5.910   0.193  -0.192  1.00  0.00           N',
            'ATOM     18  CA  GLY     3       7.126   1.010   0.040  1.00  0.00           C',
            'ATOM     19  C   GLY     3       8.254   0.308  -0.249  1.00  0.00           C',
            'ATOM     20  O   GLY     3       8.691   0.304  -1.375  1.00  0.00           O',
            'ATOM     21  OXT GLY     3       8.839  -0.334   0.651  1.00  0.00           O1-',
            'ATOM     22  H   GLY     3       6.004  -0.747  -0.521  1.00  0.00           H',
            'ATOM     23  HA2 GLY     3       7.121   1.905  -0.581  1.00  0.00           H',
            'ATOM     24  HA3 GLY     3       7.191   1.300   1.088  1.00  0.00           H',
            'TER      25      GLY     3',
        ]

        self.model_lines2 = [
            'ATOM      1  N   GLY     1      -1.104  -0.267  -0.062  1.00  0.00           N1+',
            'ATOM      2  CA  GLY     1       0.112   0.550   0.170  1.00  0.00           C',
            'ATOM      3  C   GLY     1       1.240  -0.152  -0.119  1.00  0.00           C',
            'ATOM      4  O   GLY     1       1.176  -1.323  -0.521  1.00  0.00           O',
            'ATOM      5  H1  GLY     1      -0.933  -1.171   0.368  1.00  0.00           H',
            'ATOM      6  H2  GLY     1      -1.221  -0.423  -1.054  1.00  0.00           H',
            'ATOM      7  H3  GLY     1      -1.924   0.172   0.330  1.00  0.00           H',
            'ATOM      8  HA2 GLY     1       0.107   1.445  -0.451  1.00  0.00           H',
            'ATOM      9  HA3 GLY     1       0.177   0.840   1.218  1.00  0.00           H',
            'ATOM     10  N   GLY     2       2.371   0.492   0.057  1.00  0.00           N',
            'ATOM     11  CA  GLY     2       3.674  -0.160  -0.222  1.00  0.00           C',
            'ATOM     12  C   GLY     2       4.711   0.684   0.027  1.00  0.00           C',
            'ATOM     13  O   GLY     2       4.510   1.838   0.434  1.00  0.00           O',
            'ATOM     14  H   GLY     2       2.354   1.437   0.384  1.00  0.00           H',
            'ATOM     15  HA2 GLY     2       3.809  -1.046   0.397  1.00  0.00           H',
            'ATOM     16  HA3 GLY     2       3.738  -0.441  -1.272  1.00  0.00           H',
            'ATOM     17  N   GLY     3       5.910   0.193  -0.192  1.00  0.00           N',
            'ATOM     18  CA  GLY     3       7.126   1.010   0.040  1.00  0.00           C',
            'ATOM     19  C   GLY     3       8.254   0.308  -0.249  1.00  0.00           C',
            'ATOM     20  O   GLY     3       8.691   0.304  -1.375  1.00  0.00           O',
            'ATOM     21  OXT GLY     3       8.839  -0.334   0.651  1.00  0.00           O1-',
            'ATOM     22  H   GLY     3       6.004  -0.747  -0.521  1.00  0.00           H',
            'ATOM     23  HA2 GLY     3       7.121   1.905  -0.581  1.00  0.00           H',
            'ATOM     24  HA3 GLY     3       7.191   1.300   1.088  1.00  0.00           H',
            'TER      25      GLY     3',
            'ATOM      1  N   GLY     1      -1.105  -0.267  -0.062  1.00  0.00           N1+',
            'ATOM      2  CA  GLY     1       0.112   0.550   0.170  1.00  0.00           C',
            'ATOM      3  C   GLY     1       1.240  -0.152  -0.119  1.00  0.00           C',
            'ATOM      4  O   GLY     1       1.176  -1.323  -0.522  1.00  0.00           O',
            'ATOM      5  H1  GLY     1      -0.933  -1.171   0.368  1.00  0.00           H',
            'ATOM      6  H2  GLY     1      -1.222  -0.423  -1.054  1.00  0.00           H',
            'ATOM      7  H3  GLY     1      -1.924   0.172   0.330  1.00  0.00           H',
            'ATOM      8  HA2 GLY     1       0.107   1.445  -0.451  1.00  0.00           H',
            'ATOM      9  HA3 GLY     1       0.177   0.840   1.228  1.00  0.00           H',
            'ATOM     10  N   GLY     2       2.371   0.492   0.057  1.00  0.00           N',
            'ATOM     11  CA  GLY     2       3.674  -0.160  -0.222  1.00  0.00           C',
            'ATOM     12  C   GLY     2       4.711   0.684   0.027  1.00  0.00           C',
            'ATOM     13  O   GLY     2       4.510   1.838   0.434  1.00  0.00           O',
            'ATOM     14  H   GLY     2       2.354   1.437   0.384  1.00  0.00           H',
            'ATOM     15  HA2 GLY     2       3.809  -1.056   0.397  1.00  0.00           H',
            'ATOM     16  HA3 GLY     2       3.738  -0.441  -1.272  1.00  0.00           H',
            'ATOM     17  N   GLY     3       5.910   0.193  -0.192  1.00  0.00           N',
            'ATOM     18  CA  GLY     3       7.126   1.010   0.050  1.00  0.00           C',
            'ATOM     19  C   GLY     3       8.254   0.308  -0.249  1.00  0.00           C',
            'ATOM     20  O   GLY     3       8.691   0.305  -1.375  1.00  0.00           O',
            'ATOM     21  OXT GLY     3       8.839  -0.334   0.651  1.00  0.00           O1-',
            'ATOM     22  H   GLY     3       6.005  -0.747  -0.522  1.00  0.00           H',
            'ATOM     23  HA2 GLY     3       7.122   1.905  -0.581  1.00  0.00           H',
            'ATOM     24  HA3 GLY     3       7.191   1.300   1.088  1.00  0.00           H',
            'TER      25      GLY     3',
        ]

        self.model_lines3 = [
            'ATOM      1  N   ASN A 392     -47.103  65.135 118.356  1.00 68.22           N  ',
            'ANISOU    1  N   ASN A 392     9014   7623   9282  -1326    681  -1471       N  ',
            'ATOM      2  CA  ASN A 392     -48.222  66.052 118.174  1.00 67.07           C  ',
            'ANISOU    2  CA  ASN A 392     8992   7310   9182  -1233    804  -1475       C  ',
            'ATOM      3  C   ASN A 392     -49.592  65.355 118.260  1.00 59.66           C  ',
            'ANISOU    3  C   ASN A 392     8111   6445   8112  -1090    830  -1431       C  ',
            'ATOM      4  O   ASN A 392     -49.994  64.873 119.323  1.00 58.53           O  ',
            'ANISOU    4  O   ASN A 392     7979   6442   7816  -1080    761  -1522       O  ',
            'ATOM      5  CB  ASN A 392     -48.077  66.802 116.844  1.00 69.92           C  ',
            'ANISOU    5  CB  ASN A 392     9375   7473   9718  -1212    934  -1344       C  ',
            'ATOM      6  CG  ASN A 392     -48.975  68.022 116.759  1.00 75.31           C  ',
            'ANISOU    6  CG  ASN A 392    10181   7957  10478  -1134   1044  -1365       C  ',
            'ATOM      7  OD1 ASN A 392     -49.236  68.689 117.762  1.00 78.64           O  ',
            'ANISOU    7  OD1 ASN A 392    10654   8344  10881  -1157   1023  -1521       O  ',
            'ATOM      8  ND2 ASN A 392     -49.459  68.315 115.559  1.00 76.30           N  ',
            'ANISOU    8  ND2 ASN A 392    10357   7954  10679  -1028   1155  -1206       N  ',
            'ATOM      9  N   LYS A 393     -50.297  65.295 117.134  1.00 49.77           N  ',
            'ANISOU    9  N   LYS A 393     6892   5104   6914   -976    927  -1286       N  ',
            'ATOM     10  CA  LYS A 393     -51.665  64.791 117.106  1.00 42.76           C  ',
            'ANISOU   10  CA  LYS A 393     6049   4261   5937   -831    959  -1244       C  ',
            'ATOM     11  C   LYS A 393     -51.716  63.271 117.034  1.00 32.99           C  ',
            'ANISOU   11  C   LYS A 393     4752   3207   4575   -818    887  -1178       C  ',
            'ATOM     12  O   LYS A 393     -50.813  62.627 116.499  1.00 36.37           O  ',
            'ANISOU   12  O   LYS A 393     5114   3685   5021   -879    839  -1109       O  ',
            'ATOM     13  CB  LYS A 393     -52.426  65.384 115.918  1.00 43.27           C  ',
            'ANISOU   13  CB  LYS A 393     6172   4159   6109   -696   1072  -1113       C  ',
            'ATOM     14  CG  LYS A 393     -52.569  66.896 115.977  1.00 56.21           C  ',
            'ANISOU   14  CG  LYS A 393     7887   5603   7866   -685   1149  -1166       C  ',
            'ATOM     15  CD  LYS A 393     -53.355  67.328 117.210  1.00 61.23           C  ',
            'ANISOU   15  CD  LYS A 393     8567   6261   8437   -655   1143  -1324       C  ',
            'ATOM     16  CE  LYS A 393     -53.591  68.830 117.219  1.00 59.02           C  ',
            'ANISOU   16  CE  LYS A 393     8374   5768   8283   -626   1221  -1378       C  ',
            'ATOM     17  NZ  LYS A 393     -54.502  69.224 118.322  1.00 60.12           N  ',
            'ANISOU   17  NZ  LYS A 393     8561   5927   8355   -565   1228  -1524       N  ',
            'ATOM     18  N   ALA A 775     -49.308  21.737 111.282  1.00 63.05           N  ',
            'ANISOU   19  N   ALA A 775     8305   6421   9229    -71   -637    955       N  ',
            'TER      20      ALA A 775                                                      ',
            'HETATM   21  N   GLU A 900     -56.394  42.746  99.686  1.00 12.28           N  ',
            'ANISOU   21  N   GLU A 900     1937   1498   1231    142    -51    -57       N  ',
            'HETATM   22  CA  GLU A 900     -57.621  42.955  98.892  1.00 11.62           C  ',
            'ANISOU   22  CA  GLU A 900     1552   1483   1381     92      5    -42       C  ',
            'HETATM   23  C   GLU A 900     -57.796  44.440  98.656  1.00 12.83           C  ',
            'ANISOU   23  C   GLU A 900     1524   1704   1648    114      7     57       C  ',
            'HETATM   24  O   GLU A 900     -56.948  45.257  99.093  1.00 11.79           O  ',
            'ANISOU   24  O   GLU A 900     1505   1579   1396    162    -25    116       O  ',
            'HETATM   25  CB  GLU A 900     -58.850  42.383  99.611  1.00 14.40           C  ',
            'ANISOU   25  CB  GLU A 900     1972   1628   1871    -24    241    -98       C  ',
            'HETATM   26  CG  GLU A 900     -58.965  40.878  99.434  1.00 13.62           C  ',
            'ANISOU   26  CG  GLU A 900     1970   1488   1717    -69    185   -180       C  ',
            'HETATM   27  CD  GLU A 900     -59.380  40.388  98.028  1.00 14.71           C  ',
            'ANISOU   27  CD  GLU A 900     1809   1814   1965    -45     43   -210       C  ',
            'HETATM   28  OE1 GLU A 900     -59.856  41.229  97.192  1.00 15.00           O  ',
            'ANISOU   28  OE1 GLU A 900     1549   1994   2155    -27     15   -158       O  ',
            'HETATM   29  OE2 GLU A 900     -59.274  39.157  97.788  1.00 15.26           O  ',
            'ANISOU   29  OE2 GLU A 900     1952   1869   1976    -55    -53   -285       O  ',
            'HETATM   30  OXT GLU A 900     -58.775  44.827  98.009  1.00 12.04           O  ',
            'ANISOU   30  OXT GLU A 900     1168   1641   1766     86     13     75       O  ',
            'ATOM     31  N   LYS B 393     -66.764  10.864 127.882  1.00 49.74           N  ',
            'ANISOU   31  N   LYS B 393     7459   5042   6399   1501   1303    608       N  ',
            'ATOM     32  CA  LYS B 393     -67.689  11.257 126.825  1.00 46.97           C  ',
            'ANISOU   32  CA  LYS B 393     7210   4625   6012   1300   1312    416       C  ',
            'ATOM     33  C   LYS B 393     -67.820  12.775 126.751  1.00 37.29           C  ',
            'ANISOU   33  C   LYS B 393     5881   3559   4730   1238   1202    360       C  ',
            'ATOM     34  O   LYS B 393     -67.749  13.464 127.768  1.00 42.91           O  ',
            'ANISOU   34  O   LYS B 393     6458   4445   5400   1232   1072    448       O  ',
            'ATOM     35  CB  LYS B 393     -69.070  10.638 127.051  1.00 52.47           C  ',
            'ANISOU   35  CB  LYS B 393     8070   5178   6688   1134   1324    363       C  ',
            'ATOM     36  CG  LYS B 393     -70.066  10.938 125.935  1.00 60.78           C  ',
            'ANISOU   36  CG  LYS B 393     9207   6195   7693    916   1321    172       C  ',
            'ATOM     37  CD  LYS B 393     -71.393  10.232 126.135  1.00 69.13           C  ',
            'ANISOU   37  CD  LYS B 393    10398   7135   8734    749   1338    121       C  ',
            'ATOM     38  CE  LYS B 393     -72.192  10.210 124.837  1.00 73.93           C  ',
            'ANISOU   38  CE  LYS B 393    11076   7720   9296    553   1352    -58       C  ',
            'ATOM     39  NZ  LYS B 393     -71.394   9.690 123.685  1.00 76.45           N  ',
            'ANISOU   39  NZ  LYS B 393    11422   7989   9634    602   1451   -117       N  ',
            'ATOM     40  N   ALA B 775     -72.131  55.004 131.737  1.00 62.02           N  ',
            'ANISOU   40  N   ALA B 775     9702   5074   8788  -1599    930     87       N  ',
            'TER      41      ALA B 775                                                ',
            'HETATM   42  N   GLU B 900     -85.387  33.136 131.278  1.00 17.60           N  ',
            'ANISOU   42  N   GLU B 900     2996   1746   1946   -238    433   -184       N  ',
            'HETATM   43  CA  GLU B 900     -86.668  32.904 130.595  1.00 16.25           C  ',
            'ANISOU   43  CA  GLU B 900     2925   1567   1681   -230    367   -145       C  ',
            'HETATM   44  C   GLU B 900     -87.017  31.433 130.619  1.00 17.46           C  ',
            'ANISOU   44  C   GLU B 900     3202   1745   1687   -275    259   -113       C  ',
            'HETATM   45  O   GLU B 900     -86.230  30.625 131.109  1.00 16.05           O  ',
            'ANISOU   45  O   GLU B 900     3094   1582   1422   -275    252   -110       O  ',
            'HETATM   46  CB  GLU B 900     -86.710  33.465 129.166  1.00 17.48           C  ',
            'ANISOU   46  CB  GLU B 900     3216   1598   1828   -101    403    -38       C  ',
            'HETATM   47  CG  GLU B 900     -86.947  34.980 129.119  1.00 18.54           C  ',
            'ANISOU   47  CG  GLU B 900     3287   1621   2135    -92    425    -45       C  ',
            'HETATM   48  CD  GLU B 900     -88.364  35.451 129.502  1.00 18.08           C  ',
            'ANISOU   48  CD  GLU B 900     3162   1616   2091    -60    269   -206       C  ',
            'HETATM   49  OE1 GLU B 900     -89.297  34.620 129.568  1.00 19.13           O  ',
            'ANISOU   49  OE1 GLU B 900     3250   1880   2140    -81    178   -259       O  ',
            'HETATM   50  OE2 GLU B 900     -88.512  36.682 129.748  1.00 19.09           O  ',
            'ANISOU   50  OE2 GLU B 900     3259   1646   2349     -8    216   -279       O  ',
            'HETATM   51  OXT GLU B 900     -88.065  31.023 130.122  1.00 16.83           O  ',
            'ANISOU   51  OXT GLU B 900     3163   1625   1606   -308    125    -99       O  ',

        ]

    def test_init1(self):
        model = pdb_model.from_pdb_model_lines(self.model_lines1)
        self.assertIsInstance(model, pdb_model)
        self.assertEqual(model.model_number, '1')
        self.assertEqual(len(model), 1)

    def test_init2(self):
        model = pdb_model.from_pdb_model_lines(self.model_lines2)
        self.assertIsInstance(model, pdb_model)
        self.assertEqual(model.model_number, '1')
        self.assertEqual(len(model), 2)

    def test_init3(self):
        model = pdb_model.from_pdb_model_lines(self.model_lines3)
        self.assertIsInstance(model, pdb_model)
        self.assertEqual(model.model_number, '1')
        self.assertEqual(len(model), 2)
        chain_a = model[0]
        chain_b = model[1]
        self.assertEqual(chain_a.chain_id, 'A')
        self.assertEqual(chain_b.chain_id, 'B')
        # self.assertEqual(len(chain_a), 19)
        self.assertEqual(chain_a[-1].record_name, 'ATOM')
        self.assertEqual(chain_a[-1].atom_name, 'N')
        self.assertEqual(chain_a[-1].resname, 'ALA')
        atoms_str = "-".join(map(lambda a: a.atom_name, chain_a))
        self.assertEqual(atoms_str,
                         'N-CA-C-O-CB-CG-OD1-ND2-N-CA-C-O-CB-CG-CD-CE-NZ-N')
