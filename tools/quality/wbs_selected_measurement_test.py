"""Independent pinned selected-result negatives; management assertions, Production PT credit0."""
import copy
import json
import pathlib
import subprocess
import unittest
from unittest.mock import patch

import wbs_progress_audit as audit


class SelectedMeasurementTest(unittest.TestCase):
    @staticmethod
    def selected_snapshot(name):
        # Explicit immutable selected-result fixture, not a claim about the new all-six source.
        return json.loads(subprocess.check_output([
            'git', 'show', '09528f72f:documents/400_PGPT/470_PMO/' + name], cwd=audit.ROOT))

    def setUp(self):
        snapshot = self.selected_snapshot('486_WBS現行実績.json')
        self.row = next(r for r in snapshot['rows'] if r['id'] == 'WBS-P018-02')
        self.source = snapshot['source']
        self.prior = '/home/mini/codex/project1/work/pgpt-runs/PG379/pg495-host'
        self.manifest = json.loads((audit.ROOT / self.row['measurementOverride']['manifest']).read_text())

    def test_owned_five_families_are_all_four_counter_zero(self):
        values = audit.selected_measurement(self.row, self.source, self.prior)['bootstrap']
        for family in ('ReleaseApproval', 'ReleaseInventory', 'ReleasePayloadVerification',
                       'ReleaseSignatureVerifier', 'StartupReleaseManifest'):
            actual = values['dev/codex/schubert/nk/bootstrap/' + family]
            self.assertEqual([0, 0, 0, 0], [actual[k][0] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')])
            self.assertGreater(sum(v[1] for v in actual.values()), 0)

    def test_override_hash_source_run_wbs_and_production_mismatch_refuse(self):
        for key, value in (('manifestSha256', '0' * 64), ('source', 'b' * 40), ('run', 'foreign')):
            row = copy.deepcopy(self.row)
            row['measurementOverride'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                audit.selected_measurement(row, self.source, self.prior)
        row = copy.deepcopy(self.row)
        row['id'] = 'WBS-FOREIGN'
        with self.assertRaises(ValueError):
            audit.selected_measurement(row, self.source, self.prior)
        with self.assertRaises(ValueError):
            audit.selected_measurement(self.row, 'b' * 40, self.prior)

    def test_incomplete_changed_and_formal_claim_are_not_selected_success(self):
        for key, value in (('actualExit', 1), ('FES', 1), ('staticIssues', 1),
                           ('sourceUnchanged', False), ('formalUpdated', True),
                           ('acceptedWbsDelta', 1), ('modules', [])):
            manifest = copy.deepcopy(self.manifest)
            manifest[key] = value
            with self.subTest(key=key), patch.object(audit, 'read_json', return_value=manifest):
                with self.assertRaises(ValueError):
                    audit.selected_measurement(self.row, self.source, self.prior)

    def test_xml_jar_static_result_and_baseline_binding_are_all_required(self):
        for key, value in (('coverageXmlSha256', '0' * 64), ('jarSha256', '0' * 64),
                           ('priorJarSha256', '0' * 64), ('spotbugsXmlSha256', '0' * 64),
                           ('priorJar', str(pathlib.Path(self.prior) / 'foreign.jar')),
                           ('pt', {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0})):
            manifest = copy.deepcopy(self.manifest)
            manifest['modules'][0][key] = value
            with self.subTest(key=key), patch.object(audit, 'read_json', return_value=manifest):
                with self.assertRaises(ValueError):
                    audit.selected_measurement(self.row, self.source, self.prior)

    def test_owner_module_cannot_be_omitted_to_hide_gaps(self):
        snapshot = self.selected_snapshot('486_WBS現行実績.json')
        inventory = self.selected_snapshot('485_WBS網羅性・受入対応.json')
        manifest = copy.deepcopy(self.manifest)
        manifest['modules'] = [m for m in manifest['modules'] if m['module'] == 'storage']
        target = audit.ROOT / self.row['measurementOverride']['manifest']
        real_read = audit.read_json
        with patch.object(audit, 'read_json', side_effect=lambda p: manifest if p == target else real_read(p)):
            with self.assertRaisesRegex(ValueError, 'selected omitted owner module'):
                audit.check_measurement(snapshot, inventory)


    def test_declaration_interface_is_not_an_executable_family(self):
        snapshot = self.selected_snapshot('486_WBS現行実績.json')
        inventory = self.selected_snapshot('485_WBS網羅性・受入対応.json')
        row = next(r for r in snapshot['rows'] if r['id'] == 'WBS-P017-12')
        owned = [a for a in inventory['artifacts'] if a['owner'] == row['id'] and a['kind'] == 'JAVA']
        self.assertEqual(16, len(owned))
        self.assertEqual(1, sum(a.get('counterApplicability') == 'NO_EXECUTABLE_INTERFACE' for a in owned))
        self.assertEqual(15, row['measuredFamilies'])
        self.assertEqual(1, row['nonExecutableFamilies'])
        audit.check_measurement(snapshot, inventory)
        bad = copy.deepcopy(snapshot)
        next(r for r in bad['rows'] if r['id'] == row['id'])['measuredFamilies'] = 16
        with self.assertRaisesRegex(ValueError, 'measurement drift: WBS-P017-12'):
            audit.check_measurement(bad, inventory)
        for owner in ('WBS-P017-04', 'WBS-P018-02'):
            self.assertFalse(any(a.get('counterApplicability') == 'NO_EXECUTABLE_INTERFACE'
                                 for a in inventory['artifacts'] if a['owner'] == owner and a['kind'] == 'JAVA'))

    def test_historical_fresh_six_and_later_selected_result_keep_their_own_bindings(self):
        # BUG1394: retain the exact969/PG541 oracle at its immutable fixture,
        # never apply old source expectations to a newer live acceptance snapshot.
        ref = '5121fc1ad580d19afdf01bc60c10185f03c1c0bb:documents/400_PGPT/470_PMO/'
        snapshot = json.loads(subprocess.check_output(['git','show',ref+'486_WBS現行実績.json'],cwd=audit.ROOT))
        inventory = json.loads(subprocess.check_output(['git','show',ref+'485_WBS網羅性・受入対応.json'],cwd=audit.ROOT))
        self.assertEqual('969d8ded10c0bf5841d9e3a5c531e922caf4a24a', snapshot['source'])
        self.assertEqual(snapshot['source'], inventory['source'])
        self.assertEqual(inventory['measurementBindings']['run'], snapshot['measurementRun'])
        selected = [row for row in snapshot['rows'] if 'measurementOverride' in row]
        self.assertEqual(['WBS-P017-12'], [row['id'] for row in selected])
        self.assertEqual('PG541-timeout-cardinality-selected-v1', selected[0]['measurementOverride']['run'])
        for row in snapshot['rows']:
            if row['measurementStatus'] == 'VM_STEP_VERIFIED':
                self.assertEqual('a2e98ce9e96c42425921e3686e8ae7a94bff9e6c', row['measurementSource'])
                self.assertFalse(row['appliesToPendingHostCandidate'])
        audit.check_measurement(snapshot, inventory)


if __name__ == '__main__':
    unittest.main()
