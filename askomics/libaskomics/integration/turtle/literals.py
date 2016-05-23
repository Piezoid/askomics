from codecs import unicode_escape_decode
import base64
from datetime import date, time, datetime


from .element import TurtleElement, CURIE
from .resource import Class


NoneType = type(None)

class XSDMeta(Class):
    #@classmethod
    uri2class = {}
    def __new__(meta, name, bases, dct, **kwargs):
        dct.update({'__slots__' : ()})
        return super().__new__(meta, name, bases, dct, **kwargs)

    def __init__(cls, name, bases, dct, uri=None, **kwargs):
        if uri is None and name.startswith('XSD'):
            uri = CURIE('xsd', name[3:])

        super().__init__(name, bases, dct, uri=uri, **kwargs)

        python_type = dct.get('python_type', NoneType)
        cls._type2subclasses = {}
        if python_type is not NoneType:
            cls.register_python_type(python_type)


    def register_python_type(cls, python_type):
        "Declare that cls can be instantiated from python_type and its subclasses"
        assert isinstance(python_type, type)
        meta = type(cls)
        for parent in cls.__mro__: # All indirect bases
            if isinstance(parent, meta): # select only classes with XSDMeta metaclass
                    parent._type2subclasses[python_type] = cls

class Literal(TurtleElement, metaclass=XSDMeta):
    """Base class of XSD Literals.
    Literals are a str object encoding XSD values. This class can be instantiated with a turtle str (with " quotes included).

    Literal() finds the subclass matching the datatype :
    >>> Literal('"1+1j"^^xsd:complex')
    XSDcomplex("1+1j")
    >>> str(_) # turtle literal is still there :
    '"1+1j"^^xsd:complex'
    >>> XSDcomplex(_) # instantiate with the subclass directly
    XSDcomplex("1+1j")

    Some subclasses provides an isomorphism to Python values :
    >>> XSDboolean('"true"').value # turtle literal -> Python
    True
    >>> str(XSDboolean(not _)) # Python -> turtle literal
    '"false"^^xsd:boolean'

    Literal() also deduces the subclass when constructed from a python object.
    >>> Literal(datetime(2016, 5, 17, 20, 7, 24))
    XSDdateTime("2016-05-17T20:07:24")

    """
    def __new__(cls, value):
        value_type = type(value)
        if issubclass(value_type, Literal):
            if issubclass(value_type, cls):
                return value # Pass-through
            elif issubclass(cls, value_type): # Specialization
                return cls.__new__(cls, value.value)
            else:
                raise TypeError("Can't specialize {!r} to {}".format(value, cls))
        else:
            if isinstance(value, str) and value[0] == '"':
                # We get a preformatted rdf literal
                quotedvalue, dt, datatype = value.partition('^^')
                assert quotedvalue[-1] == '"'
                if datatype != cls.id:
                    if datatype:
                        cls = cls._uri2classes.get(datatype)
                        if cls is None:
                            raise TypeError("{} is not a subclass of {}".format(datatype, cls))
                    else:
                        # Default is XSDString for abstract classes
                        if cls.id is NoneType:
                            cls = XSDstring
                        else: # or keep the the invoked class
                            value = '%s^^%s' % (quotedvalue, cls)

            else:
                # Constructing from a python type (including unquoted strs)
                if not issubclass(value_type, cls.python_type):
                    # Find a subclass accepting this type (exact match)
                    subclass = cls._type2subclasses.get(value_type)
                    if subclass is None:
                        # Slow path: scan cls subclasses for one accepting a superclass of value_type
                        for super_value_type, datatype in cls._type2subclasses.items():
                            if issubclass(value_type, super_value_type):
                                # caches the result in the datatype class found and its superclasses
                                datatype.register_python_type(value_type)
                                subclass = datatype
                                break

                    if subclass is None:
                        raise TypeError("{} can't be constructed from {}".format(cls, type(value)))
                    cls = subclass
                    assert issubclass(value_type, cls.python_type)

                value = repr(cls.toXSDstr(value))[1:-1].replace('"', '\\"')

                if cls is XSDstring:
                    value = '"%s"' % value
                else:
                    value = '"%s"^^%s' % (value, cls)

        # Make a str typed as cls
        return str.__new__(cls, value)

    def __repr__(self):
        return '{0.__class__.__name__}({0.value_quoted})'.format(self)

    @property
    def datatype(self):
        return type(self).id

    @property
    def value_quoted(self):
        'Escaped value with " quotes.'
        return self.partition('^^')[0]

    @property
    def value_str(self):
        "unescaped string"
        return unicode_escape_decode(self.partition('^^')[0][1:-1])[0]

    #
    # Subclass override the following attributes :
    #

    # if not NoneType, python_type instances can be converted from the class
    python_type = NoneType

    # Classmethod or staticmethod that converts python from python_type to unescaped string
    toXSDstr = staticmethod(str) # Default to str()

    @property
    def value(self):
        "The python value"
        # default to python_type()
        if __debug__:
            return self.python_type(self.value_str)
        else: # Inlined version
            return self.python_type(unicode_escape_decode(self.partition('^^')[0][1:-1])[0])

