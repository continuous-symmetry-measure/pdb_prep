import difflib
import functools
import multiprocessing
import os
import time

from Chemistry.PDB.pdb_chain import chain_utils
from Chemistry.PDB.pdb_obj import pdb
from Chemistry.PDB.pdb_utils import pdb_info
from version import __VERSION__


def create_pdb_info(file, dir_path, include_hetatm, ignore_remarks=[], output_type='text', bio_molecule_chains=None,
                    is_verbose=False):
    start_time = time.time()
    _file_path = os.path.join(dir_path, file)
    _pdb = pdb.from_file(_file_path, include_hetatm=include_hetatm)
    pdbinfo = pdb_info(_pdb, ignore_remarks=ignore_remarks, bio_molecule_chains=bio_molecule_chains,
                       output_type=output_type)
    if is_verbose:
        print(" create_pdb_info iter execution time = {0:.5f} ".format(time.time() - start_time))

    return pdbinfo


def get_pdb_info_iter(dir_path, files_iter, include_hetatm, ignore_remarks=[], bio_molecule_chains=None,
                      is_verbose=None):
    if len(list(files_iter)) <= 1:
        if is_verbose: print(" one file mode - not parallel")

        pdbinfo = create_pdb_info(file=files_iter[0], dir_path=dir_path, include_hetatm=include_hetatm,
                                  ignore_remarks=ignore_remarks, bio_molecule_chains=bio_molecule_chains,
                                  is_verbose=is_verbose)
        return [pdbinfo]

    with multiprocessing.Pool() as p:
        start_time = time.time()
        ft = functools.partial(create_pdb_info, dir_path=dir_path, include_hetatm=include_hetatm,
                               ignore_remarks=ignore_remarks)
        pdbinfo_iter = list(p.map(ft, files_iter))
        # pdbinfo_iter = list(
        #     p.map(functools.partial(create_pdb_info, dir_path=dir_path, include_hetatm=include_hetatm,
        #                             ignore_remarks=ignore_remarks), files_iter))
        if is_verbose:
            print("pdbinfo_iter execution time = {0:.5f} ".format(time.time() - start_time))

        return pdbinfo_iter


