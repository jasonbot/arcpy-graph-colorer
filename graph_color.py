import collections
import itertools
import random

import arcpy

def build_graph(feature_class, id_field="OID@"):
    graph = collections.defaultdict(set)

    with arcpy.da.SearchCursor(feature_class, ("SHAPE@", id_field)) as cur:
        for s1, s2 in itertools.combinations(cur, 2):
            if not s1[0].disjoint(s2[0]):
                graph[s1[1]].add(s2[1])
                graph[s2[1]].add(s1[1])
            else:
                # Force-initialize nodes without links
                graph[s1[1]]
                graph[s2[1]]
    return graph

def greedy_color(graph, colors, invalidate_neighbors):
    for n_id, links in sorted(graph.items(), key=lambda x: (x[0], -len(x[1]))):
        color = colors[n_id]
        while color == 0 or any( (colors[link] == color) for link in links):
            color += 1
        colors[n_id] = color
        if colors[n_id] >= 5:
            if invalidate_neighbors:
                colors[n_id] = 0
                for neighbor in graph[n_id]:
                    colors[neighbor] = 0

def traverse_graph(graph):
    colors = { id: 0 for id in graph }
    greedy_color(graph, colors, True)
    num_tries = 1
    while any(color == 0 for color in colors.values()) and num_tries <= len(colors):
        arcpy.AddMessage("Repainting ({} of {})".format(num_tries, len(colors)))
        items = list(graph.items())
        random.shuffle(items)
        for n_id, links in items:
            if colors[n_id] == 0:
                color = 4
                while color > 0 or any((colors[link] == color) for link in links):
                    color -= 1
                if color <= 0:
                    color = 0
                    for neighbor in graph[n_id]:
                        colors[neighbor] = 0
                colors[n_id] = color
        num_tries += 1

    if any(color == 0 for color in colors.values()):
        greedy_color(graph, colors, False)
    return colors

def color_feature_class(feature_class, field_to_populate, coloring,
                        id_field="OID@"):
    with arcpy.da.UpdateCursor(feature_class, (id_field,
                                               field_to_populate)) as cur:
        for row in cur:
            row[1] = coloring.get(row[0], 1)
            cur.updateRow(row)

def graph_color(feature_class, field_to_populate, id_field="OID@"):
    arcpy.AddMessage("Building graph")
    graph = build_graph(feature_class, id_field)

    arcpy.AddMessage("Traversing graph")
    coloring = traverse_graph(graph)

    arcpy.AddMessage("Updating color field")
    color_feature_class(feature_class, field_to_populate, coloring, id_field)

if __name__ == '__main__':
    test = graph_color(arcpy.GetParameterAsText(0),
                       arcpy.GetParameterAsText(1))
