"""Independent PG6542 lexical reference/proof bytes + exact original finding multiplicity."""
import ast
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
from host_tool_invocation import capture,verify
from public_blob_scan import sha
from pg8993_public_ancestor_provenance_post_v2 import consume_pending

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW=BASE/'PG9000-public-token-provenance-v1'
PRIOR=BASE/'PG8980-public-finding-provenance-v1'
ANCESTOR=BASE/'PG8990-public-ancestor-provenance-v1'
SNAPSHOT=ROOT.parent/'pgpt-runs/PG379/pg8968-public-blob-scan-v1/tracked'
OUT=BASE/'PG9002-public-token-provenance-post-v1'
REFERENCE=ROOT/'tools/quality/pg6542_jdbc_catch_inventory.py'
REFERENCE_SHA='9be2472be16788ab9babb537d01b84f47010ba65e31022184070457d6052dcb4'


def reference_sites():
    assert sha(REFERENCE.read_bytes())==REFERENCE_SHA
    tree=ast.parse(REFERENCE.read_text())
    selected=[node for node in tree.body if
              (isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='LEX')
              or (isinstance(node,ast.FunctionDef) and node.name in {'balanced','sites'})]
    assert len(selected)==3
    # Only reviewed public pure lexical definitions, never old main/imports/private input functions.
    namespace={'re':re,'json':json,'hashlib':hashlib,'__builtins__':{
        'len':len,'range':range,'enumerate':enumerate,'any':any,'dict':dict,'ValueError':ValueError}}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(REFERENCE),'exec'),namespace)
    return namespace['sites']


