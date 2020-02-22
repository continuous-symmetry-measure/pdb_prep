import fnmatch
import json
import os
import re

import click

from PDB_Prep.clean_stages import stages
from Utils.cli_utils import cli_utils as cu


def copy_data_into_dir(source_path, dest_path, data, cliutils):
    """
    This function will be use to copy file which we dont wanr to process
    :param source_path:
    :param dest_path:
    :param data: dict of file_name: pdb_info object
    :param cliutils:
    :return:
    """
    cliutils.verbose("Start copy data into  {} ( excpecting {} items).".format(dest_path, len(data)),
                     caller=copy_data_into_dir.__name__)
    rv = cliutils.copyfiles_to_dir(source_path, dest_path, files_list=sorted(data.keys()))
    return rv


def clean_tmp_data_file_mode(stager: stages, pdb_dir, short_file_name, informer, cliutils):
    if stager.last_stage_dir is None:
        cliutils.error_msg("excluded_files:{}".format(informer.excluded_files),
                           caller=clean_tmp_data_file_mode.__name__)
        cliutils.error_msg("File is not valid - check the 'others' dir", caller=clean_tmp_data_file_mode.__name__)
        # exit(22)
    else:
        last_stage_full_file_name = os.path.join(stager.last_stage_dir, short_file_name)
        tmp = os.path.splitext(short_file_name)
        out_file_name = os.path.join(pdb_dir, tmp[0] + "-clean" + tmp[1])

        print("\nCleaned file is: '{}'".format(out_file_name))
        if os.path.isfile(last_stage_full_file_name):
            cliutils.copy_file(last_stage_full_file_name, out_file_name)
        else:
            cliutils.error_msg("File: '{}' is not valid. try verbose mode for more info.".format(short_file_name),
                               caller=clean_tmp_data_file_mode.__name__)
    if not cliutils.is_verbose and os.path.isdir(cliutils.output_dirname):
        cliutils.rmtree(cliutils.output_dirname)
    return


def get_path(lst, cliutils):
    return os.path.join(os.getcwd(), cliutils.output_dirname, *lst)


def clean_tmp_data_dir_mode(stager: stages, pdb_dir, informer, cliutils):
    _is_verbose = cliutils.is_verbose
    if stager.last_stage_dir is None:
        # cliutils.error_msg("excluded_files:\n{}".format(informer.excluded_files))
        cliutils.error_msg("All files are not reliable or was excluded", caller=clean_tmp_data_dir_mode.__name__)
        # exit(22)
    elif not cliutils.is_verbose:
        # 'C:\\tmp\\remark-350\\test\\output-xray-20200221-100638\\reliable_r_grades'
        rule = re.compile(fnmatch.translate("*.pdb"), re.IGNORECASE)
        has_pdbs = lambda d: len([name for name in os.listdir(d) if rule.match(name)]) > 0
        dir_path = get_path(["others"], cliutils)
        if os.path.isdir(dir_path):
            delete_tmp_dirs([dir_path], cliutils)

        # dir_path = os.path.join(os.getcwd(), cliutils.output_dirname, "reliable_r_grades")
        dir_path = get_path(["reliable_r_grades"], cliutils)
        if os.path.isdir(dir_path):
            dirs = [get_path([dir_path, dir_name], cliutils) for dir_name in os.listdir(dir_path) if
                    has_pdbs(get_path([dir_path, dir_name], cliutils))]
            copy_from_tmp_dir(dirs[-1], dir_path, cliutils)
            delete_tmp_dirs(dirs, cliutils)

        dir_path = get_path(["reliable"], cliutils)
        if os.path.isdir(dir_path):
            dirs = [get_path([dir_path, dir_name], cliutils) for dir_name in os.listdir(dir_path) if
                    has_pdbs(get_path([dir_path, dir_name], cliutils))]
            copy_from_tmp_dir(dirs[-1], dir_path, cliutils)
            delete_tmp_dirs(dirs, cliutils)

        dir_path = get_path(["NMR"], cliutils)
        if os.path.isdir(dir_path):
            dirs = [get_path([dir_path, dir_name], cliutils) for dir_name in os.listdir(dir_path) if
                    has_pdbs(get_path([dir_path, dir_name], cliutils))]
            copy_from_tmp_dir(dirs[-1], dir_path, cliutils)
            delete_tmp_dirs(dirs, cliutils)

    cliutils.is_verbose = _is_verbose


def copy_from_tmp_dir(tmp_dir_path, dest_dir, cliutils):
    rule = re.compile(fnmatch.translate("*.pdb"), re.IGNORECASE)
    files = [get_path([tmp_dir_path, name], cliutils) for name in os.listdir(tmp_dir_path) if rule.match(name)]
    print("files:{}".format(files))
    cliutils.copyfiles_to_dir(tmp_dir_path, dest_dir, files)
    # for dir_path in stager.stages_dirs_list:

    cliutils.verbose("--------------------------------------------------")
    return


def delete_tmp_dirs(dirs, cliutils):
    for dir in dirs:
        if os.path.isdir(dir):
            cliutils.rmtree(dir)


