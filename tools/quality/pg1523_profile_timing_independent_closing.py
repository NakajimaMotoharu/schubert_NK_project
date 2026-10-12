"""Fresh full readonly closing and independent arithmetic for actual original IO timings."""
import inspect
import pg1511_publication_gc_closing as previous

EXTRA=r'''
profile=BASE/'pg1519-original-component-profile-v2'
profile_raw=(profile/'after.private.json').read_bytes();require(hashlib.sha256(profile_raw).hexdigest()=='91a41c9e139d987f5b74bb817ab01bbc57423957a5251084eb2308b19558d1b3')
profile_after=json.loads(profile_raw);require(profile_after['mutation0']is True and profile_after['parent']['pid']==99996 and profile_after['parent']['ticks']==1933535 and not pathlib.Path('/proc/99996').exists())
require((profile/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\nreadonlyProfile=true\nepochDbBusinessWrites=0\n')
require(hashlib.sha256(json.dumps(profile_after['current'],sort_keys=True).encode()).hexdigest()=='7cc53215980eadb5d6d788d1df0b997111b3f6beabc6eef4803f4506afb36ea5')
require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),profile_after['parent']['locks']))
for name,m in profile_after['parent']['locks'].items():require(metadata(ROOT/name)==m)
data=[]
for name,digest in [('original-profile.safe.jsonl','f94d709f60a62347caf2f1c716a7acc35e2bb218c582d6c1fbe61a37c8be01e9'),('components.safe.jsonl','1925bf907309dbfbaff14f431372e5e98806f40e5ed5e1bd0353eb8861aaed9f')]:
 b=(profile/name).read_bytes();require(hashlib.sha256(b).hexdigest()==digest);data.append([json.loads(x)for x in b.splitlines()])
require(len(data[0])==len(data[1])==4)
component_counts={'attributes':2912,'filesystem':2912,'acl':2912,'statvfs':2912,'open':272,'openNames':12}
for t,row in zip(*data):
 require(set(t)=={'twoWholeGraphObservationsNanos','completed'}and t['completed']is False)
 require(set(row)=={'wholeTwoObserveNanos','components'}and row['wholeTwoObserveNanos']==t['twoWholeGraphObservationsNanos'])
 require(type(row['wholeTwoObserveNanos'])is int and row['wholeTwoObserveNanos']>0 and set(row['components'])==set(component_counts))
 for name,c in row['components'].items():require(set(c)=={'calls','nanos'}and type(c['calls'])is int and c['calls']==component_counts[name]and type(c['nanos'])is int and 0<=c['nanos']<=row['wholeTwoObserveNanos'])
 require(sum(c['nanos']for c in row['components'].values())<=row['wholeTwoObserveNanos'])
'''
def payload():
 raw=previous.payload().replace("POST=BASE/'pg1511-publication-gc-closing-v1'","POST=BASE/'pg1523-profile-timing-independent-closing-v1'")
 marker='recovery=BASE/';assert raw.count(marker)==1
 raw=raw.replace(marker,EXTRA+'\n'+marker)
 marker="'gcKinds':gc_kinds";assert raw.count(marker)==1
 raw=raw.replace(marker,"'profileComponentsQualified':True,'profileOwnerPeerAndLocksGone':True,'gcKinds':gc_kinds")
 compile(raw,'<actual timing independent fullclosing>','exec');return raw
def main():
 raw=inspect.getsource(previous.previous.main).replace('pg1508-publication-recovery-closing-v3','pg1523-profile-timing-independent-closing-v1')
 ns={**previous.previous.__dict__,'payload':payload};exec(compile(raw,'<new readonly timing closing transport>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
