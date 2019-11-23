#!/usr/bin/env python

import os

import click

from Chemistry.PDB.pdb_utils import *
from PDB_Prep.clean_stages import stages
from PDB_Prep.pdb_prep_functions import copy_data_into_dir, clean_tmp_data_dir_mode, clean_tmp_data_file_mode, \
    finish_outputs
from PDB_Prep.pdb_prep_functions import xray_validate_params, nmr_validate_params
from PDB_Prep.pdb_prep_inform import xray_inform, nmr_inform


@click.group()
def cli():
    """
    pdb preprations
    need help?
    try : pdb_prep COMMAND --help

    """
    pass


@cli.command()
@click.option('--pdb-dir', default='.', help='the input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='sieve hydrogen atoms and hetatms from the files', show_default=True)
@click.option('--is-homomer/--is-heteromer', default=True,
              help='process the file as homomer or heteromer', show_default=True)
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='parse or ignore remark 350', show_default=True)
@click.option('--output-dir', default='output.{time}', help='output dir', show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def nmr(pdb_dir, pdb_file, with_hydrogens, is_homomer, parse_rem350, output_dir, verbose):
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
    report = ""
    ignore_remarks = []
    if not parse_rem350:
        ignore_remarks.append(350)
    cliutils = nmr_validate_params(pdb_dir=pdb_dir, pdb_file=pdb_file, output_dir=output_dir, verbose=verbose)
    informer = nmr_inform(cliutils, is_verbose=verbose, include_hetatm=True, ignore_remarks=ignore_remarks)
    mode_file_or_dir = None
    short_file_name = None
    if pdb_file:
        mode_file_or_dir = "file"
        pdb_dir, short_file_name = os.path.split(pdb_file)
        informer.process_one_file(pdb_dir, short_file_name, click)
        # informer.ignore_remarks.append(2)  # remark 2 is resolution - ignore it
        # informer.ignore_remarks.append(3)  # remark 3 is r_free - ignore it
    elif pdb_dir:
        mode_file_or_dir = "dir"
        try:
            informer.process_complete_dir(pdb_dir, click)
            cliutils.verbose("informer.process_complete_dir ended")
        except IndexError as  e:
            cliutils.error_msg("I did not find any PDB files in the input folder")
            exit(31)

    # limit_r_free_grade_text = r_free_grade_vlaues.from_value(limit_r_free_grade)
    informer.filter_data(click=click, test_is_homomer=is_homomer)

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
            informer.data, report = stager.run_clean_stages(
                directory=directory,
                dest_path=dest_path,
                data=data,
                with_hydrogens=with_hydrogens,
                ignore_remarks=ignore_remarks
            )

    if mode_file_or_dir == "file":
        clean_tmp_data_file_mode(stager, pdb_dir, short_file_name, informer, cliutils)
    else:
        clean_tmp_data_dir_mode(stager, pdb_dir, informer, cliutils)

    finish_outputs(mode_file_or_dir, informer, cliutils, stager, report)
    return


@cli.command()
@click.option('--pdb-dir', default='.', help='input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--max-resolution', default=2.0, type=float, help='maximum allowed resolution', show_default=True)
@click.option('--limit-r-free-grade', default='C', type=click.Choice(['A', 'B', 'C', 'D', 'E']),
              help='limit for R_free_grade:\n' +
                   'A - MUCH BETTER THAN AVERAGE at this resolution\n' +
                   'B - BETTER THAN AVERAGE at this resolution\n' +
                   'C - AVERAGE at this resolution\n' +
                   'D - WORSE THAN AVERAGE at this resolution\n' +
                   'E - UNRELIABLE\n',
              show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='sieve hydrogen atoms and hetatms from the files', show_default=True)
@click.option('--is-homomer/--is-heteromer', default=True,
              help='process the file as homomer or heteromer', show_default=True)
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='parse or ignore remark 350', show_default=True)
@click.option('--output-dir', default='output.{time}', help='output dir', show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, is_homomer, parse_rem350, output_dir,
         verbose):
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
    report = ""
    ignore_remarks = []
    if not parse_rem350:
        ignore_remarks.append(350)
    cliutils = xray_validate_params(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, output_dir, verbose)
    informer = xray_inform(cliutils, is_verbose=verbose, include_hetatm=True, ignore_remarks=ignore_remarks)
    mode_file_or_dir = None
    short_file_name = None
    if pdb_file:
        mode_file_or_dir = "file"
        pdb_dir, short_file_name = os.path.split(pdb_file)
        informer.process_one_file(pdb_dir, short_file_name, click)
    elif pdb_dir:
        mode_file_or_dir = "dir"
        try:
            informer.process_complete_dir(pdb_dir, click)
            cliutils.verbose("informer.process_complete_dir ended")
        except IndexError as  e:
            cliutils.error_msg("I did not find any PDB files in the input folder")
            exit(31)

    limit_r_free_grade_text = r_free_grade_vlaues.from_value(limit_r_free_grade)
    informer.filter_data(max_resolution=max_resolution, limit_r_free_grade=limit_r_free_grade_text, click=click,
                         test_is_homomer=is_homomer)

    # sort the files into directories
    stager = stages(cliutils, informer, is_homomer=is_homomer)

    for directory, data, copy_or_clean in informer.output_data_config:
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
            informer.data, report  = stager.run_clean_stages(
                directory=directory,
                dest_path=dest_path,
                data=data,
                with_hydrogens=with_hydrogens,
                ignore_remarks=ignore_remarks
            )

            # clean_missing_residues(data)
    # missing rsidues
    if mode_file_or_dir == "file":
        clean_tmp_data_file_mode(stager, pdb_dir, short_file_name, informer, cliutils)
    else:
        clean_tmp_data_dir_mode(stager, pdb_dir, informer, cliutils)

    finish_outputs(mode_file_or_dir, informer, cliutils, stager, report)
    return


if __name__ == '__main__':
    cli()
