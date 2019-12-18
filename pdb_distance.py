#!/usr/bin/env python

import os

import click

from Chemistry.PDB.Sievers import atom_names_siever
from Chemistry.PDB.pdb_atom import eqvivalent_atoms
from Chemistry.PDB.pdb_obj import pdb
from Geometry.distance import point_3d
from PDB_Distance import protein_dimer_distance, symetric_axis_distance
from Utils.cli_utils import cli_utils as cu


@click.group()
def cli():
    """
    get distance info of ... TODO\n
    need help?\n
    try : pdb_distance COMMAND --help

    """
    pass


def validate_input_file(cliutils, input_file):
    exit_code = cliutils.check_file(input_file, "--input-file")
    if exit_code > 0:
        exit(exit_code)


def validate_dimer_options(cliutils, input_file, atoms_names, verbose):
    validate_input_file(cliutils, input_file)
    if atoms_names is None or len(atoms_names) == 0:
        cliutils.exit(5, "ERROR", "missing --atoms_names")
    atoms = atoms_names.split(',')
    ret_atoms = []
    for atom in atoms:
        a = atom.strip('"').strip("'")
        if len(a) < 1:
            cliutils.exit(5, "ERROR", "missing atom in --atoms-names:{}", format(atoms_names))
        if len(a) > 3:
            cliutils.exit(5, "ERROR", "atom name:'{}' too long in --atoms-names:{}", format(a, atoms_names))
        ret_atoms.append(a)
    return ret_atoms


def validate_trimer_options(cliutils, input_file, coordinates, verbose):
    validate_input_file(cliutils, input_file)
    xyz = coordinates.split(',')
    if len(xyz) != 3:
        cliutils.exit(5, "ERROR", "--coordinates not in the format 'x,y,z' :{}", format(coordinates))
    ret_xyz = []
    try:
        for c in xyz:
            coord = c.strip('"').strip("'")
            ret_xyz.append(float(coord))
    except Exception as e:
        cliutils.exit(5, "ERROR", "--coordinates {} - Not a number:{}", format(coordinates, coord))

    return (ret_xyz[0], ret_xyz[1], ret_xyz[2])


@cli.command()
@click.option('--input-file', '-i', help='the input pdb file', default=os.path.join(os.getcwd(), "pdb_files", " "))
@click.option('--axis', '-s', help='the symmetry axis  in the formay x,y,z (e.g "0.1002,0.001,0.0003")')
@click.option('--verbose', '-v', is_flag=True, default=False, help='verbose mode')
def sym_axis(input_file, axis, verbose):
    """
    \b
    calculates the distance of each amino acid from the symmetry axis.
    homomer symmetric axis distance
    """
    _caller = "atoms_pairs command"
    cliutils = cu(click, is_verbose=verbose)

    _axis = validate_trimer_options(cliutils, input_file, axis, verbose)
    mypdb = pdb.from_file(input_file)
    atoms_names = ["CA", "CB"]
    results = []
    vector3d = point_3d(*_axis)
    for atom_name in atoms_names:
        siever = atom_names_siever(atom_name)
        for model in mypdb:
            for chain in model:
                msg = "atom:{:<3} model number:{} ,chain_id: {}"
                cliutils.verbose(msg.format(atom_name, model.model_number, chain.chain_id), caller=_caller)
                is_match = lambda atom: siever.is_match(atom, atom_name)
                current_results = symetric_axis_distance.dist_from_vector(
                    input_file=input_file,
                    model_number=model.model_number,
                    chain_id=chain.chain_id,
                    atoms=filter(is_match, chain),
                    vector3d=vector3d
                )
                results.extend(current_results)
    symetric_axis_distance.print_results(results)


@cli.command()
@click.option('--input-file', '-i', help='the input pdb file', default=os.path.join(os.getcwd(), "pdb_files", " "))
@click.option('--atoms-names', '-a', help='atom names from pdb file (e.g "CA,CB")')
@click.option('--verbose', '-v', is_flag=True, default=False, help='verbose mode')
def atoms_pairs(input_file, atoms_names, verbose):
    """
    \b
    Calculates distances between matching pairs of amino acids.
    """
    _caller = "atoms_pairs command"
    cliutils = cu(click, is_verbose=verbose)

    atoms = validate_dimer_options(cliutils, input_file, atoms_names, verbose)

    mypdb = pdb.from_file(input_file)

    if len(mypdb) == 0:
        cliutils.exit(2, "ERROR", "pdb_file  has no models: {}".format(input_file))
        exit(2)
    cliutils.verbose("{}".format(mypdb.info()), _caller)
    results = []
    for atom in atoms:
        for model in mypdb:
            cliutils.verbose("atom:{:<3} model number:{}".format(atom, model.model_number), caller=_caller)
            if len(model) != 2:
                msg = "atom:{:<3} model number: {} is not atoms_pairs (has {} chains) in pdb_file '{}'"
                cliutils.warn_msg(msg.format(atom, model.model_number, len(model), input_file), caller=_caller)
                continue
            cliutils.verbose("This is atoms_pairs (has two chains)...", caller=_caller)

            eqviv_atm = eqvivalent_atoms()
            pairs_of_atoms = eqviv_atm.get_pairs_tupels(model, atom)
            if len(pairs_of_atoms) == 0:
                msg = "atom:{:<3} model number: {} - could not find {} pairs in {}"
                cliutils.warn_msg(msg.format(atom, model.model_number, atom, len(model), input_file), caller=_caller)
            current_results = protein_dimer_distance.dist_pairs(input_file, model.model_number, pairs_of_atoms)
            results.extend(current_results)

    protein_dimer_distance.print_results(results)
    return results


if __name__ == '__main__':
    cli()
