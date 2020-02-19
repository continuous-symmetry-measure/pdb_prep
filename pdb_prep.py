#!/usr/bin/env python
import os
# import sys
# print(f"path: {sys.path}")
import click

from Utils.cli_utils import cli_utils as cu
from Chemistry.PDB.pdb_utils import *
from PDB_Prep.clean_stages import stages
from PDB_Prep.pdb_prep_functions import copy_data_into_dir, clean_tmp_data_dir_mode, clean_tmp_data_file_mode, \
    finish_outputs, validate_options
from PDB_Prep.pdb_prep_functions import xray_validate_params, nmr_validate_params
from PDB_Prep.pdb_prep_inform import xray_inform, nmr_inform

from version import __VERSION__


@click.group()
def cli():
    """
    pdb preprations
    need help?
    try : pdb_prep COMMAND --help

    """
    pass


@cli.command()
@click.option('--pdb-dir', default='.', help='The input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='Input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='Leave hydrogen atoms and hetatms from the files - default --no-hydrogens')  # , show_default=True)
@click.option('--ptype',
              type=click.Choice(['homomer', 'heteromer', 'monomer'], case_sensitive=False),
              help="Protein stoichiometry (defualt: homomer)")
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='Parse or ignore remark 350  - default --parse-rem350')  # show_default=True)
@click.option('--bio-molecule-chains', type=click.INT, help='Number of peptides in remark 350')
@click.option('--output-dir', default='output.{time}', help='Output dir', show_default=True)
@click.option('--output-text/--output-json', default=True,
              help='Output report in text or json  - default --output-text')  # , show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='Verbose mode', show_default=True)
def nmr(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350, bio_molecule_chains, output_dir,
        output_text, verbose):
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
    print("Version: {}".format(__VERSION__))
    ret_val = func_nmr(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350, bio_molecule_chains, output_dir,
                       output_text, verbose)
    exit(ret_val)


def func_nmr(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350, bio_molecule_chains, output_dir,
             output_text, verbose):
    report = ""
    is_homomer = True
    if ptype is None and bio_molecule_chains == 1:
        ptype = 'monomer'
        cu(click).msg("The option '--ptype' was set to monomer since you set '--bio-molecule-chains' to 1")

    if ptype == 'heteromer':
        is_homomer = False
    ignore_remarks = []
    if not parse_rem350:
        ignore_remarks.append(350)
    cliutils = nmr_validate_params(pdb_dir=pdb_dir, pdb_file=pdb_file, output_dir=output_dir, verbose=verbose)
    if not validate_options(parse_rem350, bio_molecule_chains, ptype, cliutils):
        return -1

    informer = nmr_inform(cliutils, is_verbose=verbose, include_hetatm=True, ignore_remarks=ignore_remarks,
                          bio_molecule_chains=bio_molecule_chains)
    mode_file_or_dir = None
    short_file_name = None
    if pdb_file:
        mode_file_or_dir = "file"
        parse_rem350 = False
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
            cliutils.error_msg("I did not find any PDB files in the input folder", caller=func_nmr.__name__)
            return 31

    # limit_r_free_grade_text = r_free_grade_values.from_value(limit_r_free_grade)
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
                ignore_remarks=ignore_remarks,
                bio_molecule_chains=bio_molecule_chains
            )

    if mode_file_or_dir == "file":
        clean_tmp_data_file_mode(stager, pdb_dir, short_file_name, informer, cliutils)
    else:
        clean_tmp_data_dir_mode(stager, pdb_dir, informer, cliutils)
    if output_text:
        output_type = "text"
    else:
        output_type = "json"
    finish_outputs(mode_file_or_dir, informer, cliutils, stager, report, output_type)
    return 0


