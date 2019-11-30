# TODO list
* unit_tests:
    * pdb_utils.eqvivalent_residues
    * pdb_atom.parse...(cls,...)
    * inform
    * simple_siever.parse_opt (None, "simple", "atom_names:H+CA
    * chain_util.fix_atoms_serial_number
    * ~~pdb_atom.eqvivalent_atom~~ 
        move get_pairs_tupels to the module: 
            Chemistry\code\atoms_pairs.py
    * ~~Utils.cli_utils~~
    * ~~hetatm~~
    * ~~pdb_chain.chain_utils~~
    * ~~pdb_remark~~
    * ~~pdb_utils.pdb_info~~
* improve pdb_quick_info
    * add commands:
        * summeray
            - short sammeray as done today
        * compare peptides
                "--model-num" ,"defualt=1"
                "--pdb_file"
            - create file "{chain_id}.{model_num}.file" for each peptide
            - create diff file of the atoms of the peptides sequances



* create Seivers pkg
* document cli_utils
* add tests for current programs   
* add exceptions for pdb_obj
* hatm_siever
* ~~**fix** remrak (each remark is is list of lines)~~
* ~~pdb_utils.to_json~~
* refract pdb_atom
    * pdb_atom.from_json
    * pdb_atom.from_line
    * pdb_atom.__init__(atom_dict)
* readme.md
* proteine_vector_distance


"""
> pdb_prep.py xray --pdb-dir .
>> we get only other dir with no report

> pdb_prep.py nmr --pdb-dir .
>> fix report format:
nmr:
file                      identical_to_the_asym_unit
5xzk.pdb                  True
6nhy.pdb                  True

excluded:
excluded_files:

excluded_file            reason
2h9r.pdb                  file: '2h9r.pdb' - exepcted homomer but got heteromer
2le8.pdb                  file: '2le8.pdb' - exepcted homomer but got heteromer

others:1qky.pdb


"""
