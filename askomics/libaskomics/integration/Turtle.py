
from io import StringIO
from collections import defaultdict
from pprint import pformat

from tempfile import NamedTemporaryFile


class Serializeable:
    """
    Abstract base class providing a common interface for serialization to strings
    and temporary files.
    Implementation must define serialize and pretty_serialize.
    """
    def serialize(self, write):
        """Dense serialization.
        write is a function called to add text fragments to the result.
        """
        raise NotImplementedError("Serializeable is an abstract class")

    def pretty_serialize(self, write):
        """Pretty serialization.
        write is a function called to add text fragments to the result.
        """
        raise NotImplementedError("Serializeable is an abstract class")

    def __str__(self):
        "str(Serializeable) returns a pretty printed serialization"
        s = StringIO()
        self.pretty_serialize(s.write)
        return s.getvalue()

    def dense_str(self):
        "Like str(self), but return a dense serialization if optimizations are enabled"
        s = StringIO()
        if __debug__:
            self.pretty_serialize(s.write)
        else:
            self.serialize(s.write)
        return s.getvalue()

    def tmpfile(self, mktemp=NamedTemporaryFile):
        "Create a temporary file, writes the serialization and returns the descriptor."
        tmpf = mktemp(mode='wt')
        if __debug__:
            #NOTE: using the write on the underlying file (tmpf.file.write) instead of tmpf.write
            # is three time faster for this usage (lots of calls).
            self.pretty_serialize(tmpf.file.write)
        else:
            self.serialize(tmpf.file.write)
        tmpf.flush()
        return tmpf


class TurtleResource(Serializeable):
    __slots__ = ('_uri', '_ns', '_data')
    def __init__(self, uri, namespace=None, data=None):
        self._uri = uri
        self._ns = namespace
        self._data = dict() if data is None else data

    def __repr__(self):
        if isinstance(self._data, dict):
            return "{0.__class__.__qualname__}({0._uri}, data={1})".format(self, pformat(self._data))
        else:
            return "{0.__class__.__qualname__}({0._uri})".format(self)

    def __iter__(self):
        "iterator over (predicate, objects) tuples"
        items = self._data
        if type(items) is dict:
            items = items.items()
        return iter(items)

    def __setitem__(self, predicate, obj):
        """
        Add a predicate, object couple to the resources.
        Multiple assignments with the same predicate differ from python normal semantics
        in the sense that it only add the object to the set of objects and doesn't mutate it.

        After the first assignment the objects collection is the singleton :
        >>> r = TurtleResource('subject')
        >>> r['predicate1'] = 'object1'
        >>> r['predicate1']
        'object1'

        After the second assignment the objects collection is a set
        >>> r['predicate2'] = 'object2'
        >>> r['predicate2'] = 'object3'
        >>> assert isinstance(r['predicate2'], set)
        >>> sorted(r['predicate2'])
        ['object2', 'object3']

        To directly mutate the set of objects, assign a set:
        >>> r['predicate2'] = {'object4', 'object5'}
        >>> sorted(r['predicate2'])
        ['object4', 'object5']
        """
        # To avoid storing a set of objects for each predicate, the first object
        # associated with a predicate is stored as value in self._data, the second
        # is stored with the first in a set, and the next ones are added to this set.
        d = self._data
        old = d.get(predicate)
        if old is None or type(obj) is set:
            d[predicate] = obj
        elif type(old) is set:
            old.add(obj)
        else:
            d[predicate] =  {old, obj}

    def __getitem__(self, predicate):
        "Subcription with a predicate might return an object or a set of objects or raise KeyError."
        return self._data[predicate]

    # Equality and hash based on uri
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return other._uri == self._uri
        else:
            return False

    def __hash__(self):
        return hash(self._uri)

    def update(self, other):
        "Merge other resource in self"
        assert self == other # Verify that URIs matches
        d = self._data
        for predicate, objects in other:
            our_objects = d.get(predicate)
            if our_objects is None:
                d[predicate] = objects
            else:
                if type(our_objects) is not set:
                    our_objects = {our_objects}
                    d[predicate] = our_objects

                if type(objects) is set:
                    our_objects.update(objects)
                else:
                    our_objects.add(objects)

    def pretty_serialize(self, write):
        uri = self._uri

        # Precompute newline sequence
        newline = '\n' + ' ' * (len(uri) - 1)

        it = iter(self)

        # First subjet predicate pair
        predicate, objects = next(it)
        write(uri)
        write(' ')
        write(predicate)
        write(' ')
        if type(objects) is str:
            write(objects)
        else:
            pretty_serialize_objects(objects, write, newline + ' ' * len(predicate) + ' , ')

        newpred = newline + '; ' # Precompute line indentation for new predicate
        for predicate, objects in it:
            write(newpred)
            write(predicate)
            write(' ')
            if type(objects) is str:
                write(objects)
            else:
                pretty_serialize_objects(objects, write, newline + ' ' * len(predicate) + ' , ')

        write(' .\n\n')

    def serialize(self, write):
        uri = self._uri

        it = iter(self) # iterator over (predicate, objects) tuples

        # First subjet predicate pair
        predicate, objects = next(it)
        write(uri)
        write(' ')
        write(predicate)
        write(' ')
        if type(objects) is str:
            write(objects)
        else:
            serialize_objects(objects, write)

        for predicate, objects in it:
            write(';')
            write(predicate)
            write(' ')
            if type(objects) is str:
                write(objects)
            else:
                serialize_objects(objects, write)

        write('.')


