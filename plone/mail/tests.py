"""Test library

$Id: test_forms.py 14595 2005-07-12 21:26:12Z philikon $
"""
import unittest

def test_suite():
    from zope.testing.doctestunit import DocTestSuite
    return unittest.TestSuite((
            DocTestSuite('plone.mail'),),)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
