import unittest

from mysqlkit.rpl import gtid


class TestGTIDRange(unittest.TestCase):

    def setUp(self):
        self.g1 = gtid.GTIDRange(12)
        self.g2 = gtid.GTIDRange(43, 43)
        self.g3 = gtid.GTIDRange(198, 2174)
        self.g4 = gtid.GTIDRange('198-2174')

    def test_invalid(self):
        self.assertRaises(ValueError, lambda: gtid.GTIDRange(91, 73))

    def test_basic(self):
        self.assertEqual(len(self.g1), 1)
        self.assertEqual(len(self.g2), 1)
        self.assertEqual(len(self.g3), 1977)
        self.assertEqual(self.g3, self.g4)

        self.assertTrue(self.g1.is_single())
        self.assertTrue(self.g2.is_single())
        self.assertFalse(self.g3.is_single())

        self.assertEqual(str(self.g1), '12')
        self.assertEqual(str(self.g3), '198-2174')

    def test_item(self):
        self.assertEqual(self.g1[0], 12)
        self.assertEqual(self.g1[1], 12)
        self.assertEqual(self.g4[1], 2174)
        self.assertRaises(IndexError, lambda: self.g4[2])

    def test_cmp(self):
        g = gtid.GTIDRange(19, 132)
        self.assertLess(g, self.g3)
        self.assertGreater(g, self.g1)
        self.assertEqual(g, (19, 132))

    def test_contain(self):
        g = gtid.GTIDRange(19, 132)
        self.assertIn(self.g2, g)
        self.assertNotIn(g, self.g2)
        self.assertNotIn(g, self.g3)
        self.assertIn(g, gtid.GTIDRange(1, 200))
        self.assertNotIn(g, gtid.GTIDRange(95, 200))
        self.assertIn((22, 39), g)

    def test_overlap(self):
        self.assertFalse(self.g1.is_overlapping(self.g2))
        self.assertFalse(self.g2.is_overlapping(self.g3))
        self.assertTrue(self.g3.is_overlapping(gtid.GTIDRange(127, 205)))
        self.assertTrue(self.g3.is_overlapping((1981, 2256)))
        self.assertTrue(self.g3.is_overlapping((318, 1562)))

    def test_consecutive(self):
        self.assertTrue(self.g1.is_consecutive(gtid.GTIDRange(13, 42)))
        self.assertTrue(self.g3.is_consecutive(gtid.GTIDRange(2175, 3985)))
        self.assertFalse(gtid.GTIDRange(125, 198).is_consecutive(self.g3))

    def test_add(self):
        self.assertEqual(self.g1 + self.g2, gtid.GTIDRangeList('12', '43'))
        self.assertEqual(self.g3 + gtid.GTIDRange(2029, 3201), gtid.GTIDRangeList('198-3201'))
        self.assertEqual(self.g1 + self.g2, self.g2 + self.g1)

    def test_sub(self):
        self.assertEqual(self.g1 - self.g2, gtid.GTIDRangeList('12'))
        self.assertEqual(self.g1 - self.g3, gtid.GTIDRangeList('12'))
        self.assertEqual(self.g3 - gtid.GTIDRange('198-200'), gtid.GTIDRangeList('201-2174'))
        self.assertEqual(self.g3 - gtid.GTIDRange('201-205'), gtid.GTIDRangeList('198-200:206-2174'))
        self.assertEqual(self.g1 - self.g1, gtid.GTIDRangeList(''))