class inform():
    def __init__(self, cliutils, is_verbose=True, include_hetatm=False, ignore_remarks=[], bio_molecule_chains=None):
        self.data = {}
        self.cliutils = cliutils
        self.is_verbose = is_verbose
        self.include_hetatm = include_hetatm
        self.ignore_remarks = ignore_remarks
        self.bio_molecule_chains = bio_molecule_chains
        self.exprimental_method = None
        self.one_file_mode = False
        self.errors = {}
        self.excluded_files = {}
        self.is_compare_atoms = False
        self.is_compare_resname = False
        self.json_dict = {}

    def __str__(self):
        s = "pdb_prep Version: {}\n".format(__VERSION__)
        return s + self._str_data(self.data)

    def verbose(self, text):
        if not self.is_verbose:
            return
        print(text)

    def _bios_value(self, info):
        bios = info.bio_struct_identical_to_the_asymmetric_unit
        if bios is None:
            bios = "N/A"
        elif bios:
            bios = "True"
        else:
            bios = "False"
        return bios

    def _str_data(self, data, data_name="data", dont_include_files=[]):
        format_string = "{0:<25} {1:<10} {2:<19} {3:<7} {4:7} {5:7} {6:<26} {7:}\n"
        s = ""
        self.json_dict[data_name] = {}
        self.json_dict["pdb_prep Version"] = __VERSION__
        #                          0       1             2                  3          4
        s += format_string.format("File", "Resolution", "Resolution_Grade", "B_factor", "R_value",
                                  #                          5        6                           7
                                  "R_free", "Forms_a_biomolecule", "R_free_grade")
        # t=(file,info)
        for file, info in sorted(data.items(), key=lambda t: t[0]):
            if file in dont_include_files:
                continue
            try:
                bios = self._bios_value(info)
                # 0     1                2                      3             4
                s += format_string.format(file, info.Resolution, info.Resolution_Grade, info.B_factor, info.R_value,
                                          #                          5           6     7
                                          info.R_free, bios, info.R_free_grade)
                if isinstance(info.R_free_grade, str):
                    r_free_grade = info.R_free_grade
                else:
                    r_free_grade = info.R_free_grade.val
                self.json_dict[data_name][file] = {"Resolution": info.Resolution,
                                                   "Resolution_grade": info.Resolution_Grade,
                                                   "B_factor": info.B_factor,
                                                   "R_free": info.R_free,
                                                   "Forms_a_biomolecule": bios,
                                                   "R_free_grade": r_free_grade
                                                   }
                if self.exprimental_method:
                    self.json_dict[data_name][file]["Exprimental method"] = self.exprimental_method

            except Exception as e:
                s += "{} - Exception{}\n".format(file, e)
                self.json_dict[data_name][file] = None
        return s

    def _str_excluded(self, files):
        ex = self.excluded_files
        s = ""
        data_name = "excluded"
        self.json_dict[data_name] = {}

        if len(ex) == 0:
            return s
        format_string_ex = "{:<100}\n"
        # s += format_string_ex.format("reason")
        for file, reason in ex.items():
            if file not in files:
                s += format_string_ex.format(reason)
                self.json_dict[data_name][file] = reason

        return s

    def get_files_list(self, dir_path):
        return list(sorted(filter(lambda s: s.endswith('.pdb'), os.listdir(dir_path))))

    def process_complete_dir(self, dir_path, click):
        """
        getting info of complete directory of pdb files using  the _process_files_iter method
        :param dir_path:
        :param click:
        :return:
        """
        # this iss only for the size of the prograss bae
        files_iter = self.get_files_list(dir_path)
        self._process_files_iter(dir_path, files_iter, click)

    def process_one_file(self, dir_path, file_name, click):
        """
        getting info of spesific one pdb file using  the _process_files_iter method
        :param dir_path:
        :param click:
        :return:
        """
        self.one_file_mode = True
        files_iter = [file_name]
        self._process_files_iter(dir_path, files_iter, click)

    def _process_files_iter(self, dir_path, files_iter, click):
        """
        getting info of list of pdb files using  the one method
        :param dir_path:
        :param files_iter:
        :param click:
        :return:
        """
        bs = 1
        with click.progressbar(length=len(files_iter), label='collecting info on dir:{}'.format(dir_path)) as bar:
            pdbinfo_iter = get_pdb_info_iter(dir_path, files_iter, self.include_hetatm,
                                             ignore_remarks=self.ignore_remarks,
                                             bio_molecule_chains=self.bio_molecule_chains,
                                             is_verbose=self.is_verbose)
            bar.update(bs)
            # for fi, file in enumerate(files_iter):
            for fi, pdbinfo in enumerate(pdbinfo_iter, 1):
                bs = fi
                bar.update(bs)
                self.one_file(pdbinfo)

    def create_pdb_info(self, file, dir_path, output_type):
        return create_pdb_info(file, dir_path, self.include_hetatm, output_type)

    def one_file(self, pdbinfo):
        """
        updates self.data[besename of file_path] withe the pdb_info object
        on verbose print the data with more info  form the pdb itselef
        :param file_path:
        :param dir_path:
        :return:
        """
        _caller = self.__class__.__name__
        _pdb = pdbinfo._pdb
        _is_verbose = self.is_verbose
        if pdbinfo.output_type == 'json':
            self.is_verbose = False
        self.verbose('')
        self.verbose('+---------------------------------------------------')
        self.verbose('| {}'.format(os.path.basename(_pdb.file_name)))
        self.verbose('+---------------------------------------------------')
        self.is_verbose = _is_verbose
        try:
            if _pdb.has_caveats():
                self.cliutils.warn_msg("file:{} - has caveats lines!!!", caller=_caller)

            self.data[os.path.basename(_pdb.file_name)] = pdbinfo
            table_data = [["model No", "chain id", "residues", "atoms"]]
            for i, model in enumerate(_pdb, 1):

                # self.verbose("\t\tmodel No. {}:".format(model.model_number))
                for chain in model:
                    try:
                        table_data.append([model.model_number, None, None, None])
                        table_data[-1][1] = chain.chain_id
                        chaiutils = chain_utils(chain)
                        residues_list = chaiutils.chain2residues_list()
                        resnames_list = list(map(lambda r: r.resname, residues_list))
                        # self.verbose("\t\t\tchains info:{:>2}  number of residues: {}".format(chain.chain_id,
                        #                                                                       len(resnames_list)))
                        table_data[-1][2] = len(resnames_list)
                        table_data[-1][3] = len(chain)
                    except Exception as e:
                        msg = "file:{} - model {} - chain {} - {}"
                        self.cliutils.error_msg(msg.format(_pdb.file_name, model.model_number, chain.chain_id, e),
                                                caller=_caller)
                        self.errors[_pdb.file_name] = e

            self.verbose(pdbinfo.info_report(models_table_data=table_data))
        except Exception as e:
            self.cliutils.error_msg("file:{} - {}".format(_pdb.file_name, e), caller=_caller)
            self.errors[_pdb.file_name] = e
        return 1


class chains_comapre():
    @staticmethod
    def short_atom_str(atom):
        return "{:<6} {:>4}{:>1}{:>3}{:>4}".format(
            atom.record_name,
            atom.atom_name,
            atom.altloc,
            atom.resname,
            atom.resseq)

    def comapre_two_chains(self, chain_a, chain_b, is_verbose=False):
        if is_verbose:
            print("\tprepare diff data...", flush=True)
        a = list(map(chains_comapre.short_atom_str, chain_a))
        b = list(map(chains_comapre.short_atom_str, chain_b))
        if is_verbose:
            print("\tfinish prepare diff data...", flush=True)
            print("\tdiff data to html...", flush=True)
        diff = difflib.HtmlDiff().make_file(a, b, chain_a.chain_id, chain_b.chain_id)
        return diff
