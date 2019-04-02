from Utils.inform import inform


class xray_inform(inform):
    def __str__(self):
        s = ""
        if len(self.reliable_data) >= 1:
            s += "\nreliable:\n"
            s += self._str_data(self.reliable_data)
        if len(self.reliable_R_grade_data) >= 1:
            s += "\nreliable_r_grade:\n"
            s += self._str_data(self.reliable_R_grade_data)
        if len(self.others_data) >= 1:
            s += "\nothers:\n"
            s += self._str_data(self.others_data)
        return s

    def filter_data(self, max_resolution, limit_r_free_grade=None, click=None):
        """
         for each file:
            if (Resolution  == NULL) then                     file is unreliable
            if (Resolution  <1.0) then                        file is reliable_R_grade
            if (1.0<=Resolution  max_resolution) then
                    if R_free_grade == 'NULL' then            file is reliable_R_grade
                    if R_free_grade>= limit_r_free_grade then file is  reliable
                    else                                      file is unreliable

        :param max_resolution:
        :param limit_r_free_grade:
        """
        self.reliable_data, self.others_data, self.reliable_R_grade_data = {}, {}, {}
        #  output_data_config:
        #  this list will contain the info about the outputs directories
        #  (dirname,data,copy_or_clean)
        #
        self.output_data_config = [
            ("reliable", self.reliable_data, "clean"),
            ("reliable_r_grades", self.reliable_R_grade_data, "clean"),
            ("others", self.others_data, "copy"),
        ]

        for fi, k in enumerate(self.data):
            file, pdbinfo = k, self.data[k]
            try:

                # bar.update(fi + 1)
                if not pdbinfo.Resolution or pdbinfo.Resolution == "NULL":
                    self.verbose("file: '{}' - Resolution='NULL'".format(file))
                    self.others_data[file] = pdbinfo
                    continue
                if 350 not in self.ignore_remarks:
                    if not pdbinfo.bio_struct_identical_to_the_asymmetric_unit:
                        self.verbose(
                            "file: '{}' - biological structure  IS NOT identical to the asymmetric unit".format(file))
                        self.others_data[file] = pdbinfo
                        continue
                else:
                    msg="remark 350 was ignored so bio_struct_identical_to_the_asymmetric_unit was not checked"
                    print("WARN:file: '{}' - {}".format(file,msg))

                current_resolution = float(pdbinfo.Resolution)
                min_r_free_key = float(min(pdbinfo.r_free_dict.keys()))
                if current_resolution <= min_r_free_key:
                    self.reliable_data[file] = pdbinfo
                    continue

                if current_resolution <= max_resolution:
                    if str(pdbinfo.R_free_grade) == 'NULL':
                        self.reliable_R_grade_data[file] = pdbinfo
                    elif pdbinfo.R_free_grade >= limit_r_free_grade:
                        self.reliable_data[file] = pdbinfo
                    else:
                        self.verbose(
                            "file: {} 'current_resolution <= max_resolution ({}<={})".format(
                                file,current_resolution , max_resolution))
                        self.others_data[file] = pdbinfo
                    continue

                if current_resolution > max_resolution:
                    self.verbose(
                        "file: {} 'current_resolution > max_resolution ({}>{})".format(
                            file, current_resolution, max_resolution))
                    self.others_data[file] = pdbinfo
                    continue

            except Exception as e:
                self.cliutils.error_msg("file {} - {}".format(file, e), self.__class__.__name__)
                self.others_data[file] = pdbinfo


class nmr_inform(inform):
    def __str__(self):
        s = ""
        s += "\nnmr:\n"
        s += self._str_data(self.nmr_data)
        return s

    def _str_data(self, data):
        format_string = "{0:<25} {1:<26}\n"
        s = ""
        #                          0      1
        s += format_string.format("file", "identical_to_the_asym_unit")

        # t=(file,info)
        for file, info in sorted(data.items(), key=lambda t: t[0]):
            try:
                bios = info.bio_struct_identical_to_the_asymmetric_unit
                if bios is None:
                    bios = "None"
                elif bios:
                    bios = "True"
                else:
                    bios = "False"
                # 0     1
                s += format_string.format(file, bios)
            except:
                s += "{}\n".format(file)

        return s

    def filter_data(self, click=None):
        """
         for each file:
            if (is_nmr ) then                     file is nmr
        """
        self.nmr_data, self.others_data = {}, {}
        self.output_data_config = [
            ("NMR", self.nmr_data, "clean"),
            ("others", self.others_data, "copy"),
        ]

        for fi, k in enumerate(self.data):
            file, pdbinfo = k, self.data[k]
            try:

                if pdbinfo.is_nmr():
                    self.verbose("file: '{}' - NMR")
                    if pdbinfo.bio_struct_identical_to_the_asymmetric_unit:
                        self.nmr_data[file] = pdbinfo
                    else:
                        self.verbose(
                            "file: '{}' - biological structure  IS NOT identical to the asymmetric unit".format(file))
                        self.others_data[file] = pdbinfo
                        continue
                else:
                    self.others_data[file] = pdbinfo
            except Exception as e:
                self.cliutils.error_msg("file {} - {}".format(file, e), self.__class__.__name__)
                self.others_data[file] = pdbinfo