@cli.command()
@click.option('--pdb-dir', default='.', help='Input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='Input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--max-resolution', default=2.0, type=float, help='Maximum allowed resolution', show_default=True)
@click.option('--limit-r-free-grade', default='C', type=click.Choice(['A', 'B', 'C', 'D', 'E']),
              help='Limit for R_free_grade:\n' +
                   'A - MUCH BETTER THAN AVERAGE at this resolution\n' +
                   'B - BETTER THAN AVERAGE at this resolution\n' +
                   'C - AVERAGE at this resolution\n' +
                   'D - WORSE THAN AVERAGE at this resolution\n' +
                   'E - UNRELIABLE\n',
              show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='Leave hydrogen atoms and hetatms from the files - default --no-hydrogens')  # , show_default=True)
@click.option('--ptype',
              type=click.Choice(['homomer', 'heteromer', 'monomer'], case_sensitive=False),
              help="Protein stoichiometry (defualt: homomer)")
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='Parse or ignore remark 350  - default --parse-rem350')  # show_default=True)
@click.option('--bio-molecule-chains', type=click.INT, help='Number of peptides in remark 350')
@click.option('--output-dir', default='output.{time}', help='Output dir', show_default=True)
@click.option('--output-text/--output-json', default=True,
              help='Output report in text or json  - default --output-text')  # , show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='Verbose mode', show_default=True)
def xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
         parse_rem350, bio_molecule_chains, output_dir, output_text, verbose):
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
    print("Version: {}".format(__VERSION__))
    print(f"path: {sys.path}")
    ret_val = func_xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
                        parse_rem350, bio_molecule_chains, output_dir, output_text, verbose)
    exit(ret_val)


def func_xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
              parse_rem350, bio_molecule_chains, output_dir, output_text, verbose):
    report = ""
    is_homomer = True
    if ptype is None and bio_molecule_chains == 1:
        ptype = 'monomer'
        cu(click).msg("The option '--ptype' was set to monomer since you set '--bio-molecule-chains' to 1")

    if ptype == 'heteromer':
        is_homomer = False

    ignore_remarks = []
    if not parse_rem350:
        ignore_remarks.append(350)
    cliutils = xray_validate_params(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, output_dir, verbose)
    if not validate_options(parse_rem350, bio_molecule_chains, ptype, cliutils):
        return -1
    informer = xray_inform(cliutils, is_verbose=verbose, include_hetatm=True, ignore_remarks=ignore_remarks,
                           bio_molecule_chains=bio_molecule_chains)
    mode_file_or_dir = None
    short_file_name = None
    if pdb_file:
        mode_file_or_dir = "file"
        pdb_dir, short_file_name = os.path.split(pdb_file)
        # print(">>>>>>>>>>{}-{}".format(pdb_file, get_experimental_method(pdb_file)))
        informer.process_one_file(pdb_dir, short_file_name, click)
    elif pdb_dir:
        mode_file_or_dir = "dir"
        try:
            informer.process_complete_dir(pdb_dir, click)
            cliutils.verbose("informer.process_complete_dir ended")
        except IndexError as e:
            cliutils.error_msg("I did not find any PDB files in the input folder", func_xray.__name__)
            return 31

    limit_r_free_grade_text = r_free_grade_values.from_value(limit_r_free_grade)
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
            informer.data, report = stager.run_clean_stages(
                directory=directory,
                dest_path=dest_path,
                data=data,
                with_hydrogens=with_hydrogens,
                ignore_remarks=ignore_remarks,
                bio_molecule_chains=bio_molecule_chains
            )

            # clean_missing_residues(data)
    # missing rsidues
    if mode_file_or_dir == "file":
        clean_tmp_data_file_mode(stager, pdb_dir, short_file_name, informer, cliutils)
    else:
        clean_tmp_data_dir_mode(stager, pdb_dir, informer, cliutils)

    if output_text:
        output_type = "text"
    else:
        output_type = "json"
    finish_outputs(mode_file_or_dir, informer, cliutils, stager, report, output_type)
    return 0


if __name__ == '__main__':
    cli()