def validate_options(parse_rem350, bio_molecule_chains, ptype, cliutils):
    if bio_molecule_chains is not None and bio_molecule_chains < 1:
        cliutils.error_msg("--bio-molecule-chains is invalid {} is not natural number")
        return False
    if not parse_rem350 and bio_molecule_chains:
        cliutils.error_msg("The combination of --ignore-rem350 and --bio-molecule-chains is invalid ")
        return False
    # check on none
    if bio_molecule_chains is not None:
        if (bio_molecule_chains == 1 and ptype != 'monomer') or (bio_molecule_chains > 1 and ptype == 'monomer'):
            msg = "The combination of --ptype {}  and --bio-molecule-chains {} is invalid "
            cliutils.error_msg(msg.format(ptype, bio_molecule_chains))
            return False
    return True


def validate_input_dir_or_file(pdb_dir, pdb_file, cliutils):
    if pdb_dir:
        cliutils.verbose("{:>20}={}".format("--pdb-dir", pdb_dir))
        if not os.path.isdir(pdb_dir):
            cliutils.exit(exit_code=1, sevirity="ERROR", msg="This is not PDB dir: '{}'".format(pdb_dir))
    if pdb_file:
        cliutils.verbose("{:>20}={}".format("--pdb_file", pdb_file))
        if not os.path.isfile(pdb_file):
            cliutils.exit(exit_code=1, sevirity="ERROR", msg="No such file: '{}'".format(pdb_file))

    if (pdb_dir != "." and pdb_file) or (not pdb_dir and not pdb_file):
        rv = 4
        cliutils.exit(rv, 'ERROR', "You  must use exactly one of --pdb-dir or --pdb-file")


def xray_validate_params(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, output_dir, verbose):
    cliutils = cu(click, is_verbose=verbose)
    validate_input_dir_or_file(pdb_dir, pdb_file, cliutils)
    cliutils.verbose("{:>20}={}".format("--max-resolution", max_resolution))
    cliutils.verbose("{:>20}={}".format("--limit-r-free-grade", limit_r_free_grade))
    cliutils.verbose("{:>20}={}".format("--output-dir", output_dir))

    _output_dir = output_dir
    if output_dir == 'output.{time}':
        _output_dir = 'output'
    rv = cliutils.make_output_dir(dirname=_output_dir, with_timestamp=True)
    if rv != 0:
        cliutils.exit(rv, 'ERROR', "Dir '{}' could not be created".format(output_dir))

    return cliutils


def nmr_validate_params(pdb_dir, pdb_file, output_dir, verbose):
    cliutils = cu(click, is_verbose=verbose)
    validate_input_dir_or_file(pdb_dir, pdb_file, cliutils)

    _output_dir = output_dir
    if output_dir == 'output.{time}':
        _output_dir = 'output'
    rv = cliutils.make_output_dir(dirname=_output_dir, with_timestamp=True)
    if rv != 0:
        cliutils.exit(rv, 'ERROR', "Dir '{}' could not be created".format(output_dir))
    return cliutils


def finish_outputs(mode_file_or_dir, informer, cliutils, stager, report, output_type="text"):
    str_informer = str(informer)
    if mode_file_or_dir == "file":
        excluded_file = "excluded-{}.json".format(list(informer.data)[0])
        print(str_informer)
        excluded_file_path = os.path.join(excluded_file)
        report_file = "report-{}.{}".format(list(informer.data)[0], output_type)
        report_file = os.path.join(report_file)
        if output_type == 'text':
            output_str = str_informer
        else:
            output_str = json.dumps(informer.json_dict, indent=4, sort_keys=True)
        cliutils.write_file(report_file, output_str)
        print("report file:{}".format(report_file))
        # print(output_str)
    #        if len(informer.excluded_files) > 0:
    #            excluded_file = "excluded-{}.json".format(list(informer.data)[0])
    #            excluded_file = os.path.join(excluded_file)
    #            cliutils.write_file(excluded_file, json.dumps(informer.excluded_files))
    #            print("excluded file:{}".format(excluded_file))
    elif mode_file_or_dir == 'dir':
        excluded_file = "excluded.json".format(list(informer.data)[0])
        print("\n")
        cliutils.msg("Output dir is: '{}'".format(cliutils.output_dirname))
        report_file = os.path.join(cliutils.output_dirname, "report.txt")
        excluded_file_path = os.path.join(cliutils.output_dirname, excluded_file)
        if output_type == 'text':
            output_str = str(informer)
        else:
            output_str = json.dumps(informer.json_dict, indent=4, sort_keys=True)
        print(output_str)
        # print(informer.json_dict)
        # print(informer.excluded_files)
        # print (">>>>>>>>{}".format(report_file))
        cliutils.write_file(report_file, output_str)
        cliutils.verbose("{:>20}={}".format("output file", report_file))
    # if len(informer.excluded_files) > 0:
    #     cliutils.write_file(excluded_file_path, json.dumps(informer.excluded_files, sort_keys=True, indent=4))

    cliutils.verbose("mode_file_or_dir={}".format(mode_file_or_dir))
    cliutils.verbose("excluded_files:\n{}".format(informer.excluded_files))
    return
