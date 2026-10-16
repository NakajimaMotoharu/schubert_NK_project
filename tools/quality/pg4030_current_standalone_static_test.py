import copy
import inspect
import unittest
from pyflakes.api import check
import pg4030_current_standalone_static as review


class ActualStandalonePremise(unittest.TestCase):
    def test_required_primary_premise_and_all_architecture_guards_never_generic_catch(self):
        path = 'src/schubert-nk-api/src/main/java/example.java'
        row = {'path': path, 'sourceSha256': 'a' * 64, 'rule': 'DoNotUseThreads'}
        context = {'sourceSha256': {path: 'a' * 64}, 'vendorExplicitJ2ee': {'DoNotUseThreads': True}, 'approvedDirectJavaProcess': True,
                   'externalJavaEEManaged': False, 'noManagedDeploymentDescriptors': True, 'moduleRoles': {'schubert-nk-api': 'STANDALONE_JAVA_SERVICE'}}
        result = review.classify_contract(row, context, {})
        self.assertEqual('CONTEXT_NOT_APPLICABLE_J2EE_RULE', result['disposition']); self.assertFalse(result['qualityGatePass'])
        for field, value in [('approvedDirectJavaProcess', False), ('externalJavaEEManaged', True), ('noManagedDeploymentDescriptors', False), ('moduleRoles', {}), ('vendorExplicitJ2ee', {})]:
            wrong = copy.deepcopy(context); wrong[field] = value
            self.assertIsNone(review.classify_contract(row, wrong, {}))
        self.assertIsNone(review.classify_contract({**row, 'rule': 'AvoidCatchingGenericException'}, context, {}))
        with self.assertRaises(ValueError): review.classify_contract({**row, 'sourceSha256': 'b' * 64}, context, {})

    def test_complete_host_payload_never_guest_action_or_false_gate(self):
        raw = '\n'.join(inspect.getsource(fn) for fn in [review.require, review.classify_contract, review.server])
        self.assertEqual(0, check(raw, '<new current standalone raw warning assessment>')); compile(raw, '<new actual primary premise>', 'exec')
        for marker in ["len(checked) == 239", "len(added) == 67", "'F03Accepted': False", "'suppressionAdded': False", "'guestActions': 0"]: self.assertIn(marker, raw)
        for marker in ['management_gate', 'systemctl', 'daemon-reload', 'Root/noargs']: self.assertNotIn(marker, raw)


if __name__ == '__main__': unittest.main()
