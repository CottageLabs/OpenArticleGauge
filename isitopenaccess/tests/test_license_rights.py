from unittest import TestCase

from isitopenaccess import license_rights

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_oa_policy_function_basics(self):
        # considered Open Access
        test_rights = {'NC': False, 'SA': False, 'ND': False}
        assert license_rights.oa_from_rights(**test_rights)

        # NOT considered Open Access

        # note the following iterates over a COPY of test_rights
        # since the loop modifies test_rights and sets the values to True one 
        # by one, achieving the effect of
        # {'SA': True, 'NC': False, 'ND': False}
        # {'SA': False, 'NC': True, 'ND': False}
        # {'SA': False, 'NC': False, 'ND': True}
        
        # It then does exactly the same, but with the value None.
        # True means there is a restriction. None is for licenses which have 
        # unknown NC or other rights they grant/deny.
        test_values = [True, None]

        for tv in test_values:
            for right, right_value in test_rights.copy().items():
            # So set every right/requirement to True or None, see if the 
            # function returns False as expected, and then reset that right,
            # ready for testing the next right.
                test_rights[right] = tv
                assert not license_rights.oa_from_rights(**test_rights)
                test_rights[right] = False
                assert license_rights.oa_from_rights(**test_rights)

    def test_oa_policy_function_additional_args(self):
        # considered Open Access
        test_rights = {'NC': False, 'SA': False, 'ND': False,
            'BY': True
        }
        assert license_rights.oa_from_rights(**test_rights)

    def test_license_rights_select_function(self):
        # oa_for_license is essentially a convenience wrapper around
        # oa_from_rights which just selects the appropriate license from the
        # license_rights.LICENSES_RIGHTS dictionary.
        # We are not going to test the *contents* of the dictionary, that is
        # up to plugin content tests. We are just going to see if the wrapper
        # works as expected.

        # try a license which should exist and should be OA
        # We don't care what value it returns, we just care about accessing
        # dict. All we're checking is that no exceptions are raised.
        dummy_open_access_value = license_rights.oa_for_license('cc-by')

        self.assertRaises(KeyError, license_rights.oa_for_license, 'should_not_exist')
