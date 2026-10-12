"""Real composed EXPECTED and real WARNING receipt, UUID independent literals."""
import ast
import datetime
import unittest
from pg1808_warning_identity_bound_sources import sources,namespace


class Identity(unittest.TestCase):
    def test_namespace_does_not_rewrite_embedded_tool_digits(self):
        original='4148e3e8-f107-431a-ab27-d6e6d1f1772e'
        self.assertEqual(original,namespace(original))
        original2='4148e3e8-f107-431a-ab27-d6e6d1f1800e'
        self.assertEqual(original2,namespace(original2))
        self.assertEqual('pg1808/Pg1808/PG1808',namespace('pg1800/Pg1800/PG1800'))

    def test_actual_emitted_warning_receipt_independent_original(self):
        raw=sources()['pg1808_parent_receipt.py'];ns={};exec(raw,ns)
        self.assertEqual('4148e3e8-f107-431a-ab27-d6e6d1f1772e',ns['EXPECTED']['run'])
        fixed={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'b5a12ee25dc44ec49b08f5d084b4052f'}
        real=str(int(datetime.datetime(2026,10,12,18,46,53,tzinfo=datetime.timezone.utc).timestamp()*1000000))
        rows=[{**fixed,'__CURSOR':'literal-failure-1','__MONOTONIC_TIMESTAMP':'83018952135','__REALTIME_TIMESTAMP':real,'MESSAGE_ID':'98e322203f7a4ed290d09fe03c09fe15','EXIT_CODE':'exited','EXIT_STATUS':'10'},{**fixed,'__CURSOR':'literal-job-2','__MONOTONIC_TIMESTAMP':'83018953880','__REALTIME_TIMESTAMP':real,'MESSAGE_ID':'be02cf6855d2428ba40df7e9d022f03d','JOB_ID':'127250','JOB_TYPE':'start','JOB_RESULT':'failed'}]
        original=b'NKDONE1\n4148e3e8-f107-431a-ab27-d6e6d1f1772e\n2026-10-12T18:20:32.598894Z\n9adbf05a-61d0-408b-b51d-ab19c7e5b16a\n2026-10-12T18:46:52.677350Z\n10\n'
        result=ns['completed'](rows,original);self.assertEqual(83018953880,result['endMonotonicUs']);self.assertTrue(result['managerFailureRetained']);self.assertFalse(result['genuinePid1StartDone'])
        for bad in [original.replace(b'f1772e',b'f1800e'),original.replace(b'\n10\n',b'\n0\n'),original.replace(b'9adbf05a',b'0adbf05a')]:
            with self.assertRaises(ValueError):ns['completed'](rows,bad)

    def test_all_emitted_namespaces_keep_independent_UUIDs(self):
        generated=sources();self.assertEqual(15,len(generated))
        for name,raw in generated.items():
            with self.subTest(name=name):
                self.assertFalse('pg1800'in raw);self.assertFalse('Pg1800'in raw);self.assertFalse('PG1800'in raw)
                if name.endswith('.py'):ast.parse(raw)


if __name__=='__main__':unittest.main()
