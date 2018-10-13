#!/usr/bin/env python

from Chemistry.PDB.pdb_utils import *
from PDB_Prep.clean_stages import stages
from PDB_Prep.pdb_prep_inform import xray_inform, nmr_inform
from Utils.cli_utils import cli_utils as cu
import click
import os
@click.group()
def cli():
    """
    pdb preprations
    need help?
    try : pdb_prep COMMAND --help

    """
    pass


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
        cliutils.error_msg( "file is not valid - check the 'others' dir", caller=clean_tmp_data.__name__)
        exit(22)
    last_stage_full_file_name = os.path.join(stager.last_stage_dir, short_file_name)
    tmp = os.path.splitext(short_file_name)
    out_file_name = os.path.join(pdb_dir, tmp[0] + ".clean" + tmp[1])

    print ("\ncleaned file is: '{}'".format(out_file_name))
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

def  validate_input_dir_or_file(pdb_dir, pdb_file,cliutils):
    if pdb_dir:
        cliutils.verbose("{:>20}={}".format("--pdb-dir", pdb_dir))
        if not os.path.isdir(pdb_dir):
            cliutils.exit(exit_code=1, sevirity="ERROR", msg="not pdb dir: {}".format(pdb_dir))
    if pdb_file:
        cliutils.verbose("{:>20}={}".format("--pdb_file", pdb_file))
        if not os.path.isfile(pdb_file):
            cliutils.exit(exit_code=1, sevirity="ERROR", msg="no such file: {}".format(pdb_file))

    if (pdb_dir != "." and pdb_file) or (not pdb_dir and not pdb_file):
        rv=4
        cliutils.exit(rv, 'ERROR', "you  must use exectly one of --pdb-dir or --pdb-file")

def xray_validate_params(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, output_dir, verbose):
    cliutils = cu(click, is_verbose=verbose)
    validate_input_dir_or_file(pdb_dir, pdb_file,cliutils)
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

def nmr_validate_params(pdb_dir,pdb_file,  output_dir, verbose):
    cliutils = cu(click, is_verbose=verbose)
    validate_input_dir_or_file(pdb_dir, pdb_file, cliutils)

    _output_dir = output_dir
    if output_dir == 'output.{time}':
        _output_dir = 'output'
    rv = cliutils.make_output_dir(dirname=_output_dir, with_timestamp=True)
    if rv != 0:
        cliutils.exit(rv, 'ERROR', "could not create {} dir".format(output_dir))
    return cliutils

def finish_outputs(mode_file_or_dir,informer,cliutils):

    if mode_file_or_dir=="file":
        print ( str(informer))

    if mode_file_or_dir=='dir':
        cliutils.msg("output dir is: '{}'".format(cliutils.output_dirname))
        report_file = os.path.join(cliutils.output_dirname, "report.txt")
        cliutils.write_file(report_file, str(informer))
        cliutils.verbose("{:>20}={}".format("output file", report_file))
    cliutils.verbose("mode_file_or_dir={}".format(mode_file_or_dir))
    return