def validate_proof(proof,inventory,sites,cache):
    kind=proof['proofKind']
    if kind=='PUBLIC_JAVA_SQLCATCH_TOKEN_DIGEST':
        expected={'proofKind','path','sourceSha256','gitObject','catchLine','publicTokenDigest','normalizationReferenceSha256'}
        if set(proof)!=expected or proof['normalizationReferenceSha256']!=REFERENCE_SHA:
            raise ValueError('unbound public token definition')
        name=proof['path'];entry=inventory.get(name)
        if entry is None or entry['sha256']!=proof['sourceSha256'] or entry['gitObject']!=proof['gitObject']:
            raise ValueError('unbound public Java source')
        if name not in cache:
            data=(SNAPSHOT/name).read_bytes()
            if sha(data)!=entry['sha256']:raise ValueError('actual public Java bytes changed')
            cache[name]=sites(data.decode('utf-8'))
        matching=[row for row in cache[name] if row['beginLine']==proof['catchLine']]
        if len(matching)!=1 or matching[0]['bodyTokenSha256']!=proof['publicTokenDigest']:
            raise ValueError('independent public token transform mismatch')
        return proof['publicTokenDigest']
    if kind=='CURRENT_PUBLIC_BLOB':
        expected={'proofKind','path','sha256','gitObject'}
        if set(proof)!=expected or proof['path'] not in inventory:raise ValueError('unknown public blob')
        entry=inventory[proof['path']]
        data=(SNAPSHOT/proof['path']).read_bytes()
        if sha(data)!=proof['sha256'] or entry['gitObject']!=proof['gitObject']:
            raise ValueError('public blob proof mismatch')
        return proof['sha256']
    if kind=='HASH_OF_PUBLIC_REACHABLE_ANCESTOR_GIT_BLOB_NOT_A_SECRET_HASH':
        published=json.loads((ANCESTOR/'public-proofs.json').read_bytes())
        if proof not in published:raise ValueError('unknown ancestor proof')
        data=subprocess.check_output(['git','cat-file','blob',proof['gitObject']],cwd=ROOT,
             env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'},timeout=30)
        if sha(data)!=proof['sha256']:raise ValueError('actual ancestor proof mismatch')
        return proof['sha256']
    raise ValueError('unsupported public provenance')


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    manifest=json.loads((RAW/'manifest.json').read_bytes())
    assert manifest['actualExit']==0 and manifest['source']=='fb9fce0f91de3d9fdfa634fe277592700f915e45'
    assert sha((RAW/'updates.json').read_bytes())==manifest['updatesSha256']
    assert sha((PRIOR/'manifest.json').read_bytes())==manifest['priorManifestSha256']
    assert sha((ANCESTOR/'manifest.json').read_bytes())==manifest['ancestorManifestSha256']
    fields=('path','ruleId','startLine','endLine','inputSha256')
    key=lambda row:tuple(row[name] for name in fields)
    pending=Counter(key(row) for row in json.loads((PRIOR/'classifications.json').read_bytes()) if row['disposition']=='UNCLASSIFIED')
    for row in json.loads((ANCESTOR/'updates.json').read_bytes()):consume_pending(pending,key(row))
    assert sum(pending.values())==9960
    inventory={row['path']:row for row in json.loads((BASE/'PG8968-public-blob-scan-v1/inventory.json').read_bytes())['rows']}
    rules=json.loads((BASE/'PG8979-gitleaks-rule-provenance-v1/manifest.json').read_bytes())['rules']
    sites=reference_sites();site_cache={};line_cache={};proof_cache={}
    updates=json.loads((RAW/'updates.json').read_bytes())
    allowed=set(fields)|{'disposition','reason','priorDisposition','exactCaptureCount','publicArtifactProofs'}
    for row in updates:
        assert set(row)==allowed and row['priorDisposition']=='UNCLASSIFIED'
        consume_pending(pending,key(row))
        assert row['disposition']=='FALSE_POSITIVE_ALL_EXACT_CAPTURES_PUBLIC_DIGESTS'
        path=row['path']
        if path not in line_cache:
            data=(SNAPSHOT/path).read_bytes();assert sha(data)==row['inputSha256'];line_cache[path]=data.decode('utf-8').splitlines(keepends=True)
        low=max(0,row['startLine']-2)
        text=''.join(line_cache[path][low:min(len(line_cache[path]),row['endLine']+1)])
        actual=set()
        for match in re.compile(rules[row['ruleId']]['regex'],re.ASCII).finditer(text):
            begin=low+text.count('\n',0,match.start(1))+1;end=low+text.count('\n',0,match.end(1))+1
            if row['startLine']<=begin<=end<=row['endLine']:actual.add(match.group(1))
        proven=set()
        for proof in row['publicArtifactProofs']:
            identifier=json.dumps(proof,sort_keys=True)
            if identifier not in proof_cache:proof_cache[identifier]=validate_proof(proof,inventory,sites,site_cache)
            proven.add(proof_cache[identifier])
        assert actual==proven and len(actual)==row['exactCaptureCount']>0
    assert len(updates)==manifest['additionalFalsePositives'] and sum(pending.values())==manifest['remainingUnclassified']
    assert updates
    import copy
    golden=updates[0]['publicArtifactProofs'][0];assert golden['proofKind']=='PUBLIC_JAVA_SQLCATCH_TOKEN_DIGEST'
    rejected=[]
    for name,delta in [('wrong-source-hash',{'sourceSha256':'0'*64}),('wrong-token',{'publicTokenDigest':'0'*64}),
                       ('unknown-catch-line',{'catchLine':0}),('wrong-reference',{'normalizationReferenceSha256':'0'*64}),
                       ('extra-secret-field',{'Secret':'DO_NOT_PUBLISH'})]:
        changed=copy.deepcopy(golden);changed.update(delta)
        try:validate_proof(changed,inventory,sites,site_cache)
        except ValueError:rejected.append(name)
        else:raise AssertionError('unproven derived digest accepted')
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
       source=manifest['source'],contentCommit=manifest['contentCommit'],classificationManifestSha256=sha((RAW/'manifest.json').read_bytes()),
       exactReferenceFunctions=['LEX','balanced','sites'],legacyMainOrImportsExecuted=False,
       additionalFalsePositives=len(updates),cumulativeFalsePositiveProof=manifest['cumulativeFalsePositiveProof'],
       remainingUnclassified=manifest['remainingUnclassified'],actualUniquePublicProofs=len(proof_cache),
       rejectedMetadataCases=rejected,originalMultiplicityPreserved=True,scannerRerun=False,
       ancestorWholeHashRerun=False,productTestsExecuted=0,productCoverage=None,
       whole451SecretGateAccepted=False,formalUpdated=False,newAccepted=0)
    with (OUT/'manifest.json').open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({name:value[name] for name in ('actualExit','additionalFalsePositives','cumulativeFalsePositiveProof','remainingUnclassified','actualUniquePublicProofs')}))


if __name__=='__main__':main()
