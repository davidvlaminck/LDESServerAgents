import random
import string
import uuid
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, HttpUrl
from rdflib import Graph, RDF, URIRef, Literal, ConjunctiveGraph, Dataset, BNode


class Agent(BaseModel):
    naam: str = Field(alias="purl:Agent.naam")
    vo_id: str = Field(alias="tz:Agent.voId")
    id: HttpUrl = Field(alias="@id")


class DataGraph(BaseModel):
    graph: List[Agent] = Field(alias="@graph")


if __name__ == '__main__':
    with open('/home/davidlinux/Documents/AWV/agents_full.json') as f:
        datax = json.load(f)
        agent_data = DataGraph(**datax).graph
        g = Dataset()
        for index, agent in enumerate(sorted(list(agent_data), key=lambda x: x.vo_id)):
            timestamp = datetime.utcnow() + timedelta(seconds=index)
            timestamp_str = str(timestamp).replace(' ', 'T')
            h = URIRef(f'{agent.id}/{timestamp_str}')
            g.add((URIRef(agent.id), RDF.type, URIRef('http://purl.org/dc/terms/Agent'), h))
            g.add((URIRef(agent.id),
                   URIRef('https://tz.data.wegenenverkeer.be/ns/implementatieelement#Agent.voId'),
                   # Literal(agent.vo_id),
                   Literal(uuid.uuid4()),
                   h))
            g.add((URIRef(agent.id), URIRef('http://purl.org/dc/terms/Agent.naam'), Literal(agent.naam), h))
            g.add((URIRef(agent.id), URIRef('https://www.w3.org/TR/prov-o/#generatedAtTime'),
                   Literal(timestamp), h))
            'http://purl.org/dc/terms/Agent.contactinfo'
            contact_node = BNode()
            g.add((URIRef(agent.id), URIRef('http://purl.org/dc/terms/Agent.contactinfo'), contact_node, h))
            random_email = ''.join(random.choices(string.ascii_lowercase, k=5)) + '@' + ''.join(random.choices(string.ascii_lowercase, k=5)) + '.be'
            g.add((contact_node, URIRef('http://schema.org/email'), Literal(random_email), h))
            random_phone = '0' + ''.join(random.choices(string.digits, k=9))
            g.add((contact_node, URIRef('http://schema.org/telephone'), Literal(random_phone), h))

        g.bind('tz', 'https://tz.data.wegenenverkeer.be/ns/implementatieelement#')
        g.bind('purl', 'http://purl.org/dc/terms/')
        g.bind('prov', 'https://www.w3.org/TR/prov-o/#')
        g.bind('asset', 'https://data.awvvlaanderen.be/id/asset/')
        g.bind('schema', 'http://schema.org/')

        g.serialize(destination=Path('agents_full.nq'), format='nquads')
        g.serialize(destination=Path('agents_full.trig'), format='trig')

        for s, p, o, c in g:
            print(f'{s} {p} {o} {c}')
