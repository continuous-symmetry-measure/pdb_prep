import os

from Geometry.distance import point_3d, distance


def print_results(results):
    line_tmpl = "{:<15} {:10} {:<9} {:<7} {:<7}    "

    header_tmpl = line_tmpl + "{:<8} {:<8} {:<8}    {:<8} {:<8} {:<8}      {}"
    line_tmpl = line_tmpl + "{:<+8.4f} {:<+8.4f} {:<+8.4f}    {:<+8.4f} {:<+8.4f} {:<+8.4f}      {:<11.4f}"

    print("", flush=True)
    print(header_tmpl.format("file", "atom_name", "model_num", "resname", "resseq",
                             "X1", "Y1", "Z1", "X2", "Y2", "Z2", "distance"))
    for rslt in results:
        (file, atom_name, model_number, resname, resseq, p1, p2, dist) = rslt

        print(
            line_tmpl.format(file,
                             atom_name,
                             model_number,
                             resname,
                             resseq,
                             float(p1.x), float(p1.y), float(p1.z),
                             float(p2.x), float(p2.y), float(p2.z),
                             dist)
        )


def dist_pairs(input_file, model_number, pairs_of_atoms):
    """

    :param model_number:
    :param pairs_of_atoms: list of eqvivalent atoms
    :return: results - a list of tuples[(atom_name, model_number, point1, point2, distance)()]
    """
    atom2point = lambda a: point_3d(a.x, a.y, a.z)
    short_file_name = os.path.basename(input_file)

    results = []
    for pair in pairs_of_atoms:
        point1, point2 = atom2point(pair[0]), atom2point(pair[1])
        # print (point1)
        # print (point2)
        dist = distance.between_points(point1, point2)
        # print (dist)
        curr_result = (
            short_file_name,
            pair[0].atom_name,
            model_number,
            pair[0].resname,
            pair[0].resseq,
            point1,
            point2,
            dist
        )
        results.append(curr_result)
    return results
