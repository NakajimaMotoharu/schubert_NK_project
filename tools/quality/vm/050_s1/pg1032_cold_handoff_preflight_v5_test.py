import ast
import unittest
from pg1032_cold_handoff_preflight_v5 import payload, missing_globals


class Closure(unittest.TestCase):
    def test_snapshot_and_full32_transitive_dependencies_closed(self):
        raw = payload()
        self.assertEqual([], missing_globals(raw, ['snapshot', 'complete_configuration', 'read', 'actor', 'controls']))
        tree = ast.parse(raw)
        missing = ast.unparse(ast.Module(body=[n for n in tree.body if not isinstance(n, ast.FunctionDef) or n.name != 'configuration_value'], type_ignores=[]))
        self.assertEqual(['configuration_value'], missing_globals(missing, ['complete_configuration']))

    def test_independent_full32_actual_function_and_negative_fields(self):
        raw = payload()
        tree = ast.parse(raw)
        names = {'configuration_value', 'complete_configuration'}
        body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names
                or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CONFIG_FIELDS' for t in n.targets)]
        namespace = {}
        exec(compile(ast.Module(body=body, type_ignores=[]), '<qualified-config-functions>', 'exec'), namespace)
        # Handwritten complete field fixture; expected values are NOT produced by
        # a production or extracted parser. Only Requires/After are unordered.
        expected = {'Id':'schubert-nk-api.service','Type':'notify','Restart':'no','RemainAfterExit':'no',
            'KillMode':'control-group','SendSIGKILL':'no','TimeoutStartUSec':'5min','TimeoutStopUSec':'1min',
            'ExecStart':'literal','ExecStop':'','User':'schubert-api','Group':'schubert-api',
            'SupplementaryGroups':'schubert-config','NoNewPrivileges':'yes','CapabilityBoundingSet':'',
            'AmbientCapabilities':'','ProtectSystem':'strict','ProtectHome':'yes','PrivateTmp':'yes',
            'PrivateDevices':'yes','RestrictAddressFamilies':'AF_UNIX AF_INET','ReadWritePaths':'/run/schubert-nk',
            'ReadOnlyPaths':'/opt/schubert-nk','Requires':'a.service z.service','After':'a.service z.service',
            'FragmentPath':'/etc/systemd/system/schubert-nk-api.service','DropInPaths':'',
            'RestrictSUIDSGID':'yes','UMask':'0077','LimitCORE':'0','MemoryMax':'1073741824','TasksMax':'128'}
        lines = [k+'='+('z.service a.service' if k in ('Requires','After') else v) for k,v in expected.items()]
        literal = '\n'.join(lines)+'\n'
        self.assertEqual(expected, namespace['complete_configuration'](literal, 'schubert-nk-api.service'))
        for bad in (None, literal+'Unknown=value\n', literal+lines[0]+'\n', literal.replace('Type=notify\n',''), literal.replace('z.service a.service','a.service a.service')):
            with self.assertRaises(ValueError): namespace['complete_configuration'](bad, 'schubert-nk-api.service')


if __name__ == '__main__': unittest.main()