class NameSpace(dict):
    def serialize(self, write):
        pass


class TurtleFile(Serializeable):
    __slots__ = ('_resources', '_ns')

    def __init__(self, namespace=None, resources=None):
        self._ns = NameSpace() if namespace is None else namespace
        self._resources = dict() if resources is None else resources

    def add(self, resource):
        """
        Add a resource to the TurtleFile.
        The TurtleFile instance must use a dictionary to store its date (default constructor)
        If the resource already present, the new triples are merged with it.
        :return: the original resource, or the updated resource if a merge occurred.
        """
        if __debug__: # Peephole branch optimization, like assert
            if not isinstance(self._resources, dict):
                raise TypeError("Adding resources to TurtleFile is only supported with dict-like resources collection")
            if not isinstance(resource, TurtleResource):
                raise TypeError("Only resources can be added to TurtleFile")

        r_uri = resource._uri
        r_ns = resource._ns # The resource prefixes
        ns = self._ns # Our prefixes
        rs = self._resources

        our_resource = rs.get(r_uri)
        if our_resource is None: # The resource is not present
            rs[uri] = resource
            # Merge the resources prefixes (if any)
            if r_ns is not None and r_ns is not ns:
                ns.update(r_ns)
            resource._ns = r_ns # Share the prefixes now that the resource is internalized
            return resource
        else: # The resource is already present
            assert our_resource._ns is ns # Prefixes will be merged by our_resource.update
            our_resource.update(resource)
            return our_resource

    def update(self, other):
        for resource in other:
            self.add(resource)

    def __getitem__(self, obj):
        if __debug__:
            if not isinstance(self._resources, dict):
                raise TypeError("TurtleFile subcription only supported with dict-like resources collection")
        rs = self._resources
        r = rs.get(obj)
        if r is None:
            r = TurtleResource(obj, self._ns)
            rs[obj] = r
        return r

    def __iter__(self):
        "Iterate over TurtleResources"
        d = self._resources
        if isinstance(d, dict):
            return iter(d.values())
        else:
            return iter(d)

    def serialize(self, write):
        self._ns.serialize(write)
        for r in self:
            r.serialize(write)

    def pretty_serialize(self, write):
        self._ns.serialize(write)
        for r in self:
            r.pretty_serialize(write)


def pretty_serialize_objects(objects, write, newline):
    objects = iter(objects)
    write(next(objects))

    for object in objects:
        write(newline)
        write(object)

def serialize_objects(objects, write):
    objects = iter(objects)
    write(next(objects))

    for object in objects:
        write(',')
        write(object)


#import random

#alph = ''.join(chr(c) for c in range(ord('a'), ord('z')))

#strings = [''.join(random.choice(alph) for i in range(random.randint(5, 30)))
           #for i in range(30)
           #]

#tf = TurtleFile()


#for i in range(10000):
    #r = tf[''.join(random.choice(alph) for i in range(random.randint(5, 30)))]
    #for j in range(100):
        #r[random.choice(strings)] = random.choice(strings)

#def test():
    #s = StringIO()
    #r.serialize(s.write)
    #return s.getvalue()

#def test2():
    #s = ''
    #def write(i):
        #nonlocal s
        #s += i
    #r.serialize(write)
    #return s

#def ptest():
    #s = StringIO()
    #r.pretty_serialize(s.write)
    #return s.getvalue()

#def ptest2():
    #s = ''
    #def write(i):
        #nonlocal s
        #s += i
    #r.pretty_serialize(write)
    #return s

#def ptest3():
    #r.pretty_serialize(open('/tmp/out', 'wt').write)

#def test3():
    #r.serialize(open('/tmp/out', 'wt').write)