@cli.command()
@click.option('--pdb-dir', default='.',  help='the input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='sieve hydrogen atoms and hetatms from the files', show_default=True)
@click.option('--is-homomer/--is-heteromer', default=True,
              help='process the file as homomer or heteromer', show_default=True)
@click.option('--output-dir', default='output.{time}', help='output dir', show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def nmr (pdb_dir,pdb_file, with_hydrogens,is_homomer, output_dir, verbose):
    """
    \b
    This procedure prepares protein files in pdb format from NMR measurements for 
    a CSM calculation according to the following stage:
      1.  Removing non-coordinates lines from the atom section.
      2.  Removing ligands and solvent lines at the end of peptides.
          HETATOM lines in the middle of a peptide are retained.
      3.  Cleaning gaps in the sequence according to REMARK 470 (missing residues) 
          and REMARK 465 (missing atoms):
          a.  If a backbone atom is missing - the whole amino acid is deleted.
          b.  If a side chain atom is missing – the side chain is removed.
          c.  For homomers – gap on one peptide causes the removal of the related 
              atoms from all other peptides.
      4.  Retaining the first location in cases of alternate location.
      5.  Removing hydrogen atoms (optional).
      6.  Ignoring pdb files for which the asymmetric unit does not represent a 
          biological structure (e.g., non unit matrix in REMARK 350).
      7.  For homomers, checking that all peptides are of the same length.
    """
    cliutils = nmr_validate_params(pdb_dir=pdb_dir,pdb_file=pdb_file, output_dir=output_dir, verbose=verbose)
    informer = nmr_inform(cliutils, is_verbose=verbose, include_hetatm=True)
    mode_file_or_dir=None
    short_file_name=None
    if pdb_file:
        mode_file_or_dir="file"
        pdb_dir,short_file_name=os.path.split(pdb_file)
        informer.process_one_file(pdb_dir,short_file_name, click)
    elif pdb_dir:
        mode_file_or_dir="dir"
        informer.process_complete_dir(pdb_dir, click)


    informer.filter_data(click=click)
    stager = stages(cliutils, informer, is_homomer=is_homomer)
    for directory, data, copy_or_clean in sorted(informer.output_data_config):
        if len(data) == 0:
            cliutils.verbose("{} - no items to process - I will continue".format(directory))
            continue
        dest_path = stager.set_dest_path(directory)
        rv = cliutils.mkdir(dirname=dest_path)
        if rv != 0:
            cliutils.exit(rv, 'ERROR', "could not mkdir {} retval is {} ".format(directory, rv))
        if copy_or_clean == 'copy':
            copy_data_into_dir(source_path=pdb_dir, dest_path=dest_path, data=data, cliutils=cliutils)
        else:
            informer.data = stager.run_clean_stages(
                                             directory=directory,
                                             dest_path=dest_path,
                                             data=data,
                                             with_hydrogens=with_hydrogens
                                             )



    if mode_file_or_dir=="file":
        clean_tmp_data(stager,pdb_dir, short_file_name, informer, cliutils)
    finish_outputs(mode_file_or_dir,informer,cliutils)
    return


@cli.command()
@click.option('--pdb-dir', default='.', help='input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--max-resolution', default=2.0, type=float, help='maximum allowed resolution', show_default=True)
@click.option('--limit-r-free-grade', default='C', type=click.Choice(['A', 'B', 'C', 'D', 'E']),
              help='limit for R_free_grade:\n'+
   	                'A - MUCH BETTER THAN AVERAGE at this resolution\n'+
   	                'B - BETTER THAN AVERAGE at this resolution\n'+
	                'C - AVERAGE at this resolution\n'+
	                'D - WORSE THAN AVERAGE at this resolution\n'+
	                'E - UNRELIABLE\n',
              show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='sieve hydrogen atoms and hetatms from the files', show_default=True)
@click.option('--is-homomer/--is-heteromer', default=True,
              help='process the file as homomer or heteromer', show_default=True)
@click.option('--output-dir', default='output.{time}', help='output dir', show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def xray (pdb_dir,pdb_file, max_resolution, limit_r_free_grade, with_hydrogens,is_homomer, output_dir, verbose):
    """
    
    \b
    This procedure prepares protein files in pdb format from X-RAY measurements for a 
    CSM calculation according. 
    At first, the files are split into three categories according to their resolution 
    and R_free grade:
        a.  Reliable  – PDB files with a resolution of up to 2.0 and an R_free grade of C 
            (Average at this resolution). Thresholds can be changed.   
        b.  Reliable_r_grade – PDB files with a resolution of up to 2.0 and no R_free data
        c.  Others – PDB files with bad resolution or R_free grade
            
    Reliable files are further processed according to the following stages:
        1.  Removing non-coordinates lines from the atom section.
        2.  Removing ligands and solvent lines at the end of peptides. HETATOM lines in the 
            middle of a peptide are retained.
        3.  Cleaning gaps in the sequence according to REMARK 470 (missing residues) and REMARK 
            465 (missing atoms):
            a.  If a backbone atom is missing - the whole amino acid is deleted.
            b.  If a side chain atom is missing – the side chain is removed.
            c.  For homomers – gap on one peptide causes the removal of the related atoms from 
                all other peptides.
        4.  Retaining the first location in cases of alternate location.
        5.  Removing hydrogen atoms (optional).
        6.  Ignoring pdb files for which the asymmetric unit does not represent a biological structure
            (e.g., non unit matrix in REMARK 350).
        7.  For homomers, checking that all peptides are of the same length.
    """

    cliutils = xray_validate_params(pdb_dir,pdb_file, max_resolution, limit_r_free_grade, output_dir, verbose)
    informer = xray_inform(cliutils, is_verbose=verbose, include_hetatm=True)
    mode_file_or_dir=None
    short_file_name=None
    if pdb_file:
        mode_file_or_dir="file"
        pdb_dir,short_file_name=os.path.split(pdb_file)
        informer.process_one_file(pdb_dir,short_file_name, click)
    elif pdb_dir:
        mode_file_or_dir="dir"
        informer.process_complete_dir(pdb_dir, click)

    limit_r_free_grade_text = r_free_grade_vlaues.from_value(limit_r_free_grade)
    informer.filter_data(max_resolution=max_resolution, limit_r_free_grade=limit_r_free_grade_text, click=click)
    # click.secho("---------------------------------------------------------------------", fg='green')
    # sort the files into directories
    stager=stages(cliutils, informer,is_homomer=is_homomer)
    for directory, data, copy_or_clean in sorted(informer.output_data_config):
        if len(data) == 0:
            cliutils.verbose("{} - no items to process - I will continue".format(directory))
            continue
        dest_path = stager.set_dest_path(directory)
        rv = cliutils.mkdir(dirname=dest_path)
        if rv != 0:
            cliutils.exit(rv, 'ERROR', "could not mkdir {} retval is {} ".format(directory, rv))
        if copy_or_clean == 'copy':
            copy_data_into_dir(source_path=pdb_dir, dest_path=dest_path, data=data, cliutils=cliutils)
        else:
            informer.data = stager.run_clean_stages(
                                             directory=directory,
                                             dest_path=dest_path,
                                             data=data,
                                             with_hydrogens=with_hydrogens
                                             )



            # clean_missing_residues(data)
    # missing rsidues
    if mode_file_or_dir=="file":
        clean_tmp_data(stager,pdb_dir, short_file_name, informer, cliutils)
    finish_outputs(mode_file_or_dir,informer,cliutils)
    return





if __name__ == '__main__':
    cli()
