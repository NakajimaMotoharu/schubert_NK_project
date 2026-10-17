import ast
import hashlib
import json
import unittest
from pyflakes.api import check
import pg4850_ssc301_302_static as role


class ActualStatic(unittest.TestCase):
    def test_new_qualified_jar_paths_and_whole_emission(self):
        old=json.loads((role.W/'pg4700-ssc299-static-v1/manifest.safe.json').read_bytes())['result']
        new={m:hashlib.sha256(('fixture '+m).encode()).hexdigest()for m in ('protocol','storage','bootstrap','api','web','batch')}
        values=role.current_auxiliary(old['auxJarSha256'],new)
        self.assertEqual(len(old['auxJarSha256']),len(values))
        self.assertEqual(6,sum('/source-full-PG4844/'in p for p in values))
        data={'source':role.SOURCE,'qualifiedJars':new,'sourceSha256':old['allMainSha256'],'includeCheckstyle':True}
        raw=role.server_source(data);ast.parse(raw)
        self.assertEqual(0,check(raw,'<complete new static payload>'))
        self.assertIn('PG4844 current3761 ABI',raw)
        self.assertIn('runs/PG4700-ssc299-static-v1/manifest.safe.json',raw)
        self.assertIn('actualRuleCountDeltaFromOld825e',raw)
        self.assertNotIn('source-full-PG4694',raw)


if __name__=='__main__':unittest.main()