class TestGTIDRangeList(unittest.TestCase):

    def setUp(self):
        self.gl1 = gtid.GTIDRangeList('1-139', '141', '145-197')

    def test_empty(self):
        empty = gtid.GTIDRangeList()
        self.assertEqual(empty.ranges, [])
        self.assertEqual(empty, gtid.GTIDRangeList(''))

    def test_parse(self):
        self.assertEqual(gtid.GTIDRangeList((1, 19)),  gtid.GTIDRangeList('1-19'))
        self.assertEqual(gtid.GTIDRangeList((1, 1), '9-12'), gtid.GTIDRangeList('1:9-12'))
        self.assertEqual(gtid.GTIDRangeList(gtid.GTIDRange(1, 5), '9-12'), gtid.GTIDRangeList('1-5:9-12'))

    def test_add(self):
        self.assertEqual(self.gl1 + gtid.GTIDRangeList('140'), gtid.GTIDRangeList('1-141', '145-197'))
        self.assertEqual(self.gl1 + gtid.GTIDRangeList('112-140'), gtid.GTIDRangeList('1-141', '145-197'))
        self.assertEqual(self.gl1 + gtid.GTIDRangeList('1-156'), gtid.GTIDRangeList('1-197'))
        self.assertEqual(self.gl1 + gtid.GTIDRangeList('142-144'), gtid.GTIDRangeList('1-139:141-197'))

        self.assertEqual(gtid.GTIDRangeList('1:3:18') + gtid.GTIDRangeList('2:4-8'), gtid.GTIDRangeList('1-8:18'))

    def test_zero_add(self):
        grl = gtid.GTIDRangeList('1') + gtid.GTIDRangeList()
        self.assertIsInstance(grl, gtid.GTIDRangeList)
        self.assertEqual(grl, gtid.GTIDRangeList('1'))

    def test_sub(self):
        self.assertEqual(self.gl1 - gtid.GTIDRangeList('2-7:100-101:141'), gtid.GTIDRangeList('1:8-99:102-139:145-197'))
        zero = self.gl1 - self.gl1
        self.assertIsInstance(zero, gtid.GTIDRangeList)
        self.assertFalse(zero)

    def test_contains(self):
        self.assertIn(gtid.GTIDRange(2, 98), self.gl1)
        self.assertIn(gtid.GTIDRange(141), self.gl1)
        self.assertIn(gtid.GTIDRange(145, 197), self.gl1)
        self.assertNotIn(gtid.GTIDRange(144, 197), self.gl1)
        self.assertNotIn(gtid.GTIDRange(142), self.gl1)

        self.assertIn(gtid.GTIDRangeList('2-98:141'), self.gl1)
        self.assertIn(gtid.GTIDRangeList('141'), self.gl1)
        self.assertIn(gtid.GTIDRangeList('1-139:141:145-197'), self.gl1)
        self.assertNotIn(gtid.GTIDRangeList('1-139:141-142:145-197'), self.gl1)

        self.assertRaises(TypeError, lambda: gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23:27') in self.gl1)
        self.assertRaises(TypeError, lambda: (1, 47) in self.gl1)

    def test_trx_count(self):
        self.assertEqual(self.gl1.count(), 193)


class TestGTIDSet(unittest.TestCase):

    def setUp(self):
        self.gtid_set = gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23:27')

    def test_parse(self):
        self.assertEqual(gtid.GTIDSet.parse(''), {})

    def test_base(self):
        self.assertEqual(self.gtid_set['3E11FA47-71CA-11E1-9E33-C80AA9429562'], gtid.GTIDRangeList('1-23:27'))
        empty = gtid.GTIDSet('')
        self.assertEqual(empty.sets, {})
        self.assertFalse(empty)
        self.assertEqual(gtid.GTIDSet('4d15910-b6a4-11e4-af2c-080027880ca6:1')['4d15910-b6a4-11e4-af2c-080027880ca6'],
                         gtid.GTIDRangeList('1'))

    def test_item(self):
        self.gtid_set['966073f3-b6a4-11e4-af2c-080027880ca6'] = gtid.GTIDRangeList('1-29')
        self.assertEqual(self.gtid_set.sets, {
            '3E11FA47-71CA-11E1-9E33-C80AA9429562': gtid.GTIDRangeList('1-23:27'),
            '966073f3-b6a4-11e4-af2c-080027880ca6': gtid.GTIDRangeList('1-29'),
        })

    def test_multiline(self):
        gtid_set = gtid.GTIDSet("""84d15910-b6a4-11e4-af2c-080027880ca6:1,
966073f3-b6a4-11e4-af2c-080027880ca6:1-29""")
        self.assertEqual(sorted(gtid_set.sets.keys()),
                         ['84d15910-b6a4-11e4-af2c-080027880ca6', '966073f3-b6a4-11e4-af2c-080027880ca6'])

    def test_str(self):
        self.assertEqual(str(self.gtid_set), '3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23:27')
        gtid_set = gtid.GTIDSet("""84d15910-b6a4-11e4-af2c-080027880ca6:1,
966073f3-b6a4-11e4-af2c-080027880ca6:1-29""")
        self.assertEqual(str(gtid_set), """84d15910-b6a4-11e4-af2c-080027880ca6:1,
966073f3-b6a4-11e4-af2c-080027880ca6:1-29""")

    def test_add(self):
        gs1 = gtid.GTIDSet('4d15910-b6a4-11e4-af2c-080027880ca6:1')
        self.assertEqual(gs1 + self.gtid_set, gtid.GTIDSet("""3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23:27,
4d15910-b6a4-11e4-af2c-080027880ca6:1"""))

        gs2 = gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:24-26:28')
        self.assertEqual(gs2 + self.gtid_set, gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-28'))

    def test_sub(self):
        gs1 = gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-23:27')
        self.assertEqual(self.gtid_set - gs1, gtid.GTIDSet(''))

        gs2 = gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:2-5:21:24-29')
        self.assertEqual(self.gtid_set - gs2, gtid.GTIDSet('3E11FA47-71CA-11E1-9E33-C80AA9429562:1:6-20:22-23'))

    def test_trx_count(self):
        self.assertEqual(self.gtid_set.count(), 24)

        gs1 = gtid.GTIDSet("""84d15910-b6a4-11e4-af2c-080027880ca6:1,
966073f3-b6a4-11e4-af2c-080027880ca6:1-29""")
        self.assertEqual(gs1.count(), 30)

        gs2 = gtid.GTIDSet('')
        self.assertEqual(gs2.count(), 0)
