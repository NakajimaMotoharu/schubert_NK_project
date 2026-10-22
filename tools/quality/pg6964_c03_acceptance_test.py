import copy
import json
import unittest

import pg6964_c03_acceptance as p


class C03AcceptanceTest(unittest.TestCase):
    def test_existing_independent_template_contract(self):
        p.config.validate_templates(*[(p.ROOT/x).read_text() for x in p.config.OWNED])
        p.config.validate_roles((p.ROOT/p.config.ROLE_SQL).read_text())

    def test_all_physical_scope_not_only_logical_names(self):
        task = next(v for v in json.loads((p.PMO/'481_PGPT詳細WBS.json').read_text())['tasks'] if v['id'] == p.ID)
        manifest = json.loads(p.PROOF.read_text())
        inventory = json.loads((p.PMO/'485_WBS網羅性・受入対応.json').read_text())['currentPhysicalCandidate']
        p.scope(task,manifest,inventory)
        for field in ('missing','extra','hash','dependency'):
            t,i = copy.deepcopy(task),copy.deepcopy(inventory)
            if field == 'missing':t['ownedArtifacts'].pop()
            elif field == 'extra':i['artifacts'].append(dict(owner=p.ID,path='unregistered',sha256='0'*64))
            elif field == 'hash':next(x for x in i['artifacts'] if x['owner']==p.ID)['sha256']='0'*64
            else:t['dependencies'].append('WBS-F03')
            with self.assertRaises(ValueError):p.scope(t,manifest,i)


if __name__ == '__main__':
    unittest.main()
