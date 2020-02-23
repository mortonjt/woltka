#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# Copyright (c) 2020--, Qiyun Zhu.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase, main
from os.path import join, dirname, realpath
from shutil import rmtree
from tempfile import mkdtemp

from woltka.util import readzip
from woltka.align import parse_b6o_line, parse_sam_line
from woltka.ordinal import (
    Ordinal, match_read_gene, read_gene_coords, whether_prefix)


class OrdinalTests(TestCase):
    def setUp(self):
        self.tmpdir = mkdtemp()
        self.datdir = join(dirname(realpath(__file__)), 'data')

    def tearDown(self):
        rmtree(self.tmpdir)

    def test_match_read_gene(self):
        # illustration of map

        #  reads:             ---------r1---------
        #                           ---------r2---------
        #                               ---------r3---------
        #                                 ---------r4---------
        #                                         ---------r5---------
        #                                         ---------r6---------
        # genome:  1 ====>>>>>>>>>>>g1>>>>>>>>>>>>===>>>>>>>>>>>>>>g2>> 50

        #  reads:             ---------r7---------
        #                          ---------r8---------
        #                                           ------r9------
        # genome: 51 >>>>>>>>>>>===>>>>>>>>>>>>>>g3>>>>>>>>>>>>>======= 100
        # --------------------------------------------------

        # gene table
        genes = [('g1',  5, 29),
                 ('g2', 33, 61),
                 ('g3', 65, 94)]
        # read map
        reads = [('r1', 10, 29),
                 ('r2', 16, 35),
                 ('r3', 20, 39),
                 ('r4', 22, 41),
                 ('r5', 30, 49),
                 ('r6', 30, 49),  # identical
                 ('r7', 60, 79),
                 ('r8', 65, 84),
                 ('r9', 82, 95)]  # shorter

        # length map
        lens = {'r{}'.format(i): 20 for i in range(1, 10)}

        # flatten lists
        genes = [x for id_, start, end in genes for x in
                 ((start, True, True, id_),
                  (end,  False, True, id_))]
        reads = [x for id_, start, end in reads for x in
                 ((start, True, False, id_),
                  (end,  False, False, id_))]

        queue = sorted(genes + reads, key=lambda x: x[0])

        # default (threshold = 80%)
        obs = match_read_gene(queue, lens, th=0.8)
        exp = {'r1': {'g1'},
               'r5': {'g2'},
               'r6': {'g2'},
               'r8': {'g3'}}
        self.assertDictEqual(obs, exp)

        # threashold = 50%
        obs = match_read_gene(queue, lens, th=0.5)
        exp = {'r1': {'g1'},
               'r2': {'g1'},
               'r3': {'g1'},
               'r5': {'g2'},
               'r6': {'g2'},
               'r7': {'g3'},
               'r8': {'g3'},
               'r9': {'g3'}}
        self.assertDictEqual(obs, exp)

    def test_ordinal_init(self):
        proc = Ordinal({}, True, 0.75)
        self.assertDictEqual(proc.coords, {})
        self.assertEqual(proc.prefix, True)
        self.assertEqual(proc.th, 0.75)
        self.assertIsNone(proc.buf)

    def test_ordinal_parse(self):
        proc = Ordinal({})

        # b6o (BLAST, DIAMOND, BURST, etc.)
        parser = parse_b6o_line
        b6o = ('S1/1	NC_123456	100	100	0	0	1	100	225	324	1.2e-30	345',
               'S1/2	NC_123456	95	98	2	1	2	99	708	608	3.4e-20	270')
        self.assertEqual(proc.parse(b6o[0], parser), 'S1/1')
        self.assertTupleEqual(
            proc.buf, ('S1/1', 'NC_123456', 345.0, 100, 225, 324))

        # sam (Bowtie2, BWA, etc.)
        parser = parse_sam_line
        sam = (
            '@HD	VN:1.0	SO:unsorted',
            'S1	77	NC_123456	26	0	100M	*	0	0	*	*',
            'S1	141	NC_123456	151	0	80M	*	0	0	*	*',
            'S2	0	NC_789012	186	0	50M5I20M5D20M	*	0	0	*	*',
            'S2	16	*	0	0	*	*	0	0	*	*')
        self.assertEqual(proc.parse(sam[1], parser), 'S1/1')
        self.assertTupleEqual(
            proc.buf, ('S1/1', 'NC_123456', None, 100, 26, 125))

        # header
        with self.assertRaises(TypeError):
            proc.parse(sam[0], parser)

        # not aligned
        with self.assertRaises(TypeError):
            proc.parse(sam[4], parser)

    def test_ordinal_append(self):
        proc = Ordinal({})

        # b6o (BLAST, DIAMOND, BURST, etc.)
        parser = parse_b6o_line
        b6o = ('S1/1	NC_123456	100	100	0	0	1	100	225	324	1.2e-30	345',
               'S1/2	NC_123456	95	98	2	1	2	99	708	608	3.4e-20	270')

        # first line
        proc.parse(b6o[0], parser)
        proc.append()
        self.assertListEqual(proc.rids, ['S1/1'])
        self.assertDictEqual(proc.lenmap, {'NC_123456': {0: 100}})
        self.assertDictEqual(proc.locmap, {'NC_123456': [
            (225, True, False, 0), (324, False, False, 0)]})

        # second line
        proc.parse(b6o[1], parser)
        proc.append()
        self.assertListEqual(proc.rids, ['S1/1', 'S1/2'])
        self.assertDictEqual(proc.lenmap, {'NC_123456': {0: 100, 1: 98}})
        self.assertDictEqual(proc.locmap, {'NC_123456': [
            (225, True, False, 0), (324, False, False, 0),
            (608, True, False, 1), (708, False, False, 1)]})

        # sam (Bowtie2, BWA, etc.)
        proc.clear()
        parser = parse_sam_line
        sam = (
            '@HD	VN:1.0	SO:unsorted',
            'S1	77	NC_123456	26	0	100M	*	0	0	*	*',
            'S1	141	NC_123456	151	0	80M	*	0	0	*	*',
            'S2	0	NC_789012	186	0	50M5I20M5D20M	*	0	0	*	*',
            'S2	16	*	0	0	*	*	0	0	*	*')

        # normal, fully-aligned, forward strand
        proc.parse(sam[1], parser)
        proc.append()
        self.assertListEqual(proc.rids, ['S1/1'])
        self.assertDictEqual(proc.lenmap, {'NC_123456': {0: 100}})
        self.assertDictEqual(proc.locmap, {'NC_123456': [
            (26, True, False, 0), (125, False, False, 0)]})

        # shortened, reverse strand
        proc.parse(sam[2], parser)
        proc.append()
        self.assertListEqual(proc.rids, ['S1/1', 'S1/2'])
        self.assertDictEqual(proc.lenmap, {'NC_123456': {
            0: 100, 1: 80}})
        self.assertDictEqual(proc.locmap, {'NC_123456': [
            (26,  True, False, 0), (125, False, False, 0),
            (151, True, False, 1), (230, False, False, 1)]})

        # not perfectly aligned, unpaired
        proc.parse(sam[3], parser)
        proc.append()
        self.assertListEqual(proc.rids, ['S1/1', 'S1/2', 'S2'])
        self.assertEqual(proc.lenmap['NC_789012'][2], 90)
        self.assertTupleEqual(
            proc.locmap['NC_789012'][0], (186,  True, False, 2))
        self.assertTupleEqual(
            proc.locmap['NC_789012'][1], (280, False, False, 2))

    def test_ordinal_flush(self):
        # TODO
        pass

    def test_read_gene_coords(self):
        # simple case
        tbl = ('## GCF_000123456',
               '# NC_123456',
               '1	5	384',
               '2	410	933',
               '# NC_789012',
               '1	912	638',
               '2	529	75')
        obs = read_gene_coords(tbl, sort=True)
        exp = {'NC_123456': [
            (5,   True, True, '1'), (384, False, True, '1'),
            (410, True, True, '2'), (933, False, True, '2')],
               'NC_789012': [
            (75,  True, True, '2'), (529, False, True, '2'),
            (638, True, True, '1'), (912, False, True, '1')]}
        self.assertDictEqual(obs, exp)

        # real coords file
        fp = join(self.datdir, 'function', 'coords.txt.xz')
        with readzip(fp) as f:
            obs = read_gene_coords(f, sort=True)
        self.assertEqual(len(obs), 107)
        obs_ = obs['G000006745']
        self.assertEqual(len(obs_), 7188)
        self.assertTupleEqual(obs_[0], (372,  True,  True, '1'))
        self.assertTupleEqual(obs_[1], (806,  False, True, '1'))
        self.assertTupleEqual(obs_[2], (816,  True,  True, '2'))
        self.assertTupleEqual(obs_[3], (2177, False, True, '2'))

    def test_whether_prefix(self):
        # gene Ids are indices
        coords = {'NC_123456': [
            (5,   True, True, '1'), (384, False, True, '1'),
            (410, True, True, '2'), (933, False, True, '2')],
                  'NC_789012': [
            (75,  True, True, '2'), (529, False, True, '2'),
            (638, True, True, '1'), (912, False, True, '1')]}
        self.assertTrue(whether_prefix(coords))

        # gene Ids are unique accessions
        coords = {'NC_123456': [
            (5,   True, True,  'NP_135792.1'),
            (384, False, True, 'NP_135792.1'),
            (410, True, True,  'NP_246801.2'),
            (933, False, True, 'NP_246801.2')],
                  'NC_789012': [
            (75,  True, True,  'NP_258147.1'),
            (529, False, True, 'NP_258147.1'),
            (638, True, True,  'NP_369258.2'),
            (912, False, True, 'NP_369258.2')]}
        self.assertFalse(whether_prefix(coords))


if __name__ == '__main__':
    main()
