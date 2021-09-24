import os

import click

from PDB_Prep.pdb_prep_functions import validate_input_dir_or_file
from Utils.cli_utils import cli_utils as cu
from Utils.inform import inform
from pdb_prep import func_xray, func_nmr, func_others_methods, get_experimental_method


@click.command()
@click.option('--pdb-dir', default='.', help='Input pdb directory containing PDB files', show_default=True)
@click.option('--pdb-file', help='Input pdb file (use this or the --pdb-dir option!)', show_default=True)
@click.option('--max-resolution', default=2.0, type=float, help='Maximum allowed resolution', show_default=True)
@click.option('--limit-r-free-grade', default='C', type=click.Choice(['A', 'B', 'C', 'D', 'E']),
              help='Limit for R_free_grade:\n' +
                   'A - Much better than average at this resolution\n' +
                   'B - Better than average at this resolution\n' +
                   'C - Average at this resolution\n' +
                   'D - Worse than average at this resolution\n' +
                   'E - Unreliable\n',
              show_default=True)
@click.option('--with-hydrogens/--no-hydrogens', default=False,
              help='Leave hydrogen atoms and hetatms from the files - default --no-hydrogens')  # , show_default=True)
@click.option('--ptype',
              type=click.Choice(['homomer', 'heteromer', 'monomer'], case_sensitive=False),
              help="Protein stoichiometry (defulet: homomer)")
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='Parse or ignore remark 350  - default --parse-rem350')  # show_default=True)
@click.option('--bio-molecule-chains', type=click.INT, help='Number of peptides in remark 350')
@click.option('--output-text/--output-json', default=True,
              help='Output report in text or json  - default --output-text')  # , show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def pdb_prep_all(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
                 parse_rem350, bio_molecule_chains, output_text, verbose):
    """"""
    output_dir = "output.{time}"
    cliutils = cu(click=click, is_verbose=verbose, caller=pdb_prep_all.name)
    validate_input_dir_or_file(pdb_dir, pdb_file, cliutils)
    if pdb_file:
        curr_pdb_dir, short_file_name = os.path.split(pdb_file)
        if pdb_dir == '': curr_pdb_dir = os.getcwd()
        exp_method = get_experimental_method(os.path.join(curr_pdb_dir, pdb_file))
        if exp_method == 'X-RAY DIFFRACTION':
            func_xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
                      parse_rem350, bio_molecule_chains, output_dir, output_text, verbose)
        elif exp_method == 'SOLUTION NMR':
            func_nmr(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350, bio_molecule_chains,
                     output_dir, output_text, verbose)
        else:
            cliutils.warn_msg(
                "File: '{}' - Experimental method {} is not fully supported - I will try to process it.".format(
                    pdb_file, exp_method))
            func_others_methods(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350, bio_molecule_chains,
                                output_dir, output_text, verbose)

    elif pdb_dir:
        os.chdir(pdb_dir)
        nmr_dir = os.path.join(pdb_dir, ".nmr.tmp")
        xray_dir = os.path.join(pdb_dir, ".xray.tmp")
        other_methods_dir = os.path.join(pdb_dir, ".other_methods.tmp")
        cliutils.mkdir(nmr_dir)
        cliutils.mkdir(xray_dir)
        cliutils.mkdir(other_methods_dir)
        informer = inform(cliutils, verbose)

        files = informer.get_files_list(pdb_dir)
        for curr_pdb_file in files:
            exp_method = get_experimental_method(curr_pdb_file)

            if exp_method == 'X-RAY DIFFRACTION':
                # print(">>>>>>>>>>{}-{}".format(curr_pdb_file, get_experimental_method(curr_pdb_file)))
                cliutils.copy_file(curr_pdb_file, xray_dir)
            elif exp_method == 'SOLUTION NMR':
                # print(">>>>>>>>>>{}-{}".format(curr_pdb_file, get_experimental_method(curr_pdb_file)))
                cliutils.copy_file(curr_pdb_file, nmr_dir)
            else:
                # print(">>>>>>>>>>{}-{}".format(curr_pdb_file, get_experimental_method(curr_pdb_file)))
                cliutils.warn_msg(
                    "File: '{}' - Experimental method {} is not fully supported - I will try to process it.".format(
                        curr_pdb_file, exp_method))
                cliutils.copy_file(curr_pdb_file, other_methods_dir)

        pdb_file = None
        if output_dir == 'output.{time}': output_dir = 'output'
        try:
            func_xray(xray_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
                      parse_rem350, bio_molecule_chains, output_dir + "-xray", output_text, verbose)
            func_nmr(nmr_dir, pdb_file, with_hydrogens, ptype,
                     parse_rem350, bio_molecule_chains, output_dir + "-nmr", output_text, verbose)
            func_others_methods(other_methods_dir, pdb_file, with_hydrogens, ptype,
                                parse_rem350, bio_molecule_chains, output_dir + "-other_methods", output_text, verbose)

        except Exception as e:
            cliutils.rmtree(nmr_dir)
            cliutils.rmtree(xray_dir)
            cliutils.rmtree(other_methods_dir)
            cliutils.error_msg("Unexpected error: {}".format(e))
            raise e

        cliutils.rmtree(nmr_dir)
        cliutils.rmtree(xray_dir)
        cliutils.rmtree(other_methods_dir)


if __name__ == '__main__':
    pdb_prep_all()
