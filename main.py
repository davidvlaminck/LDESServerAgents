from pathlib import Path
from typing import List

from rdflib import Graph, URIRef, Dataset, RDF, Literal, XSD


class LDESServer:
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.load()
        self.d: Dataset = None

    def load(self):
        self.d = Dataset()
        self.d.parse(source=self.source_path, format='trig')

        timestamp_quads = [q for q in self.d.quads(
            (None, URIRef('https://www.w3.org/TR/prov-o/#generatedAtTime'), None, None))]

        sorted_ids = list(map(lambda x: x[3], sorted(timestamp_quads, key=lambda x: x[2])))
        partial_set = self.create_partial_graph_by_contexts(graph=self.d, list_of_contexts=sorted_ids)
        base_ldes = self.create_ldes_fragment_from_partial_set(partial_set)

    @staticmethod
    def create_partial_graph_by_contexts(graph: Dataset, list_of_contexts: List[URIRef], size: int = 100) -> Dataset:
        h = Dataset()
        for context_uri in list_of_contexts[0:size-1]:
            for q in graph.quads((None, None, None, context_uri)):
                h.add(q)
        #self.print_graph(h)
        print(len(list(h.contexts())))
        return h

    @staticmethod
    def print_graph(graph: Graph):
        for s, p, o in graph:
            print(f'{s} {p} {o}')

    @staticmethod
    def print_dataset(dataset: Dataset):
        for s, p, o, c in dataset:
            print(f'{s} {p} {o} {c}')

    def create_ldes_fragment_from_partial_set(self, partial_set: Dataset):
        g = Graph()
        g.bind('ldes', 'https://w3id.org/ldes#')
        g.bind('tree', 'https://w3id.org/tree#')
        g.bind('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        g.bind('sh', 'http://www.w3.org/ns/shacl#')
        g.bind('xsd', 'http://www.w3.org/2001/XMLSchema#')
        g.bind('hydra', 'http://www.w3.org/ns/hydra/core#')
        g.bind('dct', 'http://purl.org/dc/terms/')
        g.bind('prov', 'http://www.w3.org/ns/prov#')

        ldes_uri = URIRef('https://example.com/ldes')
        g.add((ldes_uri, RDF.type, URIRef('https://w3id.org/ldes#EventStream')))
        # TODO shape
        for context in partial_set.contexts():
            if context.identifier == URIRef('urn:x-rdflib:default'):
                continue
            id, timestamp = str(context.identifier).rsplit('/', 1)
            g.add((ldes_uri, URIRef('https://w3id.org/tree#member'), context.identifier))
            g.add((context.identifier, URIRef('http://purl.org/dc/terms/isVersionOf'), URIRef(id)))
            g.add((context.identifier, URIRef('http://www.w3.org/ns/prov#generatedAtTime'),
                   Literal(timestamp + 'Z', datatype=XSD.dateTime)))
            for triple in partial_set.quads((None, None, None, context)):
                if triple[0] == URIRef(id):
                    g.add((context.identifier, triple[1], triple[2]))
                else:
                    g.add((triple[0], triple[1], triple[2]))

        self.print_graph(g)
        g.serialize(destination=Path('temp.ttl'), format='ttl')


if __name__ == '__main__':
    LDESServer(Path('agents_full.trig'))
