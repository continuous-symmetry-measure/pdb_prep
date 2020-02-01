import click

from Utils.cli_utils import cli_utils as cu
from Utils.inform import inform
from pdb_prep import *


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
# @click.option('--is-homomer/--is-heteromer', default=True,
#               help='process the file as homomer or heteromer', show_default=True)
@click.option('--ptype', default='homomer',
              type=click.Choice(['homomer', 'heteromer', 'monomer'], case_sensitive=False),
              show_default=True, help="Protein stoichiometry")
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='Parse or ignore remark 350  - default --parse-rem350')  # show_default=True)
# @click.option('--output-dir', default='output', help='output dir', show_default=True)
@click.option('--output-text/--output-json', default=True,
              help='Output report in text or json  - default --output-text')  # , show_default=True)
@click.option('--Verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def pdb_prep_all(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype, parse_rem350,
                 # output_dir,
                 output_text, verbose):
    """"""
    output_dir = "output.{time}"
    cliutils = cu(click=click, is_verbose=verbose, caller=pdb_prep_all.name)
    if pdb_file:
        curr_pdb_dir, short_file_name = os.path.split(pdb_file)
        if pdb_dir == '': curr_pdb_dir = os.getcwd()
        exp_method = get_experimental_method(os.path.join(curr_pdb_dir, pdb_file))
        if exp_method == 'X-RAY DIFFRACTION':
            func_xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype, parse_rem350,
                      output_dir, output_text, verbose)
        elif exp_method == 'SOLUTION NMR':
            func_nmr(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350,
                     output_dir, output_text, verbose)
        else:
            cliutils.error_msg("File: '{}' - Eexperimental method {} is not supported".format(pdb_file, exp_method))
    elif pdb_dir:
        nmr_dir, xray_dir = os.path.join(pdb_dir, ".nmr.tmp"), os.path.join(pdb_dir, ".xray.tmp")
        cliutils.mkdir(nmr_dir)
        cliutils.mkdir(xray_dir)
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
                cliutils.error_msg(
                    "File: '{}' - Experimental method {} is not supported".format(curr_pdb_file, exp_method))
        pdb_file = None
        if output_dir == 'output.{time}': output_dir = 'output'
        func_xray(xray_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype, parse_rem350,
                  output_dir + "-xray", output_text, verbose)
        func_nmr(nmr_dir, pdb_file, with_hydrogens, ptype, parse_rem350,
                 output_dir + "-nmr", output_text, verbose)
        cliutils.rmtree(nmr_dir)
        cliutils.rmtree(xray_dir)


if __name__ == '__main__':
    pdb_prep_all()
