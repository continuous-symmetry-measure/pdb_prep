from Utils.inform import inform
from version import __VERSION__


class xray_inform(inform):

    def __init__(self, cliutils, is_verbose=True, include_hetatm=False, ignore_remarks=[], bio_molecule_chains=None):
        super().__init__(cliutils, is_verbose, include_hetatm, ignore_remarks, bio_molecule_chains)
        self.exprimental_method = "XRAY"

    def __str__(self):
        s = "pdb_prep Version: {}\n".format(__VERSION__)
        if len(self.reliable_data) >= 1:
            s += "\nReliable:\n"
            s += self._str_data(self.reliable_data, "Reliable_data")
        if len(self.reliable_R_grade_data) >= 1:
            s += "\nReliable_r_grade:\n"
            s += self._str_data(self.reliable_R_grade_data, "reliable_R_grade_data")

        files = list(self.reliable_data.keys())
        files.extend(list(self.reliable_R_grade_data.keys()))
        if len(set(self.excluded_files.keys()) - set(files)) >= 1:
            s += "\nExcluded_files:\n"
            s += self._str_excluded(files)
            files.extend(self.excluded_files.keys())

        if len(set(self.others_data) - set(files)) >= 1:
            s += "\nOthers:\n"
            s += self._str_data(self.others_data, "others_data", dont_include_files=files)

        return s

    def filter_data(self, max_resolution, limit_r_free_grade=None, click=None, test_is_homomer=False):
        """
         for each file:
            if (Resolution  == NULL) then                     file is unreliable
            if (Resolution  <1.0) then                        file is reliable_R_grade
            if (1.0<=Resolution  max_resolution) then
                    if R_free_grade == 'NULL' then            file is reliable_R_grade
                    if R_free_grade>= limit_r_free_grade then file is reliable
                    else                                      file is unreliable

        :param max_resolution:
        :param limit_r_free_grade:
        """
        self.reliable_data, self.others_data, self.reliable_R_grade_data = {}, {}, {}
        #  output_data_config:
        #  this list will contain the info about the outputs directories
        #  (dirname,data,copy_or_clean)
        #
        cliutils = self.cliutils
        self.output_data_config = [
            # the order of this list is importent also for the clean_tmp_* funtions
            ("reliable_r_grades", self.reliable_R_grade_data, "clean"),
            ("reliable", self.reliable_data, "clean"),
            ("others", self.others_data, "copy"),
        ]

        remark_350_warn_msg_flag = True
        for fi, k in enumerate(self.data):
            file, pdbinfo = k, self.data[k]
            try:
                if test_is_homomer and pdbinfo.is_homomer(cliutils.is_verbose):
                    self.cliutils.verbose("{} is homomer as expected".format(file))
                    pass
                elif test_is_homomer and not pdbinfo.is_homomer():
                    raise ValueError("Expected homomer but got heteromer")
                # cliutils.write_a_file(full_path, str(_pdb))

                if not pdbinfo.Resolution or pdbinfo.Resolution == "NULL":
                    msg = "'{}' - Resolution='NULL'".format(file)
                    self.verbose(msg)
                    self.excluded_files[file] = msg
                    self.others_data[file] = pdbinfo
                    continue
                ignore_rem350 = 350 in self.ignore_remarks
                is_file_mode = self.one_file_mode
                is_dir_mode = not self.one_file_mode
                if is_dir_mode and not ignore_rem350:
                    if not pdbinfo.bio_struct_identical_to_the_asymmetric_unit:
                        msg = "File: '{}' - The given peptides structure does not create a biomolecule. ({})"
                        msg = msg.format(file, pdbinfo.bio_struct_msg)
                        self.verbose(msg)
                        self.excluded_files[file] = msg
                        self.others_data[file] = pdbinfo
                        continue
                elif is_file_mode and not ignore_rem350:
                    if not pdbinfo.bio_struct_identical_to_the_asymmetric_unit:
                        msg = "File: '{}' - The given peptides structure does not create a biomolecule. ({})"
                        msg = msg.format(file, pdbinfo.bio_struct_msg)
                        cliutils.warn_msg(msg, caller=type(self).__name__)
                        pdbinfo.warning_msg = msg

                if remark_350_warn_msg_flag and ignore_rem350:
                    msg = "remark 350 was ignored"
                    cliutils.msg(msg, caller=type(self).__name__)
                    remark_350_warn_msg_flag = False

                current_resolution = float(pdbinfo.Resolution)
                min_r_free_key = float(min(pdbinfo.r_free_dict.keys()))
                if is_file_mode:
                    # on one file mode we should ignore r_free value and resolution
                    self.reliable_data[file] = pdbinfo
                    continue

                # if current_resolution <= min_r_free_key:
                if current_resolution < min_r_free_key:
                    self.reliable_data[file] = pdbinfo
                    continue

                if current_resolution <= max_resolution:
                    if str(pdbinfo.R_free_grade) == 'NULL':
                        self.reliable_R_grade_data[file] = pdbinfo
                    elif pdbinfo.R_free_grade >= limit_r_free_grade:
                        self.reliable_data[file] = pdbinfo
                    else:
                        msg = "File: '{}' - R_free_grade='{}'  worse than limit_R_free_grade='{}'".format(
                            file, pdbinfo.R_free_grade, limit_r_free_grade, current_resolution, max_resolution)
                        self.verbose(msg)
                        self.excluded_files[file] = msg
                        self.others_data[file] = pdbinfo
                    continue

                if current_resolution > max_resolution:
                    msg = "File: '{}' - File resolution is worse than " \
                          "requested  (current_resolution={} > max_resolution={})".format(file, current_resolution,
                                                                                          max_resolution)
                    self.verbose(msg)
                    self.excluded_files[file] = msg
                    self.others_data[file] = pdbinfo
                    continue

            except Exception as e:
                msg = "File: '{}' - {}".format(file, e)
                self.cliutils.error_msg(msg, type(self).__name__)
                self.excluded_files[file] = msg
                self.others_data[file] = pdbinfo


