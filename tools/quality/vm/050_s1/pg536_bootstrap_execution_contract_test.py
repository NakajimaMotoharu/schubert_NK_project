"""Independent manager declaration/history golden literals. No Unit actions."""
import copy
import unittest
from pg536_bootstrap_execution_contract import configuration, record
from pg535_bootstrap_contract_test import literal20


class HistoryTest(unittest.TestCase):
    def test_golden_first_execution20_and_all_mutations(self):
        old = {'User': 'schubert-api', 'ExecStart': '{ path=/usr/bin/java ; argv[]=/usr/bin/java fixed BootstrapAdminMain ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'}
        new = {'User': 'schubert-api', 'ExecStart': '{ path=/usr/bin/java ; argv[]=/usr/bin/java fixed BootstrapAdminMain ; ignore_errors=no ; start_time=[START] ; stop_time=[END] ; pid=42 ; code=exited ; status=20 }'}
        terminal = literal20()
        actor = {'pid': '42', 'ticks': '123', 'invocation': 'a'*32, 'zeroCapabilities': True}
        self.assertTrue(configuration(old, new, terminal, actor, 'START', 'END'))
        for source, target in [('path=/usr/bin/java', 'path=/foreign'), ('fixed', 'foreign'),
                               ('ignore_errors=no', 'ignore_errors=yes'), ('[START]', '[OTHER]'),
                               ('[END]', '[OTHER]'), ('pid=42', 'pid=43'),
                               ('code=exited', 'code=killed'), ('status=20', 'status=0')]:
            self.assertFalse(configuration(old, {**new, 'ExecStart': new['ExecStart'].replace(source, target)}, terminal, actor, 'START', 'END'))
        for i, original in enumerate([old, new, terminal, actor, 'START', 'END']):
            for bad in (None, {}, '', False):
                args = [old, new, terminal, actor, 'START', 'END']
                args[i] = bad
                self.assertFalse(configuration(*args))
            if isinstance(original, dict):
                for key in original:
                    args = [old, new, terminal, actor, 'START', 'END']
                    changed = copy.deepcopy(original); changed[key] = None; args[i] = changed
                    self.assertFalse(configuration(*args))
        self.assertFalse(configuration(old, {**new, 'User':'root'}, terminal, actor, 'START', 'END'))
        self.assertFalse(configuration(old, new, terminal, {**actor, 'invocation':'b'*32}, 'START', 'END'))
        self.assertFalse(configuration(old, old, terminal, actor, 'START', 'END'))
        for bad in (None, '', 'foreign', new['ExecStart']+' ; extra', new['ExecStart']*2):
            self.assertIsNone(record(bad))


if __name__ == '__main__':
    unittest.main()
