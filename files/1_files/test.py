import unittest
import json

class TestStringMethods(unittest.TestCase):

    def test_test_func(self):
        self.assertEqual('test', test_func('test'))

    def test_upper(self):
        self.assertNotEquals('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertFalse('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)