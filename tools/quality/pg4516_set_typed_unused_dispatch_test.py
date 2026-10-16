"""Physical stage paths, all modes and complete frozen v5 are one contract."""
import ast
import io
import json
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4516_set_typed_unused_dispatch as s


class NewFiniteOperator(unittest.TestCase):
    def test_actual_source_same_new_path_and_stage_inspect_place_dependencies(self):
        raw=s.source();compile(raw,'<newv5 operator>','exec')
        literals=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)and isinstance(n.value,str)]
        for name in ['pg4500-frozen-v1.safe.json','pg4516-stage-v1.exit','pg4516-inspect-v1.exit','/home/ubuntu/pg4516-fixed-stage-v1',s.role.ARCHIVE,s.role.SOURCE]:self.assertIn(name,literals)
        self.assertNotIn('pg4468-existing-input-stage-v1/manifest.safe.json',literals)
        self.assertIn('/home/ubuntu/pg4516-fixed-stage-v1/',s.stage_source());self.assertNotIn('/home/ubuntu/pg4462-fixed-stage-v1/',s.stage_source())
        self.assertEqual(0,check("DIGEST='literal'\nFILES={}\n"+s.stage_source(),'<new stage>',Reporter(io.StringIO(),io.StringIO())))

    def test_namespace_uses_frozen_new_set_source_not_original_tuple(self):
        candidate=json.loads((s.role.W/'pg4432-candidate-build-v1.safe.json').read_bytes());ns=s.runtime_namespace(candidate)
        self.assertEqual(s.TARGET,ns['TARGET']);self.assertEqual(s.GUEST,ns['GUEST']);self.assertEqual(s.role.REMOTE,ns['REMOTE'])
        self.assertIs(s.role.sources,ns['sources']);self.assertIn("set(('Id',",ns['sources']()['pg4444_native_refs.py'])


if __name__=='__main__':unittest.main()
