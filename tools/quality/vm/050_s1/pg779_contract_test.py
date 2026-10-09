"""Generated call-to-immutable inventory join plus current151 fault fixture, no guest."""
import re
import unittest
from unittest.mock import patch
import pg778_sources as prior
from pg778_contract_test import Test as PriorTest
from pg779_sources import java,helper


class Test(unittest.TestCase):
    def test_actual_script_calls_exact_manifest_graph(self):
        self.assertEqual({'pg779_owned.py','pg779_refs.py'},set(re.findall(r'TOOLS.resolve\("([^\"]+\.py)"\)',java())))
        self.assertIn('refsHeld=true;var refs=new References',java())
        self.assertIn('refs.release();refsHeld=false;db.rollback();',java())
        self.assertNotIn('pg779_timeout_owned.py',java())
        self.assertNotIn('pg778',java());self.assertNotIn('pg778',helper())
        self.assertIn('return refsHeld || mutated ||',java())

    def test_current_existing_fault_oracle_with_actual_namespace(self):
        with patch.object(prior,'helper',helper):
            PriorTest('test_independent_current_stop_fault_fixture').test_independent_current_stop_fault_fixture()


if __name__=='__main__':unittest.main()
