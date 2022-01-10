import sys

from Chemistry.PDB.pdb_atom import pdb_atom
from Chemistry.PDB.pdb_chain import pdb_chain
from Chemistry.PDB.pdb_constants import pdb_constants

"""
* pdb is list of pdb_models
* pdb_model is a list of pdb_chains objects
* pdb _chain is a list of pdb_atom objects
* atom ahs attributes such as:
    - atom_serial_number
    - atom_name
    - resname
    - resseq
    - chain_id
    ...
"""


class pdb_model(list):

    @classmethod
    def _is_end_of_chain(cls, current_chain_id, current_line, next_line, pdb_const_str):
        if next_line is None:
            return True
        if current_chain_id != pdb_atom.parse_chain_id(current_line):
            return True
        if current_line.startswith(pdb_const_str.TER):
            return True
        return False

    @classmethod
    def _find_next_chain_id(cls, model_lines, current_index, current_chain_id):
        if current_index == len(model_lines) - 1:
            return None
        for line in model_lines[current_index + 1:]:
            if current_chain_id != pdb_atom.parse_chain_id(line):
                return pdb_atom.parse_chain_id(line)

    @classmethod
    def from_pdb_model_lines(cls, pdb_model_lines, model_number='1', include_hetatm=False, pdb_file_name=""):
        if not model_number:
            model_number = '1'
        else:
            model_number = str(model_number)

        pdb_atoms_lines = []
        pdb_chains = []
        pdb_const_str = pdb_constants()
        # flag=False
        used_chain_ids = ['NO_CHAIN']
        chain_id = pdb_atom.parse_chain_id(pdb_model_lines[0])
        ter_line = None
        for li, line in enumerate(pdb_model_lines):
            if li < len(pdb_model_lines) - 1:
                next_line = pdb_model_lines[li + 1]
            else:
                next_line = None

            if line.startswith(pdb_const_str.TER):
                ter_line = line

            if cls._is_end_of_chain(current_chain_id=chain_id, current_line=line, next_line=next_line,
                                    pdb_const_str=pdb_const_str):
                if len(pdb_atoms_lines) == 0:  # there are no atoms lines in this model
                    chain_id = cls._find_next_chain_id(model_lines=pdb_model_lines, current_index=li,
                                                       current_chain_id=chain_id)
                    ter_line = None
                    continue

                chain = pdb_chain.from_pdb_atoms_lines(pdb_atoms_lines, ter_line)
                pdb_chains.append(chain)
                pdb_atoms_lines = []
                used_chain_ids.append(chain.chain_id)
                chain_id = cls._find_next_chain_id(model_lines=pdb_model_lines, current_index=li,
                                                   current_chain_id=chain_id)
                ter_line = None
                continue
            record_name = pdb_atom.parse_record_name(line)
            current_chain_id = pdb_atom.parse_chain_id(line)
            if record_name == pdb_const_str.HETATM and current_chain_id in used_chain_ids:
                # HETATM after to TER line with prev used_chain_ids
                continue

            if record_name not in [pdb_const_str.ATOM, pdb_const_str.HETATM]:
                continue

            # chain change without ter_line so will create the terr line
            if len(pdb_atoms_lines) > 0:
                this_chain_id = pdb_atom(pdb_atoms_lines[0]).chain_id
                curr_line_chain_id = current_chain_id
                # if flag:
                # print ("this_chain_id={},curr_line_chain_id={}".format(this_chain_id,curr_line_chain_id))
                # chain end  - But no TER line
                if curr_line_chain_id != this_chain_id:
                    print("WARN: {}: TER line is missing before:'{}'".format(pdb_file_name, line), file=sys.stderr)
                    last_atom_line = pdb_atoms_lines[0]
                    ter_line = pdb_chain.create_ter_line(last_atom_line)
                    chain = pdb_chain.from_pdb_atoms_lines(pdb_atoms_lines, ter_line)
                    pdb_chains.append(chain)
                    # print ("new_chain: this_chain_id={},curr_line_chain_id={}".format(this_chain_id,curr_line_chain_id))
                    # print ("\n".join(pdb_atoms_lines))
                    pdb_atoms_lines = []
                    continue

            if line.startswith(pdb_const_str.ATOM):
                pdb_atoms_lines.append(line)
            elif line.startswith(pdb_const_str.HETATM) and include_hetatm:
                pdb_atoms_lines.append(line)

        # we should remove the last HETATM section in the following sequances:
        # ATOM-HETATM- ATOM -TER-HETATM-CONNECT
        # ATOM-...-ATOM-... -TER-HETATM-ENDMDL
        # ATOM-HETATM-..-ATOM-TER-HETATM_A-ATOM-HETATM-..-ATOM-TER-HETATM_B
        # -CONNECT
        #        cahin A            ^                     chain B   ^
        #
        is_atom = lambda a: a.record_name == pdb_const_str.ATOM
        has_atoms_records = lambda c: len(list(filter(is_atom, c))) > 0
        for i in range(-1, -1 * len(pdb_chains) - 1, -1):
            if not has_atoms_records(pdb_chains[-1]):
                del (pdb_chains[-1])
            else:
                break

        return cls(pdb_chains, model_number)

    def __init__(self, pdb_chains, model_number='1'):
        if not model_number:
            self.model_number = '1'
        else:
            self.model_number = str(model_number)
        self.pdb_const_str = pdb_constants()
        self.extend(pdb_chains)
        self.wrap_with_header_and_footer = True

    def __str__(self):
        model_str = ""
        if self.wrap_with_header_and_footer:
            model_str = "{} {}\n".format(self.pdb_const_str.MODEL, self.model_number)
        model_str += "\n".join(map(str, self))
        if self.wrap_with_header_and_footer:
            model_str += "\n" + self.pdb_const_str.ENDMDL
        return model_str

    def info(self):
        return {
            "model_number": self.model_number,
            "number_of_chains": len(self),
            "atoms_per_chain": list(map(len, self))
        }

    def get_number_of_chains(self):
        return len(self)
