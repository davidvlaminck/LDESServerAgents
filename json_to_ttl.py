from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, HttpUrl
from rdflib import Graph, RDF, URIRef, Literal, ConjunctiveGraph


class Agent(BaseModel):
    naam: str = Field(alias="purl:Agent.naam")
    vo_id: str = Field(alias="tz:Agent.voId")
    id: HttpUrl = Field(alias="@id")


class DataGraph(BaseModel):
    graph: List[Agent] = Field(alias="@graph")


if __name__ == '__main__':
    with open('/home/davidlinux/Documents/AWV/agents_full.json') as f:
        datax = json.load(f)
        agent_data = DataGraph(**datax)
        g = Graph()
        for index, agent in enumerate(agent_data.graph):
            h = Graph()
            h.add((URIRef(agent.id), RDF.type, URIRef('http://purl.org/dc/terms/Agent')))
            h.add((URIRef(agent.id), URIRef('https://tz.data.wegenenverkeer.be/ns/implementatieelement#Agent.voId'),
                   Literal(agent.vo_id)))
            h.add((URIRef(agent.id), URIRef('http://purl.org/dc/terms/Agent.naam'), Literal(agent.naam)))
            h.add((URIRef(agent.id), URIRef('https://www.w3.org/TR/prov-o/#generatedAtTime'),
                   Literal(datetime.utcnow() + timedelta(seconds=index))))
            g += h
        g.bind('tz', 'https://tz.data.wegenenverkeer.be/ns/implementatieelement#')
        g.bind('purl', 'http://purl.org/dc/terms/')
        g.bind('prov', 'https://www.w3.org/TR/prov-o/#')
        g.bind('asset', 'https://data.awvvlaanderen.be/id/asset/')

        g.serialize(destination=Path('agents_full.trig'), format='trig')

        for s, p, o in g:
            print(f'{s} {p} {o}')
