"""Independent literal role/native metadata vectors, no VM/Production PT credit."""
import copy
import json
import pathlib
import unittest

from pg534_native_role_contract import classify, inventory, terminal_units


class NativeRoleContractTest(unittest.TestCase):
    def test_current_terminal_unit_phase_actor_declaration_and_unknown_refuse(self):
        path = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg534-role-current-readonly-v1.private.json')
        units = json.loads(path.read_text())['units']
        self.assertEqual({'terminalUnitsDeclared': 2, 'metadataOnly': True, 'startupAuthorized': False},
                         terminal_units(units))
        for unit in ('schubert-nk-bootstrap-admin.service', 'schubert-nk-inbox-inspector.service'):
            for key in ('Id', 'LoadState', 'User', 'Group', 'Type', 'Restart', 'RemainAfterExit',
                        'MainPID', 'ControlPID', 'Job', 'SuccessExitStatus', 'KillMode',
                        'SendSIGKILL', 'ExecStart'):
                for fault in ('foreign', 'null', 'missing'):
                    bad = copy.deepcopy(units)
                    if fault == 'missing':
                        del bad[unit][key]
                    else:
                        bad[unit][key] = None if fault == 'null' else 'foreign'
                    with self.subTest(unit=unit, key=key, fault=fault), self.assertRaises(ValueError):
                        terminal_units(bad)
        bad = copy.deepcopy(units)
        bad['schubert-nk-bootstrap-admin.service']['ExecStart'] = bad['schubert-nk-bootstrap-admin.service']['ExecStart'].replace('BOOTSTRAP-', 'API-')
        with self.assertRaises(ValueError):
            terminal_units(bad)
        for bad in (None, {}, [], {**units, 'root-bootstrapadmin196': {}}):
            with self.assertRaises(ValueError):
                terminal_units(bad)

    def test_literal_required10_and_present8_missing_two(self):
        actual = classify(['parent', 'backup', 'cleanup', 'expiry', 'root-api193', 'root-web193',
                           'ordinary-api193', 'ordinary-web193'])
        self.assertEqual(['ordinary-bootstrap196', 'ordinary-inspector196'], actual['missing'])
        self.assertEqual(10, len(actual['requiredRoles']))
        self.assertFalse(actual['nativeAccepted'])
        self.assertFalse(actual['coverageAccepted'])

    def test_alias_phantom_duplicate_null_and_unknown_refuse(self):
        for roles in (None, {}, ['root-bootstrapadmin196'], ['ordinary-bootstrapadmin196'],
                      ['parent', 'parent'], ['parent', None], ['foreign']):
            with self.subTest(roles=roles), self.assertRaises(ValueError):
                classify(roles)

    def test_real_readonly_native8_metadata_no_authority_and_negative_changes(self):
        path = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg534-role-current-readonly-v1.private.json')
        native = json.loads(path.read_text())['native']
        actual = inventory(native)
        self.assertEqual(8, len(actual['present']))
        self.assertEqual(['ordinary-bootstrap196', 'ordinary-inspector196'], actual['missing'])
        for key, value in (('uid', 777), ('gid', 777), ('mode', 0o100640), ('size', 0),
                           ('size', 16777217), ('size', True), ('name', 'foreign.exec')):
            bad = copy.deepcopy(native)
            bad['parent'][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                inventory(bad)
        for change in ('missing-dir', 'foreign-dir', 'duplicate-file', 'unknown-row', 'null-row'):
            bad = copy.deepcopy(native)
            if change == 'missing-dir':
                del bad['ordinary-bootstrap196']
            elif change == 'foreign-dir':
                bad['root-bootstrapadmin196'] = []
            elif change == 'duplicate-file':
                bad['parent'].append(copy.deepcopy(bad['parent'][0]))
            elif change == 'unknown-row':
                bad['parent'][0]['foreign'] = 'unadmitted'
            else:
                bad['parent'][0] = None
            with self.subTest(change=change), self.assertRaises(ValueError):
                inventory(bad)


if __name__ == '__main__':
    unittest.main()
