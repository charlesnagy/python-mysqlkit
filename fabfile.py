import nose
import os


def test(suite):
    nose.run(argv=['-w', os.path.join('tests', suite), '-vv'])
