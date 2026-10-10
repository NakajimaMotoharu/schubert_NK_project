import ast
import unittest
from pg1144_terminal_cleanup_recovery_sources import files,BASE,SHA


class ProfileTest(unittest.TestCase):
    def test_only_remaining_same_cleanup_is_stopped_completed_broker_expiry_immutable(self):
        result=files();self.assertEqual(len(result),7)
        java=result['Pg1144SingleApiRecovery.java'];refs=result['pg1144_single_api_refs.py']
        self.assertTrue('List.of("schubert-nk-cleanup.service")'in java)
        self.assertFalse('List.of("artemis.service")'in java)
        for value in [BASE,SHA,"ORDER=['schubert-nk-cleanup.service']",'48281323ca3743cbbaddd706e0c4edc5',
                      'require_old_gone_and_current_profile()',"'cleanup-manager.private.jsonl'",'before.keys()-{\'ActiveState\',\'SubState\'}',
                      "require(actual[unit]==baseline['configuration'][unit])"]:
            self.assertTrue(value in refs,value)
        self.assertFalse("actor('artemis.service',baseline['units']['artemis.service'])"in refs)
        for name,text in result.items():
            if name.endswith('.py'):ast.parse(text)
            self.assertFalse('pg1134-issued-api-'in text)
            self.assertFalse('Pg1134'in text)


if __name__=='__main__':unittest.main()
