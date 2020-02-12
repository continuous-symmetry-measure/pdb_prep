from Chemistry.PDB.pdb_constants import pdb_constants
from Chemistry.PDB.pdb_model import pdb_model
from Chemistry.PDB.pdb_remark import pdb_remarks_dict

"""
* pdb is list of pdb_models
* pdb_model is a list of pdb_chains objects
* pdb _chain is a list of pdb_atom objects
* atom ahs attributes such as:
    - atom_serial_number
    - atom_name
    - resname
    - resseq
    - chain_id
    ...
"""


class pdb_file_parser():
    @classmethod
    def from_file(cls, pdb_file_name, include_hetatm=True):
        with open(pdb_file_name) as f:
            pdb_file_lines = f.readlines()
            return cls(pdb_file_lines, include_hetatm)

    def __init__(self, pdb_file_lines, include_hetatm=False):
        self.pdb_const_str = pdb_constants()
        self.lines = pdb_file_lines
        self.include_hetatm = include_hetatm
        self.index = 0
        self.model_lines = []
        self.wrap_with_header_and_footer = True

    def get_caveats_lines(self):
        is_caveat = lambda ln: ln[0: 6].strip().startswith('CAVEAT')
        caveats_lines = list(filter(is_caveat, self.lines))
        return caveats_lines

    def get_expdta_lines(self):
        is_expdta = lambda ln: ln[0: 6].startswith('EXPDTA')
        expdta_lines = list(filter(is_expdta, self.lines))
        return expdta_lines

    def get_seqres_lines(self):
        is_expdta = lambda ln: ln[0: 6].startswith('SEQRES')
        seqres_lines = list(filter(is_expdta, self.lines))
        return seqres_lines

    def get_models_lines(self):
        """
        returns lines wich are relvaat to the models
        """
        if len(self.model_lines) > 0:
            return self.model_lines
        else:
            def is_model_line(line):
                # position is according to average frequency for better perfomance
                prefixes_list = "ATOM|TER|MODEL|ENDMDL|ANISOU|END".split('|')
                if self.include_hetatm:
                    prefixes_list.insert(1, self.pdb_const_str.HETATM)
                for prefix in (prefixes_list):
                    if line.startswith(prefix): return True
                return False

            self.model_lines = list(map(str.rstrip, filter(is_model_line, self.lines)))
            return self.model_lines

    def get_next_model_lines(self):
        global start, end
        models_lines = self.get_models_lines()
        cnst = self.pdb_const_str
        if self.index >= len(models_lines) or models_lines[self.index].startswith(cnst.END):
            return (None, None)

        # if first line is MODEL:
        #    start from the next line and find the first ENDMDL line this is the end
        #    get model number from the MODEL
        #

        if (models_lines[self.index].startswith(cnst.MODEL)):
            self.wrap_with_header_and_footer = True
            model_number = str(models_lines[self.index].split()[1])
            self.index = self.index + 1
            start = self.index
        else:
            self.wrap_with_header_and_footer = False
            model_number = '1'
            start = self.index
        for i, line in enumerate(models_lines[start:], start):
            end = i
            self.index = i + 1
            if line.startswith(cnst.ENDMDL) or line.startswith(cnst.END):
                break

        return (str(model_number), models_lines[start:end])

    def parse_remarks(self):
        remarks = pdb_remarks_dict.from_lines(self.lines)
        return remarks


