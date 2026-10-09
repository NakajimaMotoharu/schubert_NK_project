"""Literal retained trees/missing/extra predicates and finite new stage source contract."""
import ast,unittest
from pg936_stage_candidate import source,payload,TREE_PROJECTION
class Test(unittest.TestCase):
    def test_current_tree_schema_groups_exact_entries_without_loss(self):
        env={};raw=TREE_PROJECTION[:TREE_PROJECTION.index("baseline['trees']")];exec('import pathlib\n'+raw,env)
        record={f:{'/'+f:{'metadata':[0]*9,'sha256':None},'/'+f+'/child':{'metadata':[1]*9,'sha256':'a'*64}}for f in ('originals','backup','credentials','startup','oldProofs','native')}
        got=env['retained_trees'](record);self.assertEqual(6,len(got));self.assertEqual(12,sum(len(v)for v in got.values()))
        for field,rows in record.items():self.assertEqual(rows,got['/'+field])
        for mode in ('absent','empty','badfields','badmetadata','relative'):
            import copy
            bad=copy.deepcopy(record)
            if mode=='absent':del bad['native']
            elif mode=='empty':bad['native']={}
            elif mode=='badfields':bad['native']['/native']['ignored']=True
            elif mode=='badmetadata':bad['native']['/native']['metadata']=[0]*8
            else:bad['native']['relative']=bad['native'].pop('/native')
            with self.assertRaises((AssertionError,KeyError)):env['retained_trees'](bad)
    def test_finite_pins_full_resource_before_after_and_no_start(self):
        raw=source();body=payload();ast.parse(raw);ast.parse(body)
        for expected in ("SOURCE = '40ef6e894573d2ffab1d1732124960f9c98d5f97'","RELEASE = W / 'pg932-release-v1'","PG936_UNUSED_CANDIDATE_PLACED","pg936-stage-v6","pg932-manifest-v1.sig"):
            self.assertIn(expected,raw)
        for expected in ("old=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG862')",'pg935-current-preflight-v1/after.private.json','4aa97f5a256d8d74283f83310b6c8e042dc0f8ca0bcd957bc68abed2fce257cb',"baseline['trees']=retained_trees(baseline)",'==584','== 584','before=protected();assert before==protected()','assert protected()==before','manager.RefUnit(unit)','manager.UnrefUnit(unit)','signature_bytes=signature.read_bytes()','tar.extractall(root,filter='):
            self.assertIn(expected,body)
        self.assertLess(body.index('self.manager.RefUnit(unit)'),body.index('before=protected()'))
        for forbidden in ('StartUnit','StopUnit','RestartUnit','ReloadUnit','daemon-reload','force-reload','ALTER TABLE','insert into','pg492'):
            self.assertNotIn(forbidden,body)
if __name__=='__main__':unittest.main()
