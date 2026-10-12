"""All immutable attrs, times/target/inode negatives, management vs normal generation."""
import copy
import stat
import unittest
from pg1793_warning_fresh_history_contract import match_parent_history,match_peer_history
import pg1780_warning_live_peer_proof_test as peer_fixtures


class History(unittest.TestCase):
    def fixture(self):
        fds={str(i):{'target':'/fixed/'+str(i),'metadata':[1,i,0,0,stat.S_IFREG|0o400,1,1,100,100]}for i in range(101)}
        for i in ['29','32']:fds[i]={'target':'/run','metadata':[1,999,0,0,stat.S_IFDIR|0o755,7,4096,100,100]}
        return {'pid':476087,'ticks':8492401,'authority':'root','fds':fds}

    def test_only_two_shared_times_may_advance(self):
        old=self.fixture();new=copy.deepcopy(old)
        for k in ['29','32']:new['fds'][k]['metadata'][7:]=[101,102]
        self.assertTrue(match_parent_history(old,new))
        for fd,index,value in [('29',0,2),('32',1,998),('29',2,1),('32',4,stat.S_IFREG|0o755),('29',5,8),('32',6,8192),('29',7,99),('32',8,True),('30',7,101)]:
            bad=copy.deepcopy(new);bad['fds'][fd]['metadata'][index]=value
            with self.subTest(fd=fd,index=index),self.assertRaises(ValueError):match_parent_history(old,bad)
        for kind in ['target','pid','newfd','missing']:
            bad=copy.deepcopy(new)
            if kind=='target':bad['fds']['29']['target']='/var'
            elif kind=='pid':bad['pid']=476088
            elif kind=='newfd':bad['fds']['101']=bad['fds']['30']
            else:del bad['fds']['30']
            with self.assertRaises(ValueError):match_parent_history(old,bad)

    def test_normal_pool_may_renew_but_management_may_not(self):
        peers=peer_fixtures.Peers().fixture()
        old={'activity':peers[-1],'allPeers':peers,'bindings':[{'role':r['role'],'ownerPid':{'schubert_app':451130,'schubert_web_session':452144,'schubert_batch':476087}[r['role']],'backendPid':r['pid'],'clientInode':str(i+1),'serverInode':str(i+10)}for i,r in enumerate(peers)],'liveDaemonPeersPreserved':True}
        new=copy.deepcopy(old);new['allPeers'][0]['pid']=500010;new['allPeers'][0]['port']=35010;new['bindings'][0]['backendPid']=500010;new['bindings'][0]['clientInode']='new'
        self.assertTrue(match_peer_history(old,new))
        for change in ['activity','binding','role','extra']:
            bad=copy.deepcopy(new)
            if change=='activity':bad['activity']['port']=36059
            elif change=='binding':bad['bindings'][-1]['clientInode']='foreign'
            elif change=='role':bad['allPeers'][0]['role']='postgres'
            else:bad['bindings'].append(bad['bindings'][0])
            with self.assertRaises(ValueError):match_peer_history(old,bad)


if __name__=='__main__':unittest.main()