class XSDstring(Literal): python_type = str

class XSDnormalizedString(XSDstring): pass
class XSDtoken(XSDnormalizedString): pass
class XSDlanguage(XSDtoken): pass

class XSDName(XSDtoken): pass
class XSDNCName(XSDName): pass
class XSDID(XSDNCName): pass
class XSDIDREF(XSDNCName): pass
class XSDENTITY(XSDNCName): pass


class XSDdecimal(Literal):
    python_type = float
    def __float__(self):
        return float(self.value_str)

class XSDdouble(XSDdecimal): pass
class XSDfloat(XSDdouble): pass

class XSDinteger(XSDdecimal):
    python_type = int
    def __int__(self):
        return int(self.value_str)

class XSDlong(XSDinteger): pass
class XSDint(XSDlong): pass
class XSDshort(XSDint): pass
class XSDbyte(XSDshort): pass
class XSDboolean(XSDbyte):
    python_type = bool
    toXSDstr = staticmethod(lambda b: "true" if b else "false")
    @property
    def value(self):
        s = self.value_str
        if s == "true":
            return True
        elif s == "false":
            return False
        else:
            raise ValueError("{} is not a valid XSDboolean".format(s))

    def __bool__(self):
        return self.value



class XSDnonPositiveInteger(XSDinteger): pass
class XSDnegativeInteger(XSDnonPositiveInteger): pass

class XSDnonNegativeInteger(XSDinteger): pass
class XSDpositiveInteger(XSDnonNegativeInteger): pass

class XSDunsignedLong(XSDnonNegativeInteger): pass
class XSDunsignedInt(XSDunsignedLong): pass
class XSDunsignedShort(XSDunsignedInt): pass
class XSDunsignedByte(XSDunsignedShort): pass

class XSDcomplex(Literal):
    python_type = complex
    def __complex__(self):
        return complex(self.value_str)


class XSDdateTime(Literal):
    python_type = datetime
    toXSDstr = staticmethod(lambda value: value.isoformat().partition('.')[0])
    value = property(lambda self: datetime.strptime(self.value_str, '%Y-%m-%dT%H:%M:%S'))

class XSDdate(XSDdateTime):
    python_type = date
    toXSDstr = staticmethod(lambda value: value.isoformat())
    value = property(lambda self: datetime.strptime(self.value_str, '%Y-%m-%d'))

class XSDtime(XSDdateTime):
    python_type = time
    value = property(lambda self: datetime.strptime(self.value_str, '%H:%M:%S'))

class XSDbase64Binary(Literal):
    python_type = bytes
    toXSDstr = staticmethod(lambda value: base64.b64encode(value).decode('ascii'))
    value = property(lambda self: base64.b64decode(self.value_str))


__all__ = [k for k,v in globals().items() if type(v) is XSDMeta]
