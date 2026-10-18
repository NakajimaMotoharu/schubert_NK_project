"""Independent genuine end/start vectors, complete graph/ABI/transport guards."""
import inspect
import unittest
from pyflakes.api import checkPath
import pg4932_current_bootstrap_test as previous
import pg5102_corrected_bootstrap_sources as role
import pg5104_corrected_bootstrap_compile as compiler
import pg5106_corrected_bootstrap_dispatch as dispatch
import pg4822_new_current_bootstrap_compile as compile_template


def matrix():
    raw = inspect.getsource(previous.CurrentBootstrap)
    for old, new in [('Pg4932','Pg5102'),('pg4932','pg5102'),('PG4932','PG5102'),
                     ('==884','==894'),('199849150395','308517705767'),
                     ('7fe303d625de4a83b23d23fca4eca2bb','abe95f4c09b849a8a2304e94a3cb8165'),
                     ('7bae6042-b79f-4fb2-9d9f-edf47b428cbe','b683da46-df42-4e52-8379-5ac8bfbca0ae'),
                     ('4e220f3b-fbb4-411c-b5c4-7ca1371daa20','15322936-6512-4550-8123-a3ef688dc1da'),
                     ('pg4916','pg5060'),('actual4930','actual5080'),('pg4918','pg5062'),
                     ('pg4860','pg4980'),('PG4860','PG4980'),('pg4934','pg5104'),
                     ('role.previous.SOURCE','"0"*40'),
                     ('inspect.getsource(compiler.previous.previous)','inspect.getsource(compile_template)')]:
        raw = raw.replace(old,new)
    ns = {**vars(previous),'__file__':__file__,'role':role,'compiler':compiler,'dispatch':dispatch,'compile_template':compile_template}
    exec(compile(raw,'<corrected complete existing20 matrix>','exec'),ns)
    return ns['CurrentBootstrap']


CurrentBootstrap = matrix()


class EndAndNamespace(unittest.TestCase):
    def test_actual_genuine_end_is_independent_of_start_and_old_fixture(self):
        terminal = role.owned.actual.receipt(role.owned.acceptance.TERM)
        start = role.owned.admission.live()['start']
        self.assertEqual(308517705767,terminal['endMonotonicUs'])
        self.assertEqual(306951851178,start)
        helper = role.files(role.BASELINE)['pg5102_bootstrap_existing.py']
        role.validate_parent_end(helper)
        for wrong in ('306951851178','199849150395','None','True',repr('foreign')):
            altered = helper.replace('parent_receipt[\'endMonotonicUs\']==308517705767',
                                     'parent_receipt[\'endMonotonicUs\']=='+wrong)
            with self.subTest(wrong=wrong),self.assertRaises(ValueError):role.validate_parent_end(altered)
        with self.assertRaises(ValueError):role.validate_parent_end('pass')
        self.assertEqual(role.files(role.BASELINE)['pg5060_parent_receipt.py'],
                         (role.W/role.owned.TOOLS/'pg5060_parent_receipt.py').read_text())

    def test_full_new_only_stage_identity_and_no_old_failure_slot(self):
        ns=dispatch.namespace()
        self.assertIs(ns['authenticate_host'],role.before.admission.authenticate_host)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG4980',ns['STAGE'])
        for text in ('PG4860','PG4702'):self.assertNotIn(text,ns['STAGE'])
        values=role.files(role.BASELINE)
        for name,text in values.items():
            for old in ('Pg5082','pg5082','PG5082','pg5080-current-bootstrap-before-v1'):
                self.assertTrue(old not in text,(name,old))
        for path in (role.__file__,compiler.__file__,dispatch.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
