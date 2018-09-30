#!/usr/bin/env python

import os
import click
from Utils.cli_utils import cli_utils as cu
from Utils.inform import inform
from Utils.inform import chains_comapre
from Chemistry.PDB.pdb_obj import pdb


@click.group()
def cli():
    """
    some info about PDB file
    need help?
     try : pdb_info COMMAND --help

    """
    pass


@cli.command()
@click.option('-d', '--pdb-dir', help='the input pdb  directory which contains PDB files')
@click.option('-v', '--verbose', is_flag=True, default=False, help='verbose mode')
def dir_brief(pdb_dir, verbose):
    """
    get a brief info on the PDB file content
    """
    cliutils = cu(click, is_verbose=verbose)
    informer = inform(cliutils)
    if not os.path.isdir(pdb_dir):
        cliutils.exit(1, "ERROR", "no such dir:{}".format(pdb_dir))

    file_name = os.path.basename(pdb_dir)
    path = os.path.dirname(pdb_dir)
    informer.complete_dir(pdb_dir, click)
    return 0


@cli.command()
@click.option('-i', '--pdb-file', help='the input pdb file or a directory containing PDB files')
@click.option('-v', '--verbose', is_flag=True, default=False, help='verbose mode')
def brief(pdb_file, verbose):
    """
    get a brief info on the PDB file content
    """
    cliutils = cu(click, is_verbose=verbose)
    informer = inform(cliutils)
    if not os.path.isfile(pdb_file):
        cliutils.exit(1, "ERROR", "no such file:{}".format(pdb_file))

    if not pdb_file.lower().endswith(".pdb"):
        cliutils.exit(2, "ERROR", "not a pdb file: {}".format(pdb_file))

    file_name = os.path.basename(pdb_file)
    path = os.path.dirname(pdb_file)
    pdbinfo=informer.create_pdb_info(file_name, path)
    informer.one_file(pdbinfo)
    return 0


@cli.command()
@click.option('-i', '--pdb-file', help='the input pdb file ')
@click.option('-o', '--out-file', help='the output html file [defult PDB_FILE-diff.html]')
@click.option('-a', '--chain-a', help='the chain id  of the first peptide')
@click.option('-b', '--chain-b', help='the chain id  of the second peptide')
@click.option('--model-a', default='1', help='the model number of the first peptide ', show_default=True)
@click.option('--model-b', default='1', help='the model number of the second peptide ', show_default=True)
@click.option('-v', '--verbose', is_flag=True, default=False, help='verbose mode')
def diff(pdb_file, out_file, chain_a, chain_b, model_a, model_b,
         verbose):  # , chain_id_a, chain_id_b, model_num_a, model_num_b,verbose):
    """compare two peptides"""
    cliutils = cu(click, is_verbose=verbose)
    if not os.path.isfile(pdb_file):
        cliutils.exit(1, "ERROR", "no such file:{}".format(pdb_file))

    if not pdb_file.lower().endswith(".pdb"):
        cliutils.exit(2, "ERROR", "not a pdb file: {}".format(pdb_file))

    if not out_file:
        out_short_name = os.path.basename(pdb_file, )
        out_short_name = os.path.splitext(out_short_name)[0]
        out_short_name = out_short_name + '-diff.html'
        out_file = os.path.join(os.getcwd(), out_short_name)

    _pdb = pdb.from_file(pdb_file)
    chain_a = _pdb.get_chain(str(model_a), str(chain_a))
    chain_b = _pdb.get_chain(str(model_b), str(chain_b))
    _chains_comapre = chains_comapre()
    print("start diff...", flush=True)
    diff = _chains_comapre.comapre_two_chains(chain_a, chain_b)
    print("end diff...", flush=True)
    with open(out_file, "w") as htf:
        htf.write(diff)
    click.echo("diff is is in: {}".format(out_file))
    return 0


if __name__ == '__main__':
    cli()
