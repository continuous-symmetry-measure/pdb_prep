import json
import os

import click

from PDB_Prep.clean_stages import stages
from Utils.cli_utils import cli_utils as cu


def copy_data_into_dir(source_path, dest_path, data, cliutils):
    """
    this function will be use to copy file which we dont wanr to process
    :param source_path:
    :param dest_path:
    :param data: dict of file_name: pdb_info object
    :param cliutils:
    :return:
    """
    cliutils.verbose("start copy data into  {} ( excpecting {} items).".format(dest_path, len(data)),
                     caller=copy_data_into_dir.__name__)
    rv = cliutils.copyfiles_to_dir(source_path, dest_path, files_list=sorted(data.keys()))
    return rv


def clean_tmp_data(stager: stages, pdb_dir, short_file_name, informer, cliutils):
    if stager.last_stage_dir is None:
        cliutils.error_msg("exluded_files:\n{}".format(informer.exluded_files))
        cliutils.error_msg("file is not valid - check the 'others' dir", caller=clean_tmp_data.__name__)
        exit(22)
    last_stage_full_file_name = os.path.join(stager.last_stage_dir, short_file_name)
    tmp = os.path.splitext(short_file_name)
    out_file_name = os.path.join(pdb_dir, tmp[0] + ".clean" + tmp[1])

    print("\ncleaned file is: '{}'".format(out_file_name))
    if os.path.isfile(last_stage_full_file_name):
        cliutils.copy_file(last_stage_full_file_name, out_file_name)
    else:
        cliutils.error_msg("file:{} is not valid. try verbose mode for more info.".format(short_file_name))
    if not cliutils.is_verbose:
        # print ("remove:{}".format(cliutils.output_dirname))
        cliutils.rmtree(cliutils.output_dirname)
        # for directory, data, copy_or_clean in sorted(informer.output_data_config):
        #     if os.path.isdir(directory):
        #         cliutils.rmtree(directory)
    return


def validate_input_dir_or_file(pdb_dir, pdb_file, cliutils):
    if pdb_dir:
        cliutils.verbose("{:>20}={}".format("--pdb-dir", pdb_dir))
        if not os.path.isdir(pdb_dir):
            cliutils.exit(exit_code=1, sevirity="ERROR", msg="not pdb dir: {}".format(pdb_dir))
    if pdb_file:
        cliutils.verbose("{:>20}={}".format("--pdb_file", pdb_file))
        if not os.path.isfile(pdb_file):
            cliutils.exit(exit_code=1, sevirity="ERROR", msg="no such file: {}".format(pdb_file))

    if (pdb_dir != "." and pdb_file) or (not pdb_dir and not pdb_file):
        rv = 4
        cliutils.exit(rv, 'ERROR', "you  must use exectly one of --pdb-dir or --pdb-file")


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
        cliutils.exit(rv, 'ERROR', "could not create {} dir".format(output_dir))

    return cliutils


def nmr_validate_params(pdb_dir, pdb_file, output_dir, verbose):
    cliutils = cu(click, is_verbose=verbose)
    validate_input_dir_or_file(pdb_dir, pdb_file, cliutils)

    _output_dir = output_dir
    if output_dir == 'output.{time}':
        _output_dir = 'output'
    rv = cliutils.make_output_dir(dirname=_output_dir, with_timestamp=True)
    if rv != 0:
        cliutils.exit(rv, 'ERROR', "could not create {} dir".format(output_dir))
    return cliutils


def finish_outputs(mode_file_or_dir, informer, cliutils, report):
    if mode_file_or_dir == "file":
        print(str(informer))

        report_file = "report-{}.txt".format(list(informer.data)[0])
        report_file = os.path.join(report_file)
        cliutils.write_file(report_file, str(informer))
        print("report file:{}".format(report_file))
        if len(informer.exluded_files) > 0:
            ecxluded_file = "ecxluded-{}.json".format(list(informer.data)[0])
            ecxluded_file = os.path.join(ecxluded_file)
            cliutils.write_file(ecxluded_file, json.dumps(informer.exluded_files))
            print("ecxluded file:{}".format(ecxluded_file))

    if mode_file_or_dir == 'dir':
        cliutils.msg("output dir is: '{}'".format(cliutils.output_dirname))
        report_file = os.path.join(cliutils.output_dirname, "report.txt")
        print(str(informer))
        cliutils.write_file(report_file, str(informer))
        cliutils.verbose("{:>20}={}".format("output file", report_file))
        print("---\n")
        print(report)
    cliutils.verbose("mode_file_or_dir={}".format(mode_file_or_dir))
    cliutils.verbose("exluded_files:\n{}".format(informer.exluded_files))
    return
