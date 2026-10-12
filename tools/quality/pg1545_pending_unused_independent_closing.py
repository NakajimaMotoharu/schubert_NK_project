"""Separate readonly full current and unused signed-candidate closing; no placement replay."""
import inspect
import pg1511_publication_gc_closing as prior

EXTRA=r'''
placement=BASE/'pg1539-pending-unused-placement-v1'
raw=(placement/'after.private.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='0891ca388aa40417035900b2cf782e5b75308fba8ae13e96ac6d87bc5709cee0')
placed=json.loads(raw);require(placed['unusedCandidatePlaced']is True and placed['currentApprovalEpochDbUnitsUnchanged']is True)
require(placed['parent']['pid']==101487 and placed['parent']['ticks']==2525313 and placed['parent']['argvSha256']=='94458fec066f6ddee8dc1b80dae30c15cffca40a1d3dce682fcd0e054dff6e3f'and not pathlib.Path('/proc/101487').exists())
require((placement/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\nunusedPlacement=true\nepochDbBusinessWrites=0\n')
require(hashlib.sha256(json.dumps(placed['current'],sort_keys=True).encode()).hexdigest()=='7cc53215980eadb5d6d788d1df0b997111b3f6beabc6eef4803f4506afb36ea5')
require(contract.free_flocks(pathlib.Path('/proc/locks').read_text().splitlines(),placed['parent']['locks']))
for name,m in placed['parent']['locks'].items():require(metadata(ROOT/name)==m)
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1544');sig=BASE/'pg1544-manifest.sig';bom='e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c'
manifest=(candidate/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(manifest).hexdigest()==bom)
data=json.loads(manifest);require(data['source']['commit']=='4d6bcbddb417b76d27e52d5d9640752c300edccf'and data['release']=='0.1.0-PG1544'and len(data['artifacts'])==187 and data['versions']['schema']=='028'and len(data['migrations'])==29)
require(len(list((candidate/'db/migration').glob('*.sql')))==28)
sums=contract.canonical_sum_bytes(data['artifacts'],bom);require((candidate/'SHA256SUMS').read_bytes()==sums)
records=data['artifacts']+[{'path':'RELEASE-MANIFEST.json','size':len(manifest),'sha256':bom},{'path':'SHA256SUMS','size':len(sums),'sha256':hashlib.sha256(sums).hexdigest()}]
newheld=[]
try:
 newheld.append(contract.HeldInventory(str(candidate),records,0).open())
 newheld.append(contract.HeldInventory(str(BASE),[{'path':'pg1544-manifest.sig','size':64,'sha256':'fed7f4c24a2356f095aed4310c5a826f9896452cc731971fbd3589f94ae6d232'}],0).open_file())
 first_candidate=[h.capture()for h in newheld]
 require(sig.stat().st_uid==sig.stat().st_gid==0 and stat.S_IMODE(sig.stat().st_mode)==0o400)
 command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],4096)
 require(first_candidate==[h.capture()for h in newheld])
finally:
 for h in reversed(newheld):h.close()
unused_candidate_normal=True
'''

def payload():
    raw=prior.payload().replace("POST=BASE/'pg1511-publication-gc-closing-v1'", "POST=BASE/'pg1545-pending-unused-independent-closing-v1'")
    marker='recovery=BASE/'
    if raw.count(marker)!=1:raise ValueError('fixed independent pending closing boundary refused')
    raw=raw.replace(marker,EXTRA+'\n'+marker).replace("'gcKinds':gc_kinds", "'unusedCandidateSigned187Qualified':unused_candidate_normal,'placementOwnerPeerAndLocksGone':True,'candidateNotActivated':True,'gcKinds':gc_kinds")
    compile(raw,'<independent failed-partial candidate/current closing>','exec');return raw

def main():
    raw=inspect.getsource(prior.previous.main).replace('pg1508-publication-recovery-closing-v3','pg1545-pending-unused-independent-closing-v1')
    ns={**prior.previous.__dict__,'payload':payload};exec(compile(raw,'<new-only pending unused closing transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
