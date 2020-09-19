from Chemistry.PDB.pdb_constants import pdb_constants


class pdb_remark(list):
    """
    pdb_remark is  a list of remark record and
    has remark_number
    012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
    REMARK   1
    REMARK   1 REFERENCE 1
    REMARK   1  AUTH   J.H.CHILL,R.NIVASCH,R.LEVY,S.ALBECK,G.SCHREIBER,
    REMARK   1  AUTH 2 J.ANGLISTER
    REMARK   1  TITL   THE HUMAN INTERFERON RECEPTOR: NMR-BASED MODELING,
    REMARK   1  TITL 2 MAPPING OF THE IFN-ALPHA2 BINDING SITE, AND
    REMARK   1  TITL 3 OBSERVED LIGAND-INDUCED TIGHTENING
    REMARK   1  REF    BIOCHEMISTRY                  V.  41  3575 2002
    REMARK   1  REFN                   ISSN 0006-2960
    REMARK   1  DOI    10.1021/BI011778F
    """

    @classmethod
    def is_remark_line(cls, pdb_line):
        return pdb_line.startswith(pdb_constants().REMARK)

    @classmethod
    def parse_remark_number(cls, pdb_line):
        return pdb_line[6:10].strip()

    @classmethod
    def parse_remark_text(cls, pdb_line):
        return pdb_line[10:].strip()

    @classmethod
    def parse_remark_line(cls, pdb_line):
        if not cls.is_remark_line(pdb_line):
            raise ValueError("not a remark line:'{}'".format(pdb_line))
        remark_number = cls.parse_remark_number(pdb_line)
        remark_text = cls.parse_remark_text(pdb_line)
        return remark_number, remark_text

    @classmethod
    def from_lines(cls, lines):
        remarks_records = list(map(cls.parse_remark_line, lines))
        remark_number = list(map(lambda r: r[0], remarks_records))
        remark_texts = list(map(lambda r: r[1], remarks_records))
        if len(set(remark_number)) != 1:
            raise ValueError("not a single remark got those remark numbers:{}".format(set(remark_number)))
        return cls(remark_number[0], remark_texts)

    def __init__(self, remark_number, remark_texts):
        _remark_number = remark_number
        if remark_number is None or remark_number == '':
            _remark_number = 0
        self.remark_number = _remark_number
        self.extend(remark_texts)

    def __str__(self):
        s = ""
        to_line = lambda ln: "{}{:>4} {}".format(pdb_constants().REMARK, self.remark_number, ln)
        s += "\n".join(map(to_line, self))
        s += "\n"
        return s


class pdb_remarks_dict(dict):
    """
    pdb_remarks_dict is a dict of pdb_remarks - the keys wre the remark_number
    """

    @classmethod
    def from_lines(cls, lines):
        """
         retern th dict from PDB file lines
        :param lines:
        :return: dict of remarks
        """
        # filter only remarks lines
        pdb_lines = list(filter(pdb_remark.is_remark_line, lines))

        # set remarks unique numbers
        tmp = list(map(pdb_remark.parse_remark_number, pdb_lines))
        remarks_numbers = []
        # add the numbers by their order
        for n in tmp:
            if n not in remarks_numbers:
                remarks_numbers.append(n)

        # for each_remark create remark object and appnd it to a list
        is_r_number_eq_n = lambda r, n: pdb_remark.parse_remark_number(r) == n
        remarks_dict = {}
        remarks_order = []
        for n in remarks_numbers:
            is_remark_n = lambda r: is_r_number_eq_n(r, n)
            remark_lines = list(filter(is_remark_n, pdb_lines))
            remark = pdb_remark.from_lines(remark_lines)
            _remark_number = remark.remark_number
            if _remark_number is None or _remark_number == '':
                _remark_number = 0
            remarks_dict[int(_remark_number)] = remark
            remarks_order.append(int(remark.remark_number))
        return cls(remarks_dict, remarks_order)

    def __init__(self, pdb_remarks_dict, remarks_order=None):

        if remarks_order is None:
            remarks_order = []
        for rn in pdb_remarks_dict:
            self[rn] = pdb_remarks_dict[rn]
        self.remarks_order = remarks_order

    def __str__(self):
        s = ""
        for remark_number in sorted(self):
            remark = self[remark_number]
            s += str(remark)
        return s