class pdb(list):
    @classmethod
    def from_file(cls, pdb_file_name, include_hetatm=True):
        with open(pdb_file_name) as f:
            pdb_file_lines = f.readlines()
            pdb = cls.from_file_lines(pdb_file_lines=pdb_file_lines, include_hetatm=include_hetatm,
                                      pdb_file_name=pdb_file_name)
            pdb.file_name = pdb_file_name
            return pdb

    @classmethod
    def from_file_lines(cls, pdb_file_lines, include_hetatm=False, pdb_file_name=""):
        """

        :param pdb_file_lines:
        :param include_hetatm:
        :param pdb_file_name: we need this only for model warning messages
        :return:
        """
        parser = pdb_file_parser(pdb_file_lines, include_hetatm)
        # prepare remarks
        remarks = parser.parse_remarks()

        # prepare models
        (model_number, pdb_model_lines) = parser.get_next_model_lines()
        models = []
        while model_number:
            model = pdb_model.from_pdb_model_lines(pdb_model_lines, model_number, include_hetatm,
                                                   pdb_file_name=pdb_file_name)
            models.append(model)
            (model_number, pdb_model_lines) = parser.get_next_model_lines()
        # TODO prepare connects lines
        caveat_lines = parser.get_caveats_lines()
        extdta_lines = parser.get_expdta_lines()
        seqreq_lines = parser.get_seqres_lines()
        if len(models) == 1:
            # we will not wrap MODEL 1 ... ENMMDL lines if the orig input  did not have them
            models[0].wrap_with_header_and_footer = parser.wrap_with_header_and_footer
        return cls(models, remarks=remarks, caveats=caveat_lines, extdta=extdta_lines, seqres=seqreq_lines,
                   include_hetatm=include_hetatm)

    def __init__(self, pdb_models, remarks=None, caveats=None, extdta=None, seqres=None, **kwargs):
        super().__init__()
        if remarks is None:
            remarks = {}
        if caveats is None:
            caveats = {}
        if extdta is None:
            extdta = []
        self[0:len(pdb_models)] = list(pdb_models)
        self.remarks = remarks
        self.caveats = caveats
        self.extdta = extdta
        self.seqres = seqres
        self.file_name = None
        self.include_extdta_in__str__ = False
        self.include_remarks_in__str__ = False
        self.include_seqres_in__str__ = False

    def has_caveats(self):
        return len(self.caveats) > 1

    def get_number_of_models(self):
        return len(self)

    def reset_models_numbers(self):
        for i, model in enumerate(self, start=1):
            self[i - 1].model_number = i

    def get_models_by_numbers(self, *models_numbers):
        models = [self[model_number - 1] for model_number in models_numbers]
        return models

    def get_chain(self, model_number, chain_id):
        for mi, model in enumerate(self):
            if model_number == model.model_number:
                for ci, chain in enumerate(model):
                    if chain_id == chain.chain_id:
                        return chain
                raise RuntimeError("chain_id {} was not found in model number {}".format(chain_id, model_number))
        raise RuntimeError(" model number {} was not found in".format(model_number))

    def __str__(self):
        s = ""
        chomp = lambda s: s.rstrip('\n')
        if self.include_extdta_in__str__:
            s += "\n".join(map(chomp, self.extdta))
            s += "\n"
        if self.include_remarks_in__str__:
            s += str(self.remarks)
        if self.include_seqres_in__str__:
            s += "\n".join(list(map(chomp, self.seqres)))
            s += "\n"

        s += "\n".join(map(str, self)) + "\n" + pdb_constants().END + "\n"
        return s

    def info(self):
        info = {
            "number_of_models": len(self),
            "number_of_remarks": len(self.remarks),
            "models_info": list(map(pdb_model.info, self))
        }
        if self.file_name:
            info["file_name"] = self.file_name
        return info

    def get_resseq_as_chaindict(self):
        seq = self.seqres
        chain_dict = dict([(l[11], []) for l in seq])
        for c in chain_dict.keys():
            chain_seq = [l[19:70].split() for l in seq if l[11] == c]
            for x in chain_seq:
                chain_dict[c].extend(x)
        return chain_dict


"""





sub set_rama_type_of_atom {
sub set_rama_type_of_peptide {
sub set_gaps_in_data {
sub gaps_report_text{
sub pdb_stracture_has_gaps{
sub validate_atom {
sub _mark_resgaps {
sub get_number_of_models{
sub get_number_of_peptides{

sub get_peptide_by_number{
sub get_model_by_number{

sub get_connect_by_number{
sub get_peptide_chain_id{

sub get_next_model {
sub get_ter_line {
sub create_ter_line {

sub which_resname{
sub which_resseq{

sub peptides_list2pdb {
sub atoms_list2pdb {
sub atoms_list2xyz{
"""
