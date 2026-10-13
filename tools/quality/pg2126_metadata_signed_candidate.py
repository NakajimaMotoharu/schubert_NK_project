"""Current qualified three-semantic/one-debug Main candidate, host signing only; never deploys."""
import inspect
import pg1638_api_signed_candidate as prior
from pg2124_metadata_boundary_full_six import production

W,P,T=prior.W,prior.P,prior.T
OLD=W/'pg1846-release-v1'
NEXT=W/'pg2126-release-v1'
FROZEN=W/'pg2126-frozen-six-v1'
SIG=P/'pg2126-manifest-v1.sig'
OLD_SOURCE='0fd734195b4d5338f6b7e860e087cce561d49562'
OLD_BOM='ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7'
CHANGED={
    'batch:dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration.class',
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext.class',
    'batch:dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class',
    'batch:dev/codex/schubert/nk/batch/file/MorningBackupArtifacts.class',
}

def validate_gate(outer,source):
    expected={'actualExit':0,'productionSource':source,'tests':3631,'suites':540,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0,'classifierFourCounters100':True,'global100':False,'formalAccepted':False,'semanticChangedClasses':3,'debugOnlyChangedClasses':1}
    if type(outer)is not dict or type(outer.get('actualExit'))is not int or outer['actualExit']!=0:
        raise ValueError('actual independent current full qualification required')
    gate=outer.get('result')
    if type(gate)is not dict or any(type(gate.get(k))is not type(v)or gate[k]!=v for k,v in expected.items()):
        raise ValueError('exact current-source full/quality required')
    if gate.get('changedClasses')!=sorted(CHANGED)or gate.get('addedClasses')!=[]:
        raise ValueError('all four actual changed Main bytes required')
    proof=gate.get('debugLineQualification');name='dev/codex/schubert/nk/batch/platform/RootStartupContext$NativeIo.class'
    if type(proof)is not dict or set(proof)!={name}:
        raise ValueError('independent native debug byte proof required')
    detail=proof[name]
    if type(detail)is not dict or set(detail)!={'lineEntries','lineOffset','nonLineBytesIdentical'}or type(detail['lineEntries'])is not int or detail['lineEntries']<=0 or type(detail['lineOffset'])is not int or detail['lineOffset']!=1 or detail['nonLineBytesIdentical']is not True:
        raise ValueError('fixed all-LNT/non-LNT proof required')
    hashes=gate.get('jarHashes')
    if type(hashes)is not dict or set(hashes)!=set(prior.MODULES)or any(type(h)is not str or len(h)!=64 or set(h)-set('0123456789abcdef')for h in hashes.values()):
        raise ValueError('six qualified jar hashes required')
    return gate

def verify_delta(before,after):
    if type(before)is not dict or type(after)is not dict or set(before)!=set(prior.MODULES)or set(after)!=set(before):
        raise ValueError('fixed six Main inventories required')
    changed=set()
    for m in before:
        if set(before[m])!=set(after[m]):raise ValueError('no added/removed Main classes permitted')
        changed.update(m+':'+n for n in before[m]if before[m][n]!=after[m][n])
    if changed!=CHANGED or sum(len(v)for v in after.values())!=1643:
        raise ValueError('exact current four-class physical delta required')
    return 1643

def receive(module):
    raw=inspect.getsource(prior.transfer.receive).replace('PG1532','PG2124').replace('pg1535','pg2126')
    ns={**prior.transfer.__dict__,'FROZEN':FROZEN}
    exec(compile(raw,'<qualified current six artifact transport>','exec'),ns)
    return ns['receive'](module)

def main_source():
    raw=inspect.getsource(prior.main).replace('pg1638','pg2126').replace('PG1638','PG2126').replace('PG1544','PG1846')
    raw=raw.replace('1683dd9f6de00e71d2317d9af3cd50400a37bf4e',production())
    raw=raw.replace('pg1636-api-boundary-full-qualified-v1','pg2125-metadata-boundary-full-qualified-v1').replace('from pg1636_api_boundary_full_qualification import server','from pg2125_metadata_boundary_full_qualification import server')
    raw=raw.replace("{'VERSION', 'api/api.jar'} <= changed","{'VERSION', 'operations/batch.jar'} <= changed")
    raw=raw.replace("'tests': 3596, 'suites': 532","'tests': 3631, 'suites': 540").replace("'changedClasses': 3, 'addedClasses': 6","'changedClasses': 4, 'semanticChangedClasses':3, 'debugOnlyChangedClasses':1, 'addedClasses': 0")
    compile(raw,'<host-only current source signing>','exec');return raw

def main():
    ns={**prior.__dict__,'__file__':__file__,'PRODUCTION':production(),'OLD_SOURCE':OLD_SOURCE,'OLD_BOM':OLD_BOM,'OLD':OLD,'NEXT':NEXT,'FROZEN':FROZEN,'SIG':SIG,'receive':receive,'validate_gate':validate_gate,'verify_delta':verify_delta}
    exec(compile(main_source(),'<current host signing entry>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
