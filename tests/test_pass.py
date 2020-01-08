""" run with

nosetests -v --nocapture

or

nosetests -v

"""

from builtins import object
from cloudmesh_base.util import HEADING

class Test_pass(object):

    def setup(self):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        HEADING()
        assert True
