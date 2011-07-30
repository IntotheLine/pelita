# -*- coding: utf-8 -*-

import unittest
from numbers import Number
import json
from pelita.containers import *
from pelita.messaging.json_convert import json_converter
from pelita.datamodel import MazeComponent

class TestMesh(unittest.TestCase):

    def test_init(self):
        m = Mesh(2, 2)
        self.assertEqual(m.values(), [None, None, None, None])
        self.assertEqual(m.shape, (2, 2))
        m = Mesh(0, 0)
        self.assertEqual(m.values(), [])
        self.assertEqual(m.shape, (0, 0))
        m = Mesh(1, 4)
        self.assertEqual(m.values(), [None, None, None, None])
        self.assertEqual(m.shape, (1, 4))
        m = Mesh(4, 1)
        self.assertEqual(m.values(), [None, None, None, None])
        self.assertEqual(m.shape, (4, 1))

    def test_indices(self):
        m = Mesh(2, 3)
        target = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]
        self.assertEqual(target, m.keys())

    def test_index_linear_to_tuple(self):
        m = Mesh(3, 4)
        for (i, (x, y)) in enumerate(m.iterkeys()):
            self.assertEqual(m._index_linear_to_tuple(i), (x, y))

    def test_index_tuple_to_linear(self):
        m = Mesh(3, 4)
        for (i, (x, y)) in enumerate(m.iterkeys()):
            self.assertEqual(m._index_tuple_to_linear((x, y)), i)

    def test_getitem(self):
        m = Mesh(2, 2)
        m._data = [1, 2, 3, 4]
        self.assertEqual(m[0, 0], 1)
        self.assertEqual(m[1, 0], 2)
        self.assertEqual(m[0, 1], 3)
        self.assertEqual(m[1, 1], 4)
        self.assertRaises(IndexError, m.__getitem__, (3, 0))
        self.assertRaises(IndexError, m.__getitem__, (-1, 0))
        self.assertRaises(IndexError, m.__getitem__, (0, 3))
        self.assertRaises(IndexError, m.__getitem__, (0, -1))

    def test_setitem(self):
        m = Mesh(2, 2)
        m[0, 0] = 1
        m[1, 0] = 2
        m[0, 1] = 3
        m[1, 1] = 4
        self.assertEqual(m._data, [1, 2, 3, 4])
        self.assertRaises(IndexError, m.__setitem__, (3, 0), 1)
        self.assertRaises(IndexError, m.__setitem__, (-1, 0), 1)
        self.assertRaises(IndexError, m.__setitem__, (0, 3), 1)
        self.assertRaises(IndexError, m.__setitem__, (0, -1), 1)

    def test_iter(self):
        m = Mesh(2, 3)
        self.assertEqual([i for i in m], [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)])

    def test_set_data(self):
        m = Mesh(2, 2)
        m._set_data([1, 2, 3, 4])
        self.assertEqual(m.values(), [1, 2, 3, 4])
        self.assertRaises(TypeError, m._set_data, 'abcd')
        self.assertRaises(ValueError, m._set_data, [1, 2, 3])

    def test_init_data(self):
        m = Mesh(2, 2, data=[1, 2, 3, 4])
        self.assertEqual(m.values(), [1, 2, 3, 4])
        self.assertRaises(TypeError, Mesh, 2, 2, data='abcd')
        self.assertRaises(ValueError, Mesh, 2, 2, data=[1, 2, 3])

    def test_len(self):
        m = Mesh(2, 2)
        self.assertEqual(len(m), 4)

    def test_str(self):
        m = Mesh(2, 3, data=[1, 2, 3, 4, 5, 6])
        self.assertEqual(str(m), '[1, 2]\n[3, 4]\n[5, 6]\n')

    def test_compact_str(self):
        m = Mesh(2, 3, data=[1, 2, 3, 4, 5, 6])
        self.assertEqual(m.compact_str, '12\n34\n56\n')
        m = Mesh(3, 2, data=[1, 2, 3, 4, 5, 6])
        self.assertEqual(m.compact_str, '123\n456\n')

    def test_repr(self):
        m = Mesh(2, 2, data=[1, 2, 3, 4])
        m2 = eval(repr(m))
        self.assertEqual(m, m2)

    def test_repr_2(self):
        # check that types work
        data=["1", 2.0, 3, 4]
        m = Mesh(2, 2, data=list(data))
        m2 = eval(repr(m))
        self.assertEqual(m, m2)
        self.assertEqual(data, m2._data)

    def test_copy(self):
        m = Mesh(2, 2)
        m2 = m
        m3 = m.copy()
        m[1, 1] = True
        self.assertTrue(m2[1, 1])
        self.assertFalse(m3[1, 1])

    def test_json(self):
        m = Mesh(2, 3, data=[1, 2, 3, 4, 5, 6])
        m_json = json_converter.dumps(m)
        m_json_target = {"__id__": "pelita.containers.Mesh",
                         "__value__": {"width": 2,
                                       "data": [1, 2, 3, 4, 5, 6],
                                       "height": 3}}

        self.assertEqual(json.loads(m_json), m_json_target)
        self.assertEqual(json_converter.loads(m_json), m)

    def test_json_non_trivial(self):
        simple_mesh = Mesh(2, 3, data=[1, 2, 3, 4, 5, 6])
        m = Mesh(2, 3, data=[1,
                            {"key": "value"},
                             [3, 6, 9, 27],
                             ("a", "tuple?"),
                              u"ünico∂e",
                              simple_mesh])

        m_no_tuple = Mesh(2, 3, data=[1,
                            {"key": "value"},
                             [3, 6, 9, 27],
                             ["a", "tuple?"],
                              u"ünico∂e",
                              simple_mesh])

        m_json = json_converter.dumps(m)

        self.assertEqual(json_converter.loads(m_json), m_no_tuple)


