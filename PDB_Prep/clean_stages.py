import functools
import multiprocessing
import os
import time

from Chemistry.PDB.Sievers import atom_hydrogen_siever
from Chemistry.PDB.pdb_atom import pdb_atom
from Chemistry.PDB.pdb_utils import pdb_utils, pdb_info
from Utils.cli_utils import cli_utils


def write_a_file(file_info, cliutils):
    file_path, file_data = file_info[0], file_info[1]
    try:
        rv = cliutils.write_file(file_path, str(file_data))
        print(".", flush=True, end='')
    except Exception as e:
        cliutils.error_msg("{} - {}".format(e, file_path))
    return rv


def write_files(files_dict, is_verbose):
    if len(files_dict) == 1:
        cliutils = cli_utils(None, is_verbose, "write_files")
        result = write_a_file(list(files_dict.items())[0], cliutils)
        return [result]

    with multiprocessing.Pool() as p:
        start_time = time.time()
        cliutils = cli_utils(None, is_verbose, "write_files")
        results = list(p.map(functools.partial(write_a_file, cliutils=cliutils), files_dict.items()))
        cliutils.verbose("pdbinfo_iter execution time = {0:.5f}".format(time.time() - start_time), caller="write_files")
        return results


class stages():
    def __init__(self, cliutils, informer, is_homomer):
        self.cliutils = cliutils
        self.informer = informer
        self.current_dest_path = ""
        self.other_data = []
        self.last_stage_dir = None
        self.stages_dirs_list = []
        self.is_homomer = is_homomer

    def set_dest_path(self, directory):
        self.current_dest_path = os.path.join(os.getcwd(), self.cliutils.output_dirname, directory)
        return self.current_dest_path

    def _change_stages_last_dir(self, dest_path, stage_dir_name):
        self.last_stage_dir = os.path.join(dest_path, stage_dir_name)
        self.stages_dirs_list.append(self.last_stage_dir)
        return self.last_stage_dir

    def handle_file_with_unexpected_errors(self, file_name, file_delete, info, exeption, caller):
        cliutils = self.cliutils
        msg = "file:'{}' Error: {}  = I will write the file in others dir".format(file_name, exeption)
        print("\n")
        cliutils.error_msg(msg, caller)
        others_dir = self.set_dest_path('others')
        cliutils.mkdir(dirname=others_dir, raise_error_if_exists=False)
        rv = cliutils.write_file(os.path.join(others_dir, file_name), str(info._pdb))
        self.other_data.append(file_name)
        if os.path.isfile(file_delete):  # just to make sure
            cliutils.delete_file(file_delete)

        return rv

    def clean_01_into_dir(self, dest_path, data, with_hydrogens, ignore_remarks=[]):
        """
        for  each pdb:
            atom_hydrogen_siever
            clean_alternate_location
            copy  into 01_without_gaps_handling after
        :param dest_path:
        :param data:
        :param cliutils:
        :return:
        """
        _caller = self.clean_01_into_dir.__name__

        cliutils = self.cliutils
        _dest_path = self._change_stages_last_dir(dest_path, "01_without_gaps_handling")

        rv = cliutils.mkdir(dirname=_dest_path)
        if cliutils.is_verbose:
            print("\n")
        cliutils.verbose("start stage 01 clean data into  {} ( excpecting {} items).".format(_dest_path, len(data)),
                         caller=_caller)
        _data = data
        if len(_data.items()) == 0:
            cliutils.verbose("end  stage 01 clean data {} ( no data ).".format(_dest_path), caller=_caller)
            return _dest_path, _data
        h_siever = atom_hydrogen_siever()
        bs = 0
        files_to_write = {}
        for fi, itm in enumerate(sorted(_data.items())):
            file_name, info = itm
            full_path = os.path.join(_dest_path, file_name)
            try:
                # bs = fi
                # bar.update(bs)
                _pdb = pdb_utils.clean_alternate_location(info._pdb)
                if not with_hydrogens:
                    _pdb = h_siever.sieve(_pdb)
                _pdb.include_remarks_in__str__ = True
                _pdb.include_extdta_in__str__ = True
                files_to_write[full_path] = str(_pdb)
                # cliutils.write_a_file(full_path, str(_pdb))

                _pdb_info = pdb_info(_pdb, ignore_remarks=ignore_remarks)
                report = "# {}\n".format(_caller)
                report += _pdb_info.info_report()
                data[file_name] = _pdb_info
            except Exception as e:
                file_delete = full_path
                del (data[file_name])
                self.handle_file_with_unexpected_errors(file_name, file_delete, info, e, _caller)

        write_files(files_dict=files_to_write, is_verbose=self.cliutils.is_verbose)
        # bar.update(bs + 1)
        cliutils.verbose("end  stage 01 clean data into  {} ( excpecting {} items).\n".format(_dest_path, len(data)),
                         caller=_caller)

        return _dest_path, data, report

    def get_02_missing_resseqs_per_chain_id(self, info):
        missing_residues_per_chain_id = {}
        try:
            info.parse_remark_465()
            for data in info.missing_residues:
                chain_id = data["chain_id"]
                resseq = data["resseq"]
                missing_residues_per_chain_id.setdefault(chain_id, []).append(resseq)
        except Exception as e:
            pass

        return missing_residues_per_chain_id

    def clean_02_missing_resseqs_found_in_remarks(self, dest_path, data, ignore_remarks=[]):
        """
        this function cleans the missing resseqs we found remark 365
        """
        _caller = "02-missing_resseqs-remarks"
        cliutils = self.cliutils
        _dest_path = self._change_stages_last_dir(dest_path, "02_missing_resseqs_found_in_remarks")
        _data = data
        if cliutils.is_verbose:
            print("\n")
        cliutils.verbose(
            "start stage 02-missing_resseqs-remarks {} ( excpecting {} items).".format(_dest_path, len(data)),
            caller=_caller)
        if len(_data.items()) == 0:
            cliutils.msg("end  02-missing_resseqs-remarks {} ( no data ).".format(_dest_path), caller=_caller)
            return _dest_path, _data
        rv = cliutils.mkdir(dirname=_dest_path)

        files_to_write = {}
        for fi, itm in enumerate(sorted(_data.items()), 1):
            # bs = fi
            # bar.update(bs)

            file_name, info = itm
            full_path = os.path.join(_dest_path, file_name)
            try:

                _pdb = info._pdb
                _pdb.include_remarks_in__str__ = True
                _pdb.include_extdta_in__str__ = True
                missing_residues_per_chain_id = self.get_02_missing_resseqs_per_chain_id(info)
                s = str(_pdb)
                _pdb = pdb_utils.remove_residues_from_every_chain(missing_residues_per_chain_id, _pdb)
                _pdb_info = pdb_info(_pdb, ignore_remarks=ignore_remarks)
                report = "# {}\n".format(_caller)
                report += _pdb_info.info_report()

                s = str(_pdb)
                _pdb.include_remarks_in__str__ = True
                _pdb.include_extdta_in__str__ = True
                files_to_write[full_path] = str(_pdb)
                _data[file_name] = _pdb_info
                # cliutils.write_file(full_path, str(_pdb))
            except Exception as e:
                file_delete = full_path
                del (_data[file_name])
                self.handle_file_with_unexpected_errors(file_name, file_delete, info, e, _caller)
                continue
        write_files(files_dict=files_to_write, is_verbose=self.cliutils.is_verbose)
        # bar.update(bs)
        cliutils.verbose(
            "end  stage 02-missing_resseqs-remarks {} ( excpecting {} items).\n".format(_dest_path, len(data)),
            caller=_caller)

        return _dest_path, _data, report

    def clean_03_fix_resseqs(self, dest_path, data):
        _caller = "03-fix_resseqs"
        _dest_path = self._change_stages_last_dir(dest_path, "03_fix_resseqs")
        _data = data
        cliutils = self.cliutils
        cliutils.verbose("end  stage {} {} TODO: (was not iplemented).\n".format(_caller, _dest_path, len(data)),
                         caller=_caller)
        return _dest_path, _data

    def get_04_missing_atoms_per_chain_id(self, info):
        missing_atoms_per_chain_id = {}
        try:
            info.parse_remark_470()
            for data in info.missing_atoms:
                # data = { "resname": resname,"chain_id": chian_id,"resseq": resseq, "atom_names": [atom_name,atom_name...]}
                chain_id = data["chain_id"]
                missing_atoms_per_chain_id.setdefault(chain_id, []).append(data)
        except Exception as e:
            pass
        return missing_atoms_per_chain_id

    def is_04_missing_atom(self, atom, missing_atoms_per_chain_id):
        for chain_id, chain_data in missing_atoms_per_chain_id.items():
            for data_item in chain_data:
                reseeq = data_item["resseq"]
                for atom_name in data_item["atom_names"]:
                    if (atom.resseq, atom.atom_name) == (reseeq, atom_name):
                        return True
        return False

    def clean_04_missing_atoms_found_in_remarks(self, dest_path, data, ignore_remarks=[]):
        """
        this function cleans the missing atoms we found remark 365
        """

        _caller = "04-missing_atoms-remarks"
        _dest_path = self._change_stages_last_dir(dest_path, "04_missing_atoms_found_in_remarks")
        self.last_stage_dir = _dest_path
        _data = data
        cliutils = self.cliutils
        cliutils.verbose("start stage {} {} ( excpecting {} items).".format(_caller, _dest_path, len(data)),
                         caller=_caller)
        if len(_data.items()) == 0:
            cliutils.msg("end  stage {} {} ( no data ).".format(_caller, _dest_path), caller=_caller)
            return _dest_path, _data
        rv = cliutils.mkdir(dirname=_dest_path)
        files_to_write = {}
        for fi, itm in enumerate(sorted(_data.items())):
            file_name, info = itm
            full_path = os.path.join(_dest_path, file_name)
            try:
                # bs = fi
                # bar.update(bs)

                _pdb = info._pdb
                _pdb.include_remarks_in__str__ = True
                _pdb.include_extdta_in__str__ = True

                missing_atoms_per_chain_id = self.get_04_missing_atoms_per_chain_id(info)
                if len(missing_atoms_per_chain_id) == 0:
                    _pdb.include_remarks_in__str__ = True
                    _pdb.include_extdta_in__str__ = True
                    files_to_write[full_path] = str(_pdb)
                    # cliutils.write_file(full_path, str(_pdb))
                    continue
                missing_residues_per_chain_id = {}
                atoms_to_remove = []
                # missing_atoms_per_chain_id: { chain_id : [(resseq,atom_name)(resseq,atom_name)...], ...}

                for mi, model in enumerate(_pdb):
                    for ci, chain in enumerate(model):
                        for ai, atom in enumerate(chain):
                            if self.is_04_missing_atom(atom, missing_atoms_per_chain_id):
                                if pdb_atom.is_backbone(atom.atom_name):
                                    missing_residues_per_chain_id.setdefault(atom.chain_id, []).append(atom.resseq)
                                elif atom.resseq not in missing_residues_per_chain_id:
                                    atoms_to_remove.append((atom.resname, atom.resseq, atom.atom_name))
                # print (atoms_to_remove)
                _pdb = pdb_utils.remove_atoms_from_every_chain(atoms_to_remove, _pdb)
                _pdb = pdb_utils.remove_residues_from_every_chain(missing_residues_per_chain_id, _pdb)

                _pdb_info = pdb_info(_pdb, ignore_remarks=ignore_remarks)
                report = "# {}\n".format(_caller)
                report += _pdb_info.info_report()

                _pdb.include_remarks_in__str__ = True
                _pdb.include_extdta_in__str__ = True
                files_to_write[full_path] = str(_pdb)
                _data[file_name] = _pdb_info
                # cliutils.write_file(full_path, str(_pdb))
            except Exception as e:
                file_delete = full_path
                del (_data[file_name])
                self.handle_file_with_unexpected_errors(file_name, file_delete, info, e, _caller)
                continue
        write_files(files_dict=files_to_write, is_verbose=self.cliutils.is_verbose)
        # bar.update(bs + 1)

        cliutils.verbose("end  stage {} {} ( excpecting {} items).\n".format(_caller, _dest_path, len(data)),
                         caller=_caller)
        return _dest_path, _data

    def clean_05_all_chains_has_same_number_of_atoms(self, dest_path, data, ignore_remarks=[],informer=None):
        """
        move to 05 dir only if each model chains has same number of atoms
        :param dest_path:
        :param data:
        :param cliutils:
        :return:
        """
        _caller = "05-all_chains_has_same_number_of_atoms"
        _dest_path = self._change_stages_last_dir(dest_path, "05_all_chains_has_same_number_of_atoms")
        _data = data
        cliutils = self.cliutils
        print("")
        cliutils.verbose("start stage {} {} ( excpecting {} items).".format(_caller, _dest_path, len(data)),
                         caller=_caller)
        if len(_data.items()) == 0:
            cliutils.verbose("end  stage {} {} ( no data ).".format(_caller, _dest_path), caller=_caller)
            return _dest_path, _data
        rv = cliutils.mkdir(dirname=_dest_path)

        files_to_write = {}
        for fi, itm in enumerate(sorted(_data.items())):
            file_name, info = itm
            full_path = os.path.join(_dest_path, file_name)
            try:
                # bs = fi
                # bar.update(bs)

                _pdb = info._pdb
                _pdb.include_remarks_in__str__ = True
                _pdb.include_extdta_in__str__ = True
                is_ok = True
                for mi, model in enumerate(_pdb):
                    first_chain_len = len(model[0])
                    for ci, chain in enumerate(model):
                        if len(chain) != first_chain_len:
                            is_ok = False
                            informer.exluded_files[_pdb.file_name]="not hommomer"
                            break
                    if is_ok:
                        continue
                    else:
                        break
                if is_ok:
                    _pdb.include_remarks_in__str__ = True
                    _pdb.include_extdta_in__str__ = True
                    files_to_write[full_path] = str(_pdb)
                    # cliutils.write_file(full_path, str(_pdb))
            except Exception as e:
                file_delete = full_path
                del (_data[file_name])
                self.handle_file_with_unexpected_errors(file_name, file_delete, info, e, _caller)
                continue
        write_files(files_dict=files_to_write, is_verbose=self.cliutils.is_verbose)
        # bar.update(bs + 1)
        cliutils.verbose("end  stage {} {} ( excpecting {} items).\n".format(_caller, _dest_path, len(data)),
                         caller=_caller)
        return _dest_path, _data

    def run_clean_stages(self, directory, dest_path, data, with_hydrogens, ignore_remarks=[],informer=None):
        _caller = "run_clean_stages"
        _dest_path, _data = dest_path, data
        cliutils = self.cliutils
        cliutils.verbose("directory: '{}'".format(directory))
        total_report = ""
        # ------------------------------------------------------------
        # 01_without_gaps_handling
        _dest_path, _data, report = self.clean_01_into_dir(dest_path, _data, with_hydrogens, ignore_remarks)
        total_report += "\n{}\n".format(report)

        # ------------------------------------------------------------
        # 02-missing_resseqs-remarks
        _dest_path, _data, report = self.clean_02_missing_resseqs_found_in_remarks(dest_path, _data, ignore_remarks)
        total_report += "\n{}\n".format(report)

        # ------------------------------------------------------------
        # 02-fix_resseqs
        _dest_path, _data = self.clean_03_fix_resseqs(dest_path, _data)
        total_report += "\n{}\n".format(report)

        # ------------------------------------------------------------
        # 04-missing_atoms-remarks"
        _dest_path, _data = self.clean_04_missing_atoms_found_in_remarks(dest_path, _data, ignore_remarks)
        if not self.is_homomer:
            self.cliutils.msg("This is hetromer so I will skip on stage '05_all_chains_has_same_number_of_atoms'")
            return _data
        # ------------------------------------------------------------
        # 05-missing_atoms-remarks"
        _dest_path, _data = self.clean_05_all_chains_has_same_number_of_atoms(dest_path, _data, ignore_remarks,informer)
        return _data, total_report
