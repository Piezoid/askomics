import unittest
from datetime import date, time, datetime

from askomics.libaskomics.integration.turtle.element import *
from askomics.libaskomics.integration.turtle.literals import *
from askomics.libaskomics.integration.turtle.resource import *
from askomics.libaskomics.integration.turtle.writer import *

class ClassTests(unittest.TestCase):
    def test_class(self):
        class Test(Resource, uri='ex:Test'):
            p = FunctionalProperty('ex:p')
        t = Test('ex:t')
        self.assertIn(type(Test), Test.type)

        inst = Test('ex:test')
        self.assertIn(type(inst), inst.type)


class TestResource(unittest.TestCase):
    def test_constructor(self):
        r1 = Resource('ex:test')
        self.assertIsInstance(r1, Resource)

        r2 = Resource('ex:test')
        self.assertIsNot(r1, r2)
        self.assertIsNot(r1._data, r2._data)
        self.assertEqual(r1.id, r2.id)
        self.assertEqual(r1, r2)
        self.assertEqual(hash(r1), hash(r2))

        uri = r1.id
        self.assertIsInstance(uri, ResourceIdentifier)


class TestLiteral(unittest.TestCase):
    python_literals = [
        ('xsd:boolean', bool, True),
        ('xsd:integer', int, 1),
        ('xsd:decimal', float, 1.1),
        ('xsd:complex', complex, 1+1j),
        ('xsd:string', str, "str"),
        ('xsd:base64Binary', bytes, b'bytes'),
        ('xsd:dateTime', datetime, datetime(2005, 6, 26, 17, 30)),
        ('xsd:date', date, date(2016, 5, 26)),
        ('xsd:time', time, time(17,30)),
        ]

    def test_iso_literal(self):
        for xsdty, pyty, val in self.python_literals:
            l = Literal(val)
            self.assertIsInstance(l, Literal)
            self.assertIsInstance(l, Literal.get_class(xsdty))
            self.assertEqual(l.datatype, xsdty)

            s = str(l)
            self.assertIs(type(s), str)

            val_back = l.value
            self.assertIs(type(val_back), type(val))
            self.assertEqual(val_back, val)

    def test_python_type_subclass(self):
        "Test that Literal hierachy can learn about python types subclassing the registered ones."
        class T(int): pass
        self.assertNotIn(T, Literal._type2subclasses)

        lit = Literal(T(1))
        self.assertEqual(lit.datatype, 'xsd:integer')
        self.assertEqual(lit.value, 1)

        # type T is now registered by XSDinteger
        self.assertEqual(XSDinteger._type2subclasses[T], XSDinteger)
        # Information about T should have been propagated to the root of hierarchy
        self.assertEqual(Literal._type2subclasses[T], XSDinteger)




