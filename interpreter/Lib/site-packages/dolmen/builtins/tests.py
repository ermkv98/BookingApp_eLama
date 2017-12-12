#-*- coding: utf-8 -*-

import doctest
import unittest


def test_suite():
    return unittest.TestSuite(doctest.DocFileSuite('README.txt'))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