class TestTypeAwareList(unittest.TestCase):

    def test_eq_repr(self):
        tal = TypeAwareList([1, 2.0, 3+1j], base_class=Number)
        tal2 = TypeAwareList([1, 2.0, 3+1j], base_class=Number)
        tal3 = TypeAwareList([], base_class=Number)
        self.assertEqual(tal, tal2)
        self.assertEqual(tal, eval(repr(tal)))
        self.assertNotEqual(tal, tal3)

    def test_contains(self):
        tal = TypeAwareList([1, [], {}])
        self.assertTrue(1 in tal)
        self.assertTrue(int in tal)
        self.assertTrue([] in tal)
        self.assertTrue(list in tal)
        self.assertTrue({} in tal)
        self.assertTrue(dict in tal)
        self.assertFalse(set() in tal)
        self.assertFalse(set in tal)

    def test_index(self):
        tal = TypeAwareList([1, [], {}])
        self.assertEqual(tal.index(1), 0)
        self.assertEqual(tal.index(int), 0)
        self.assertEqual(tal.index([]), 1)
        self.assertEqual(tal.index(list), 1)
        self.assertEqual(tal.index({}), 2)
        self.assertEqual(tal.index(dict), 2)
        self.assertRaises(ValueError, tal.index, set)
        self.assertRaises(ValueError, tal.index, set())

    def test_filter_types(self):
        tal = TypeAwareList([1, 2, [], {}, 1, [], 3])
        self.assertEqual(tal.filter_type(int), [1, 2, 1, 3])
        self.assertEqual(tal.filter_type(list), [[], []])
        self.assertEqual(tal.filter_type(dict), [{}])
        self.assertEqual(tal.filter_type(set), [])

        self.assertRaises(TypeError, tal.filter_type, 1)
        self.assertRaises(TypeError, tal.filter_type, list())

        # needs to raise for empty list as well
        tal = TypeAwareList([])
        self.assertRaises(TypeError, tal.filter_type, 1)
        self.assertRaises(TypeError, tal.filter_type, list())

    def test_remove_types(self):
        tal = TypeAwareList([1, 2, [], {}, 1, [], 3])
        tal.remove_type(int)
        self.assertEqual(list(tal), [[], {}, []])

        tal = TypeAwareList([1, 2, [], {}, 1, [], 3])
        tal.remove_type(list)
        self.assertEqual(list(tal), [1, 2, {}, 1, 3])

        tal = TypeAwareList([1, 2, [], {}, 1, [], 3])
        tal.remove_type(dict)
        self.assertEqual(list(tal), [1, 2, [], 1, [], 3])

        tal = TypeAwareList([1, 2, [], {}, 1, [], 3])
        tal.remove_type(set)
        self.assertEqual(list(tal), [1, 2, [], {}, 1, [], 3])

        tal = TypeAwareList([])
        tal.remove_type(int)
        self.assertEqual(list(tal), [])

        tal = TypeAwareList([1, 2, [], {}, 1, [], 3])
        self.assertRaises(TypeError, tal.remove_type, 1)
        self.assertRaises(TypeError, tal.remove_type, list())

        tal = TypeAwareList([])
        self.assertRaises(TypeError, tal.remove_type, 1)
        self.assertRaises(TypeError, tal.remove_type, list())

    def test_insert_types(self):
        class A(object):
            pass

        class B(A):
            pass

        class C(B):
            pass

        class D(object):
            pass

        tal = TypeAwareList(base_class=A)
        a, b, c, d = A(), B(), C(), D()
        tal.append(a)
        tal.append(b)
        tal.append(c)

        self.assertRaises(ValueError, tal.append, 1)
        self.assertRaises(ValueError, tal.append, d)
        self.assertRaises(ValueError, tal.__setitem__, 0, d)

        self.assertEqual(list(tal), [a, b, c])
        tal[0] = b
        self.assertEqual(list(tal), [b, b, c])

    def test_base_class(self):
        self.assertRaises(TypeError, TypeAwareList, base_class=1)
        self.assertRaises(TypeError, TypeAwareList, base_class=list())

        tal = TypeAwareList([1, 2, 3], base_class=int)
        self.assertEqual(list(tal), [1, 2, 3])

        self.assertRaises(ValueError, TypeAwareList, [1, []], base_class=list)

    def test_json(self):
        tal = TypeAwareList([MazeComponent(), MazeComponent(), MazeComponent()], base_class=MazeComponent)
        tal_json = json_converter.dumps(tal)
        self.assertEqual(json_converter.loads(tal_json), tal)

        class A(object):
            pass

        tal = TypeAwareList([], base_class=A)
        tal_json = json_converter.dumps(tal)
        self.assertRaises(AttributeError, json_converter.loads, tal_json)

        # test base_class=None
        tal = TypeAwareList([], base_class=None)
        tal_json = json_converter.dumps(tal)
        self.assertEqual(json_converter.loads(tal_json), tal)
