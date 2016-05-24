from urllib.parse import quote, unquote


__all__ = ['TurtleElement',
           'ObjectIdentifier',
           'CURIE',
           'URI',
           'BNode']

class TurtleElement(str):
    """A thin wrapper around str that represent a turtle syntax element (the object EBNF subtree). The original string is conserved, and returned by element
    The constructor accept turtle's object syntax and detect the correct subclass.
    >>> TurtleElement('ex:diff%20mRNA')
    CURIE('ex:diff%20mRNA')
    >>> _.value
    'diff mRNA'
    >>> TurtleElement('<http://example.com/diff%20mRNA>')
    URI('<http://example.com/diff%20mRNA>')


    Directly instantiating subclasses allows to produce specific elements from python values:
    >>> CURIE('plop')
    CURIE(':plop')
    >>> from .literals import Literal
    >>> Literal(True)
    XSDboolean("true")

    """
    __slots__ = ()

    def __repr__(self):
        return "{0.__class__.__qualname__}({1})".format(self, str.__repr__(self))

    # For subclass deriving directly from TurtleElement, provides a way to recover
    # the concrete element
    @property
    def element(self):
        return self


class ObjectIdentifier(TurtleElement):
    "URI, CURIE and BNode"
    __slots__ = ()
    def __new__(cls, s):
        "Constructor delegating to URI and CURIE"
        if isinstance(s, cls):
            return s
        elif s[0] == '<' and s[-1] == '>':
            cls = URI
        elif ':' in s:
            if s.startswith('_:'):
                cls = BNode
            else:
                cls = CURIE
        else:
            raise ValueError("ObjectIdentifier can only construct URI, CURIE and BNode")

        return str.__new__(cls, s)

    @property
    def id(self):
        return self

class URI(ObjectIdentifier):
    __slots__ = ()
    def __new__(cls, uri):
        if isinstance(uri, URI):
            return uri
        elif uri[0] == '<' and uri[-1] == '>':
            pass # Construction from formatted URI
        else:
            assert '<' not in uri and '>' not in uri
            uri = '<%s>' % uri
        return str.__new__(cls, uri)

    @property
    def uri(self):
        return self[1:-1]

class CURIE(ObjectIdentifier):
    __slots__ = ()
    def __new__(cls, prefix, ident=None):
        if isinstance(prefix, CURIE):
            return prefix

        if ident is None: # One arg case, prefix may be a preformatted CURIE
            s = prefix
            prefix, colon, ident = s.partition(':')
            if not colon: # else :
                prefix = ''
                ident = s
        else:
            assert ':' not in prefix

        s = '%s:%s' % (prefix, quote(ident))
        return str.__new__(cls, s)

    @property
    def args(self):
        prefix, semic, ident = self.partition(':')
        assert semic
        return prefix, unquote(ident)

    prefix = property(lambda self: self.args[0])
    value = property(lambda self: self.args[1])


class BNode(ObjectIdentifier):
    "Blank TurtleElement"
    def __new__(cls, s):
        if isinstance(s, str):
            if not s.startswith('_:'):
                s = '_:' + quote(s)
        else:
            s = '_:%d' % id(s)
        return str.__new__(cls, s)

    @property
    def bident(self):
        return unquote(self[2:])


