"""Independent296 unused187 post against fresh A2 full11/native88, built before stage/place."""
import ast
import json
from pyflakes.api import check
import pg5438_ownership_unused_sources as role
import pg5434_current_full_preservation as current
from pg4992_ssc304_unused_post import qualify_placement as base_qualification

SLOT='pg5444-ownership-unused-post-v1'


def payload():
    role.qualify();raw=current.payload()
    marker='save = base / '+repr(current.SLOT)
    if raw.count(marker)!=1:raise ValueError('one new unused-post evidence namespace')
    raw=raw.replace(marker,'save = base / '+repr(SLOT),1)
    marker="    proof = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in root.iterdir() if p.is_file()}"
    if raw.count(marker)!=1:raise ValueError('one exact still-held reference boundary')
    raw=raw.replace(marker,'\n'.join('    '+line for line in EXTRA.splitlines())+'\n'+marker,1)
    tree=ast.parse(raw);last=tree.body[-1]
    if not(isinstance(last,ast.Expr)and isinstance(last.value,ast.Call)and isinstance(last.value.func,ast.Name)and last.value.func.id=='print'):
        raise ValueError('one final print only after reference-return finally')
    result=last.value.args[0].args[0]
    if not isinstance(result,ast.Dict):raise ValueError('exact existing post summary dict')
    result.keys.extend([None,ast.Constant('newTenReferencesReturnedNormally')])
    result.values.extend([ast.Name(id='candidate_post',ctx=ast.Load()),ast.parse('len(refs)==10',mode='eval').body])
    last_text=ast.get_source_segment(raw,last)
    raw=raw.replace(last_text,ast.unparse(ast.fix_missing_locations(last)),1)
    candidate=json.loads((role.W/'pg5430-candidate-build-v1.safe.json').read_bytes())
    raw='CANDIDATE='+repr(candidate)+'\nBEFORE='+repr(role.BEFORE)+'\nFRESH_FIELDS='+repr(role.view.FIELDS)+'\nVIEW_SLOT='+repr(role.view.SLOT)+'\nfrom pathlib import Path\n'+raw
    if check(raw,'<complete independent296/A2 full11/native88>'):raise ValueError('all emitted standalone static0')
    compile(raw,'<unused187 post, no new publication authority>','exec')
    return raw


EXTRA=r'''
expected={key:value[key]for key in FRESH_FIELDS}
require(len(expected)==11 and len(expected['rows'])==24 and len(expected['units'])==10 and sum(p.endswith('.exec')for p in expected['native'])==88)
for name,item in expected['unitFilesActual'].items():
 p=Path(name);require(metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]==item)
for unit,oldcfg in expected['configuration'].items():
 observed=complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode(),unit);require(observed==oldcfg)
candidate=Path('/opt/schubert-nk/releases/0.1.0-PG5430');manifest_raw=(candidate/'RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(manifest_raw).hexdigest()==CANDIDATE['manifestSha256']);c=json.loads(manifest_raw)
require(c['source']['commit']==CANDIDATE['candidateSource']=='29612b2a484a5ab7418e02a491c4360af7444626'and c['release']=='0.1.0-PG5430'and len(c['artifacts'])==187)
for row in c['artifacts']:
 p=candidate/row['path'];require(p.resolve().is_relative_to(candidate)and not p.is_symlink()and p.is_file()and p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
sig=Path('/var/lib/pgpt-s1-preservation/pg5430-manifest.sig');require(sig.stat().st_size==64 and hashlib.sha256(sig.read_bytes()).hexdigest()==CANDIDATE['signatureSha256'])
command(['/usr/bin/openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],4096)
require(set(str(p.relative_to(candidate))for p in candidate.rglob('*')if p.is_file())=={row['path']for row in c['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'}and not any(p.is_symlink()for p in candidate.rglob('*')))
before=(Path('/var/lib/pgpt-s1-preservation')/VIEW_SLOT/'before.private.json').read_bytes()
require(hashlib.sha256(before).hexdigest()==BEFORE and json.loads(before)==expected)
require(str(Path('/opt/schubert-nk/current').readlink())=='/opt/schubert-nk/releases/0.1.0-PG4980')
require(not os.path.lexists('/var/lib/schubert-nk/maintenance/active')and not list(Path('/run/schubert-nk/startup').glob('*.start.intent')))
candidate_post={'candidateSource':c['source']['commit'],'currentSource':SOURCE,'candidateManifestSha256':CANDIDATE['manifestSha256'],'candidate187SignatureVerified':True,'current187SignatureVerified':True,'all24TablesEqualTwice':True,'allTenKernelJob0':True,'configuration32EveryFieldUnchanged':True,'allUnitFileBytesMetadataUnchanged':True,'originalBackupCredentialOldProofsPreserved':True,'native88Preserved':True,'full11BeforeSha256':BEFORE,'runtimeStartupAndApprovalEpochUnchanged':True,'allClientAdvisoryMA0':True,'candidateUnusedOnly':True,'noSignalsOrStartsOrReloads':True,'candidateNativeCredit':False,'dbWrites':0,'guestEvidenceFilesWritten':1,'formalAccepted':False}
'''


def main():
    value=json.loads((role.W/'pg5442-place-v1.safe.json').read_bytes());qualify_placement(value)
    return current.admission.execute(SLOT,payload(),180)


def qualify_placement(value):
    base_qualification(value)
    expected={'action':'place','candidateSource':role.SOURCE,'installedSource':role.CURRENT,
        'unusedPlacementOnly':True,'startsStopsReloadsSqlWrites0':True,'oldFailedNormalized':False}
    if any(type(value.get(k))is not type(v)or value[k]!=v for k,v in expected.items()):
        raise ValueError('genuine currentA2/candidate296 unused-only placement receipt')


if __name__=='__main__':raise SystemExit(main())
