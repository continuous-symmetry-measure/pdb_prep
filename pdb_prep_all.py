from pdb_prep import *
from Utils.cli_utils import cli_utils as cu
import click


@click.command()
@click.option('--pdb-dir', default='.', help='the input pdb directory containing PDB files', show_default=True)
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
# @click.option('--is-homomer/--is-heteromer', default=True,
#               help='process the file as homomer or heteromer', show_default=True)
@click.option('--ptype', default='homomer',
              type=click.Choice(['homomer', 'heteromer', 'monomer'], case_sensitive=False),
              show_default=True, help="protein stoichiometry")
@click.option('--parse-rem350/--ignore-rem350', default=True,
              help='parse or ignore remark 350', show_default=True)
@click.option('--output-dir', default='output.{time}', help='output dir', show_default=True)
@click.option('--output-text/--output-json', default=True,
              help='output report in text or json', show_default=True)
@click.option('--verbose', is_flag=True, default=False, help='verbose mode', show_default=True)
def pdb_prep_all(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype, parse_rem350, output_dir,
                 output_text, verbose):
    """ add your help msg here"""
    cliutils = cu(click=click, is_verbose=verbose, caller=pdb_prep_all.name)
    if pdb_file:
        mode_file_or_dir = "file"
        pdb_dir, short_file_name = os.path.split(pdb_file)
        if pdb_dir == '': pdb_dir = '.'
        exp_method = get_experimental_method(pdb_file)
        if exp_method == 'X-RAY DIFFRACTION':
            func_xray(pdb_dir, pdb_file, max_resolution, limit_r_free_grade, with_hydrogens, ptype,
                      parse_rem350, output_dir, output_text, verbose)
        elif exp_method == 'SOLUTION NMR':
            func_nmr(pdb_dir, pdb_file, with_hydrogens, ptype, parse_rem350, output_dir,
                     output_text, verbose)
        else:
            cliutils.error_msg("file: {} - exprimental method {} s not supported".format(pdb_file, exp_method))
    elif pdb_dir:
        cliutils.error_msg("dir: {} - --pdb-dir {} s not supported".format(pdb_dir))


if __name__ == '__main__':
    pdb_prep_all()
