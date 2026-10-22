import copy
import json
import unittest
import pg6840_api_counter_delta as p
from pg6818_current_counter_delta import explicit_four100


class ApiCounterDeltaDefinitionTest(unittest.TestCase):
    def test_nonmeasured_not_completed(self):
        self.assertFalse(explicit_four100({}))
        self.assertFalse(explicit_four100({k:dict(covered=0,missed=0)for k in('LINE','METHOD','CLASS','BRANCH')}))

    def test_real_baseline_not_newly_closed_or_deletable(self):
        before=json.loads(p.BEFORE.read_bytes())
        with self.assertRaises(ValueError):p.compare(before,before)
        changed=copy.deepcopy(before);del changed['allPhysicalMainSha256'][next(iter(changed['allPhysicalMainSha256']))]
        with self.assertRaises(ValueError):p.compare(before,changed)


if __name__=='__main__':unittest.main()
