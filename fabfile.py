import nose
import os
import sys

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))


def test(suite):
    nose.run(argv=['-w', os.path.join('tests', suite), '-vv', '--with-cover', '--cover-package=mysqlkit'])
