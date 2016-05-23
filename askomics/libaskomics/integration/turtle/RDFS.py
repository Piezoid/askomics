from .element import CURIE

# Classes
Resource      = CURIE('rdfs:Resource')
Class         = CURIE('rdfs:Class')
Literal       = CURIE('rdfs:Literal')
Datatype      = CURIE('rdfs:Datatype')
langString    = CURIE('rdf:langString')
HTML          = CURIE('rdf:HTML')
XMLLiteral    = CURIE('rdf:XMLLiteral')
Property      = CURIE('rdf:Property')
# Properties
type          = CURIE('rdf:type')
range         = CURIE('rdfs:range')
domain        = CURIE('rdfs:domain')
subClassOf    = CURIE('rdfs:subClassOf')
subPropertyOf = CURIE('rdfs:subPropertyOf')
label         = CURIE('rdfs:label')
comment       = CURIE('rdfs:comment')
