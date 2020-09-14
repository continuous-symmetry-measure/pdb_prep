import os

from Geometry.distance import point_3d, distance


def print_results(results):
    line_tmpl = "{:<15} {:10} {:<9} {:<8} {:<7} {:<7}   "

    header_tmpl = line_tmpl + "{:>8} {:>8} {:>8}    {:>8}"
    line_tmpl = line_tmpl + "{:+2.4f} {:>+2.4f} {:>+2.4f}    {:8.4f}"
    print("", flush=True)
    print(header_tmpl.format("file", "atom_name", "model_num", "chain_id", "resname", "resseq", "X1", "Y1", "Z1",
                             "distance"))
    for rslt in results:
        (file, atom_name, model_number, chain_id, resname, resseq, p, dist) = rslt
        print(line_tmpl.format(
            file,
            atom_name,
            model_number,
            chain_id,
            resname,
            resseq,
            float(p.x), float(p.y), float(p.z),
            dist))


def dist_from_vector(input_file, model_number, chain_id, atoms, vector3d):
    short_file_name = os.path.basename(input_file)
    results = []
    for atom in atoms:
        point = point_3d(atom.x, atom.y, atom.z)
        dist = distance.between_point_and_vector(point, vector3d)
        curr_result = (
            short_file_name,
            atom.atom_name,
            model_number,
            chain_id,
            atom.resname,
            atom.resseq,
            point,
            dist
        )
        results.append(curr_result)
        return results
