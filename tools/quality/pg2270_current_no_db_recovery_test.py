"""Independent current generation/actor/OFD/zero-side-effect recovery fixtures."""
import unittest
from types import SimpleNamespace
from pg2270_current_no_db_recovery import prefix,payload,qualify_signature_tuple,SOURCE,metadata9,fresh_parent_source
from pg1651_retained_no_db_readonly_proof_v2 import fd_relation


class CurrentRecoveryTest(unittest.TestCase):
    def test_exact_release_signature_generation_and_negative_fields(self):
        values=['PG2126','pg2126','0.1.0-PG2126',SOURCE,'62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c']
        self.assertTrue(qualify_signature_tuple(*values))
        for i in range(5):
            for wrong in [None,'','pg1846','0fd734195b4d5338f6b7e860e087cce561d49562']:
                changed=list(values);changed[i]=wrong
                with self.assertRaises(ValueError):qualify_signature_tuple(*changed)

    def test_fixed_actual_nochild_nodb_proof_and_full_oracle(self):
        raw=payload('proof');compile(raw,'<independent whole proof>','exec')
        for literal in ['91637','893074','91635','require(not children)','def metadata9(s):','pg2246-native-stop-v1','PG998-native-stop','0e88008b096c404d69d994e1fd45685cbfbdcbd75f11011dd72f07bd4d8ba984','fourBusinessOwnersUnchanged','b2d6f605-61cf-425f-8fbd-12d606f6ee66']:
            self.assertIn(literal,raw)
        self.assertNotIn('pidfd_send_signal',raw)
        self.assertNotIn('StopUnit(',raw)
        self.assertIn("set(OWNED)",prefix())

    def test_stat_metadata_nine_independent_order(self):
        names=['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']
        self.assertEqual((11,12,13,14,15,16,17,18,19),metadata9(SimpleNamespace(**dict(zip(names,range(11,20))))))

    def test_shared_ancestor_only_chronology_and_exact_39_fds(self):
        import copy
        ns={};exec(fresh_parent_source(),ns);guard=ns['fresh_parent']
        actor={'pid':91637,'ticks':893074,'argvSha256':'fixed','authority':{},'cgroup':'fixed','fds':{str(i):{'target':'fixed','metadata':[1,2,3,4,5,6,7,10,10]}for i in range(39)}}
        for fd in ['29','32']:actor['fds'][fd]={'target':'/run','metadata':[1,2,3,4,5,6,7,10,10]}
        new=copy.deepcopy(actor)
        for fd in ['29','32']:new['fds'][fd]['metadata'][7:]=[11,12]
        self.assertTrue(guard(actor,new,12))
        for fd,index,value in [('29',0,9),('29',7,9),('29',8,13),('28',7,11)]:
            bad=copy.deepcopy(new);bad['fds'][fd]['metadata'][index]=value
            with self.assertRaises(ValueError):guard(actor,bad,12)
        bad=copy.deepcopy(new);del bad['fds']['0']
        with self.assertRaises(ValueError):guard(actor,bad,12)

    def test_independent_exact_ofd_relationships(self):
        result=fd_relation('maintenance.lock',['30','33','34'],['34'],lambda a,b:1)
        self.assertEqual([False,False,False],[v['sameOfd']for v in result])
        self.assertEqual([True],[v['sameOfd']for v in fd_relation('startup-admission.lock',['43','128'],['43','128'],lambda a,b:0)])
        for name,linked,locks in [('maintenance.lock',['34'],['34']),('startup-admission.lock',['43','128'],['43'])]:
            with self.assertRaises(ValueError):fd_relation(name,linked,locks,lambda a,b:0)


if __name__=='__main__':unittest.main()