class nmr_inform(inform):
    def __init__(self, cliutils, is_verbose=True, include_hetatm=False, ignore_remarks=[], bio_molecule_chains=None):
        super().__init__(cliutils, is_verbose, include_hetatm, ignore_remarks, bio_molecule_chains)
        self.exprimental_method = "NMR"

    def __str__(self):
        s = "pdb_prep Version: {}\n".format(__VERSION__)
        s += "\nnmr:\n"
        s += self._str_data(self.nmr_data, "Reliable_data")
        return s

    def _str_data(self, data, data_name="Reliable_data"):
        format_string = "{0:<25} {1:<26}\n"
        s = ""
        self.json_dict["pdb_prep Version"] = __VERSION__
        self.json_dict[data_name] = {}
        #                          0      1
        s += format_string.format("file", "forms_a_biomolecule")

        for file, info in sorted(data.items(), key=lambda t: t[0]):
            try:
                bios = self._bios_value(info)
                # 0     1
                s += format_string.format(file, bios)
                self.json_dict[data_name][file] = {"Forms_a_biomolecule": bios,
                                                   "Exprimental_method": self.exprimental_method}
                if info.warning_msg:
                    self.json_dict[data_name][file]["Warning"] = info.warning_msg

            except:
                s += "{}\n".format(file)
                self.json_dict[data_name][file] = None

        if len(self.excluded_files) >= 1:
            data_name = "excluded"
            self.json_dict[data_name] = {}
            files = []
            if len(set(self.excluded_files.keys())) >= 1:
                s += "\nexcluded_files:\n"
                s += self._str_excluded(files)
            s += "\nothers:\n"
            for file in self.others_data:
                if file not in self.excluded_files:
                    s += "{}\n".format(file)
                    self.json_dict[data_name][file] = None

        return s

    def filter_data(self, click=None, test_is_homomer=False):
        """
         for each file:
            if (is_nmr ) then                     file is nmr
        """
        self.nmr_data, self.others_data = {}, {}
        self.output_data_config = [
            ("nmr", self.nmr_data, "clean"),
            ("others", self.others_data, "copy"),
        ]

        for fi, k in enumerate(self.data):
            file, pdbinfo = k, self.data[k]
            try:
                if test_is_homomer and pdbinfo.is_homomer():
                    self.cliutils.verbose("{} is homomer as expected".format(file))
                    pass
                elif test_is_homomer and not pdbinfo.is_homomer():
                    # self.cliutils.error_msg("{} is not homomer".format(file))
                    raise ValueError("Expected homomer but got heteromer")
                # cliutils.write_a_file(full_path, str(_pdb))

                if pdbinfo.is_nmr():
                    self.verbose("'{}' - NMR")
                    if pdbinfo.bio_struct_identical_to_the_asymmetric_unit:
                        self.nmr_data[file] = pdbinfo
                    else:
                        ignore_rem350 = 350 in self.ignore_remarks
                        is_file_mode = self.one_file_mode
                        is_dir_mode = not self.one_file_mode
                        if is_dir_mode and not ignore_rem350:
                            msg = "File: '{}' - The given peptides structure does not create a biomolecule. ({})"
                            msg = msg.format(file, pdbinfo.bio_struct_msg)
                            self.cliutils.error_msg(msg, type(self).__name__)
                            self.excluded_files[file] = msg
                            self.others_data[file] = pdbinfo
                            continue
                        elif is_dir_mode and ignore_rem350:
                            # if bio_struct_identical_to_the_asymmetric_unit=False
                            #    and  this is_dir_mode
                            #    and  ignore_rem350
                            msg = "File: '{}' - The given peptides structure does not create a biomolecule. ({})"
                            msg = msg.format(file, pdbinfo.bio_struct_msg)
                            self.cliutils.error_msg(msg, type(self).__name__)
                            self.excluded_files[file] = msg
                            self.others_data[file] = pdbinfo
                        elif is_file_mode and not ignore_rem350:
                            msg = "File: '{}' - The given peptides structure does not create a biomolecule. ({})"
                            msg = msg.format(file, pdbinfo.bio_struct_msg)
                            self.cliutils.warn_msg(msg, caller=type(self).__name__)
                            pdbinfo.warning_msg = msg
                            self.nmr_data[file] = pdbinfo
                else:
                    self.others_data[file] = pdbinfo
            except Exception as e:
                msg = "File: '{}' - {}".format(file, e)
                self.cliutils.error_msg(msg, type(self).__name__)
                self.excluded_files[file] = msg
                self.others_data[file] = pdbinfo
