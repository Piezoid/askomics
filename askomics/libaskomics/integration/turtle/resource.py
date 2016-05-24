from operator import attrgetter
from collections import defaultdict

from .utils import refine_class
from . import RDFS
from .element import *

class Named:
    def __init__(self, uri=None, **kwargs):
        if uri is not None:
            uri = ObjectIdentifier(uri)
        else:
            #print('New bnode for %r' % type(self))
            uri = BNode(self)
        self._id = uri
        #print('{.__name__}.__init__({!r},{!r})'.format(Named, self, uri))

    @property
    def id(self):
        return self._id

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if isinstance(other, Named):
            return self._id == other._id
        else:
            return False

    def __repr__(self):
        if isinstance(self.id, BNode) and hasattr(self, '__qualname__'):
            return "{0.__class__.__qualname__}({0.id!r}->{0.__qualname__})".format(self)
        else:
            return "{0.__class__.__qualname__}({0.id!r})".format(self)

    def __str__(self):
        return self._id



class heap_type(type): pass

class Resource:
    def __init__(self, **kwargs):
        self._data = defaultdict(set)
        pass


    def _mkpseudoprop(name):
        def fget(self):
            return self._data[name]
        def fset(self, x):
            self._data[name].add(x)
        return property(fget=fget, fset=fset)
    label = _mkpseudoprop(RDFS.label)
    comment = _mkpseudoprop(RDFS.comment)
    type = _mkpseudoprop(RDFS.type)
    subClassOf = _mkpseudoprop(RDFS.subClassOf)
    del _mkpseudoprop


class Class(Resource, type, metaclass=heap_type):
    _id = CURIE('rdfs:Class')
    #def __new__(meta, name, bases, dct):
        ## Substitute the class uri with an accesor for the instance's uri
        #try:
            #dct['_id'] = ObjectIdentifier(dct.pop('uri'))
        #except KeyError:
            #pass
        #cls = super().__new__(meta, name, bases, dct)
        #return cls

    def __new__(meta, name, bases, dct, **kwargs):
        dct.setdefault('_data', defaultdict(set))
        return type.__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct, **kwargs):
        #print('{.__name__}.__init__({!r})'.format(Class, cls))

        type.__init__(cls, name, bases, dct) #FIXME: try super()
        Resource.__init__(cls, **kwargs)

        for base in bases:
            if isinstance(base, Resource):
                cls.subClassOf = base
        cls.label = name
        if '__doc__' in dct:
            cls.comment = dct['__doc__']

        cls._uri2classes = {}
        for parent in cls.__mro__: # cls and all it's indirect bases
            if hasattr(parent, '_uri2classes'):
                parent._uri2classes[cls.id] = cls

    @classmethod
    def get_class(meta, uri):
        return meta._uri2classes[uri]

    def __instancecheck__(cls, resource):
        assert issubclass(cls, Resource)
        if type.__instancecheck__(Resource, resource):
            if type.__instancecheck__(cls, resource):
                return True
            else:
                subclass_uris = cls._indentifier2classes
                return any(ty in subclass_uris for ty in resource.type)
        else:
            return False
Class.__class__ = Class
del heap_type

class Resource(Named, metaclass=Class):
    "The class resource, everything."
    _data = defaultdict(set)
    def __new__(cls, uri=None, **kwargs):
        #print('{.__name__}.__new__({.__name__},{!r})'.format(Resource, cls, uri))
        cls = object.__new__(cls)
        cls._data = defaultdict(set)
        return cls

    def __init__(self, *args, **kwargs):
        Named.__init__(self, *args, **kwargs)
        #print('{.__name__}.__init__({!r})'.format(Resource, self))
        self.type = type(self)

    def __iter__(self):
        def convert_object(obj):
            if isinstance(obj, TurtleElement):
                return obj
            elif isinstance(obj, Resource):
                return obj.id
            else:
                raise TypeError('%r is neither a TurtleElement or a Literal')
                #return literals.Literal(obj)

        for predicate, objects in self._data.items():
            if type(objects) is set:
                if len(objects) == 1:
                    objects = convert_object(next(iter(objects)))
                else:
                    objects = { convert_object(obj) for obj in objects }
                yield (predicate, objects)
            else:
                yield (predicate, convert_object(objects))



class PropertyAccessError(AttributeError): pass

class Property(Resource, uri=RDFS.Resource):
    def __set__(self, resource, new_object):
        if type(new_object) is set:
            resource._data[self.id] = new_object
        else:
            resource._data[self.id].add(new_object)

    def __get__(self, resource, rtype):
        if resource is None:
            assert False
            return self
        return resource._data[self.id]



Class.__bases__ = (Resource, type)

class Resource(metaclass=refine_class):
    label = Property(RDFS.label)
    comment = Property(RDFS.comment)
    type = Property(RDFS.type)

class Class(metaclass=refine_class):
    subClassOf = Property(RDFS.subClassOf)

Resource.__init__(Class, uri=RDFS.Class)
Resource.__init__(Resource, uri=RDFS.Resource)
Resource.__init__(Property, uri=RDFS.Property)


class Property(metaclass=refine_class):
    range = Property(uri=RDFS.range)
    domain = Property(uri=RDFS.domain)


class FunctionalProperty(Property, uri=CURIE('owl:FunctionalProperty')):
    def __get__(self, obj, objtype):
        try:
            v = obj._data[self.id]
            if __debug__:
                if isinstance(v, set):
                    raise PropertyAccessError(
                        '{obj:r} has many values for the functional property {self:r}'\
                        .format(locals()))
        except KeyError:
            raise PropertyAccessError(
                '{obj:r} has no property {self:r}'.format_map(locals()))

        return v


class DatatypeProperty(Property, uri='owl:DatatypeProperty'):
    pass
