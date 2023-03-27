from pathlib import Path
from typing import List

from rdflib import Graph, URIRef


class LDESServer:
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.load()
        self.g: Graph = None

    def load(self):
        self.g = Graph()
        self.g.parse(source=self.source_path, format='turtle')
        #self.print_graph()

        id_timestamps = self.g.subject_objects(predicate=URIRef('https://www.w3.org/TR/prov-o/#generatedAtTime'))
        sorted_ids = list(map(lambda x: x[0], sorted(id_timestamps, key=lambda x: x[1])))
        print(sorted_ids)
        self.create_graph_by_ids(graph=self.g, list_of_ids=sorted_ids)

    def create_graph_by_ids(self, graph: Graph, list_of_ids: List[URIRef]):
        h = Graph()
        for id_uri in list_of_ids:
            for triple in graph.predicate_objects(subject=id_uri):
                pass

    def print_graph(self, graph: Graph):
        for s, p, o in graph:
            print(f'{s} {p} {o}')


if __name__ == '__main__':
    LDESServer(Path('agents_full.ttl'))


