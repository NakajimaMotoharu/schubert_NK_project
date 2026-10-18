import types
import re
import unittest
import pg5265_owned_factory_proof as proof
import pg5332_service_resources_selected as entry
import pg5156_native_coverage_selected as bootstrap
import pg5336_service_resources_public as public


class ModuleAndInventory(unittest.TestCase):
    def test_module_never_silently_reads_another_compiled_scope(self):
        self.assertEqual(proof.validate_module(entry,'bootstrap'),'bootstrap')
        self.assertEqual(proof.validate_module(types.SimpleNamespace(PREFIX='batch:p/'),'batch'),'batch')
        for module in ('batch','api','unknown',None):
            with self.assertRaises(ValueError): proof.validate_module(entry,module)

    def test_four_new_source_cases_and_previous_repetition_unchanged(self):
        source=entry.selected.ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/ServiceOwnedReleaseTest.java'
        raw=source.read_text();names=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
        self.assertEqual(len(names),4);self.assertEqual(raw.count('@Test'),4)
        self.assertEqual([n[:13] for n in names],['serviceown001','serviceown002','serviceown003','serviceown004'])
        entry.configure()
        self.assertEqual(len(entry.selected.EXTRA_CHANGED),56)
        self.assertEqual(len(entry.extra_suites()),101)
        self.assertEqual(entry.repetitions(),entry.previous.repetitions())
        self.assertEqual(tuple(names),public.NAMES)
        ids=public.revalidated_case_ids(owner_new=True)
        self.assertEqual(sum(v['newInThisChange'] for v in ids.values()),4)
        self.assertEqual(sum(v['newInThisChange'] for v in public.revalidated_case_ids().values()),0)
        self.assertEqual(len({v['testId'] for v in ids.values()}),len(ids))

    def test_missing_or_undeclared_bootstrap_growth_is_refused(self):
        old={str(n):'bootstrap' for n in range(42)}
        self.assertEqual(bootstrap.validate_inventory(old,set()),old)
        extra={'new'};current={**old,'new':'bootstrap'}
        self.assertEqual(bootstrap.validate_inventory(current,extra),current)
        for values,declared in ((current,set()),(old,extra),({**current,'unknown':'bootstrap'},extra)):
            with self.assertRaises(ValueError):bootstrap.validate_inventory(values,declared)


if __name__=='__main__':unittest.main()
