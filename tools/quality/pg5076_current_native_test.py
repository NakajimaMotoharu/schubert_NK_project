"""Current native provenance, complete factories and fail-closed admission; no VM actions."""
import copy
import inspect
import json
import unittest
from pyflakes.api import check, checkPath
import pg5070_current_native_catalog as catalog
import pg5072_current_native_qualified as native
import pg5074_current_native_public as public


class CurrentNative(unittest.TestCase):
    def setUp(self):
        self.post = json.loads((native.W / 'pg5066-current-owned-post-v1/manifest.safe.json').read_bytes())
        self.terminal = catalog.role.actual.receipt(catalog.role.acceptance.TERM)
        self.full = json.loads((native.W / native.FULL / 'manifest.safe.json').read_bytes())

    def test_actual_stopped_current_and_genuine_warning_prerequisite(self):
        catalog.prerequisites(self.post, self.terminal)
        for key, invalid in [('actualExit', False), ('actualExit', None), ('actualExit', 1),
                             ('productionSource', 'foreign'), ('all24UnchangedTwice', False),
                             ('allTenUnitsKernelEmpty', False), ('normalNewMetadataScopes', False),
                             ('allClientAdvisoryFlock0', False)]:
            with self.subTest(key=key, invalid=invalid), self.assertRaises(ValueError):
                catalog.prerequisites({**self.post, key: invalid}, self.terminal)
        for key, invalid in [('productionSource', 'foreign'), ('genuineRootDone', False), ('completionCode', 0)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                catalog.prerequisites(self.post, {**self.terminal, key: invalid})

    def test_generated_complete_current_catalog_old80_are_data_only(self):
        receipt = (native.W / catalog.role.TOOLS / 'pg5060_parent_receipt.py').read_text()
        raw = catalog.catalog_source(receipt, catalog.role.admission.live(), self.terminal['endMonotonicUs'])
        self.assertEqual(0, check('SEALS={}\n' + raw, '<current native catalog>'))
        for literal in (native.SOURCE, catalog.role.BOM, catalog.role.admission.ONCE,
                        catalog.role.admission.before(), 'all80BeforeCopiesPreserved',
                        "'oldSourceNativeImported':False", "==80", "'pg5060-native-stop-v1'"):
            self.assertIn(literal, raw)
        self.assertNotIn('all72BeforeCopiesPreserved', raw)
        self.assertIn("'replayAllowed':False", inspect.getsource(catalog.TEMPLATE.main))

    def test_original3791_553_all1650_qualification(self):
        q = native.qualify(self.full)
        self.assertEqual((3791, 553, 1650, 1646), tuple(q[k] for k in ('tests', 'suites', 'mainClasses', 'unchangedPhysicalClasses')))
        self.assertEqual(4, len(q['changedClasses']))
        for key, invalid in [('tests', 3761), ('suites', 551), ('mainClasses', 1647),
                             ('productionSource', 'foreign'), ('oldNativeImported', True),
                             ('unchangedPhysicalClasses', 1645), ('staticSixModules', 1),
                             ('FESFlakyNotRun', 1), ('F03Accepted', True), ('formalAccepted', True)]:
            wrong = copy.deepcopy(self.full)
            wrong['result'][key] = invalid
            with self.subTest(key=key), self.assertRaises(ValueError):
                native.qualify(wrong)

    def test_full_server_namespace_and_immutable_original_paths(self):
        raw = native.server()
        coordinates = native.previous.previous.transport.prior.previous.entry().__globals__['coordinates']
        complete = ('import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\n'
                    'ARCHIVE_SHA="' + 'a' * 64 + '"\n' + inspect.getsource(coordinates) + '\n' + raw)
        self.assertEqual(0, check(complete, '<all1650 same-source native server>'))
        for literal in ('PG4968-six-v1', 'source-full-PG4968', 'PG5072-native-v1', native.SOURCE,
                        "full['tests'] == 3791", "len(v['selected']) == 10", "len(streams) == 9",
                        "qualified['jarHashes'][m]", "qualified['modules'][m]['coverageXmlSha256']",
                        "result['classByteMismatch'] == 0", 'NativePointDominanceTest',
                        "'oldNativeImported': False", "'formalAccepted': False"):
            self.assertIn(literal, raw)
        for old in ('PG4926', 'PG4844', '3761', '1647'):
            self.assertNotIn(old, raw)
        transport = native.source()
        for literal in (native.FULL, catalog.SLOT, native.SLOT,
                        'test ! -e /home/mini/schubert-nk-pgpt/transfer/PG5072-native-input-v1.tar',
                        'test ! -e /home/mini/schubert-nk-pgpt/runs/PG5072-native-v1'):
            self.assertIn(literal, transport)

    def test_public_projection_preserves_historical_acceptance_and_redaction(self):
        raw = public.source()
        for literal in ('PG5072-native-v1', '3791', '553', '1650', "'PMDRaw': 1657",
                        "'CheckstyleRaw': 0", "'F03Accepted': False", "'acceptedLeafDelta': 0",
                        "'effortPercent': None", "'automaticSourceRebinding': False",
                        '7fffab57a567914956b66452e5e54388642efdec', 'base.redact_report',
                        "native['manifestSha256']", "n['xmlHashes'][module]"):
            self.assertIn(literal, raw)
        self.assertNotIn('PG4926-native-v1', raw)
        self.assertEqual(native.SOURCE, public.SOURCE)
        for path in (catalog.__file__, native.__file__, public.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
