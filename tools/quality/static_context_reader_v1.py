"""Immutable v1 static context reader: declarative data only, no Product/test/service execution."""
from collections import Counter
import json
from pathlib import PurePosixPath
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_ascii import span
from trace_owner_join import canonical
import snapshot_program_qualified_v2 as cfg

ORIGINAL=('PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
MEASURED=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
NORMAL_SHA='8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65'
HELD={'tools/quality/pg9892_snapshot_key_close_witness.py','tools/quality/architecture/SnapshotKeyCloseWitness.java'}
RULES={'AvoidSynchronizedStatement','AvoidCatchingGenericException'}

def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def require(ok,message):
    if not ok:raise ValueError(message)
def digest(v):return isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) is not None
def public_name(name):
    return (isinstance(name,str) and name not in HELD and len(name)>0 and chr(0) not in name
      and not PurePosixPath(name).is_absolute() and all(v not in ('','..','.') for v in name.split('/')))
def source_name(name):
    return (public_name(name) and re.fullmatch(r'src/schubert-nk-(api|batch|bootstrap|protocol|storage|web)/src/(main|test)/java/[A-Za-z0-9_/$.-]+\.java',name) is not None)
def document_name(name):
    return public_name(name) and re.fullmatch(r'documents/(100_RD|200_UI|300_SS)/[^\n\r]+\.md',name) is not None
def output_name(name):
    return isinstance(name,str) and re.fullmatch(r'PG[1-9][0-9]+-[a-z0-9]+(?:-[a-z0-9]+)*',name) is not None
def validate_plan(plan):
    require(isinstance(plan,dict) and set(plan)=={'out','record','rule','targets','design'},'fixed declarative plan fields only')
    require(output_name(plan['out']) and isinstance(plan['rule'],str) and plan['rule'] in RULES,'new-only public output and supported exact rule')
    record=plan['record'];require(public_name(record) and record.startswith('evidence/01_PT/') and record.endswith('.md'),'public PT specification/result reference')
    require(isinstance(plan['targets'],dict) and 1<=len(plan['targets'])<=64,'bounded explicit source scope')
    ids=[]
    for path,target in plan['targets'].items():
        require(source_name(path) and isinstance(target,dict) and set(target)=={'sha256','owner','ids','reason','guards','ordered','prefixLines','prefixSha256','monitor'},'explicit public Java source target schema')
        require(digest(target['sha256']) and (target['owner'] is None or isinstance(target['owner'],str) and target['owner'].startswith('WBS-')),'source digest and explicit known/unknown owner')
        require(isinstance(target['ids'],list) and target['ids'] and all(isinstance(v,str) and re.fullmatch(r'PMD-[0-9]{5}',v) for v in target['ids']),'original diagnostic IDs only')
        ids.extend(target['ids'])
        require(isinstance(target['reason'],str) and 1<=len(target['reason'].strip())<=3000,'human source/SS reason required')
        require(isinstance(target['guards'],list) and target['guards'] and all(isinstance(v,str) and v for v in target['guards']),'exact reviewed source guards')
        require(isinstance(target['ordered'],list) and all(isinstance(v,list) and len(v)>=2 and all(isinstance(p,str) and p for p in v) for v in target['ordered']),'explicit source order guards')
        n=target['prefixLines'];h=target['prefixSha256']
        require((n is None and h is None) or (type(n) is int and n>=1 and digest(h)),'prefix must be literal positive line count and exact original digest')
        monitor=target['monitor']
        require(monitor is None or isinstance(monitor,str) and re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*',monitor),'explicit simple monitor name or absent')
        require(plan['rule']!='AvoidSynchronizedStatement' or monitor is not None,'synchronized statement requires exact monitor')
    require(len(ids)==len(set(ids)) and len(ids)<=300,'no duplicate ID loss or unbounded scope')
    require(isinstance(plan['design'],dict) and plan['design'] and all(document_name(p) and digest(h) for p,h in plan['design'].items()),'approved RD/UI/SS pins only')
    return set(ids)
def read_known(name,known,reader=None):
    # Validate/exclude before any filesystem metadata, including in the injected tool-only spy.
    require(public_name(name) and name in known and digest(known[name]),'known public input only; no held/traversal/unknown file access')
    if reader is None:
        path=data.ROOT
        for part in name.split('/'):
            path=path/part
            require(not path.is_symlink(),'symlink input is not admitted')
        require(path.is_file(),'regular public input required')
        content=path.read_bytes()
    else:content=reader(name)
    require(isinstance(content,bytes) and data.sha(content)==known[name],'exact current public input digest required')
    return content
def guard_text(target,text):
    require(all(v in text for v in target['guards']),'reviewed source phrase missing')
    for sequence in target['ordered']:
        positions=[text.index(v) for v in sequence]
        require(all(a<b for a,b in zip(positions,positions[1:])),'reviewed source phase order changed')
    n=target['prefixLines']
    if n is not None:
        prefix=''.join(text.splitlines(keepends=True)[:n])
        require(len(prefix.splitlines())==n and data.sha(prefix.encode())==target['prefixSha256'],'original no-escape prefix required')
    else:prefix=text
    return prefix
def bind_rows(plan,catalog,facts,texts,owners):
    ids=validate_plan(plan);result=[]
    index={r['id']:r for r in catalog};require(len(index)==len(catalog),'original catalog IDs must be unique')
    for path,target in plan['targets'].items():
        require(path in texts and path in owners,'explicit text and canonical ownership scope')
        text=texts[path];require(data.sha(text.encode())==target['sha256'],'current source differs')
        prefix=guard_text(target,text)
        owned=owners[path]
        require(isinstance(owned,dict) and set(owned)=={'canonicalOwner','canonicalCostOwner','ownershipStatus','basis'},'canonical owner fields only, never runtime/quality overrides')
        require(owned['canonicalOwner']==owned['canonicalCostOwner']==target['owner'],'baseline owner not inferred from change group')
        old=[index[v] for v in target['ids'] if v in index];require(len(old)==len(target['ids']),'missing original diagnostic')
        counts=Counter(wire(r['attributes']) for r in old);seen=Counter()
        for original in sorted(old,key=lambda r:r['id']):
            attrs=original['attributes'];key=wire(attrs)
            require(attrs.get('beginline')==attrs.get('endline'),'v1 single-line diagnostic token only')
            matched=[r for r in facts if r['path']==path and r['rule']==plan['rule'] and r['attributes']==attrs]
            require(original['path']==path and original['rule']==plan['rule'] and original['inputSha256']==target['sha256'],'original finding/source/rule mismatch')
            require(len(matched)==counts[key] and matched and all(r['sourceSha256']==target['sha256'] for r in matched),'raw occurrence multiplicity retained')
            start,end,token=span(prefix,attrs);require(text[start:end]==token,'original prefix must retain full-source selected position')
            if plan['rule']=='AvoidSynchronizedStatement':
                require(token=='synchronized' and text[end:].startswith(' ('+target['monitor']+')'),'exact synchronized keyword/monitor required')
            else:require(token in {'Exception','RuntimeException','Throwable','Error','NullPointerException'},'review generic catch token before extending supported scope')
            result.append(dict(id=original['id'],path=path,source=cfg.SOURCE,sourceSha256=target['sha256'],rule=plan['rule'],attributes=attrs,originalRowSha256=original['rowSha256'],spanStart=start,spanEndExclusive=end,spanSha256=data.sha(token.encode()),typeToken=token,rawDiagnosticMultiplicity=len(matched),occurrenceOrdinal=seen[key],monitor=target['monitor'],reason=target['reason'],coordinateScope=dict(prefixLines=target['prefixLines'],prefixSha256=target['prefixSha256'],wholeJavaUnicodeTranslationValidated=False),disposition='EXPLICIT_SOURCE_CONTRACT_CURRENT_WHOLE_JOIN_PENDING',rawRetained=True,currentWholeJoinPending=True,sourceChanged=False,productTestsExecuted=0,nativeRuntimeProven=False,qualityGatePass=False,**owned))
            seen[key]+=1
    require(len(result)==len(ids) and {r['id'] for r in result}==ids,'all explicit raw IDs exactly once')
    return sorted(result,key=lambda r:r['id'])
def related_scope(text,hashes):
    result={}
    for imported in re.findall(r'^import (?:static )?(dev\.codex\.schubert\.nk\.[A-Za-z0-9_.]+);$',text,re.M):
        parts=imported.split('.');found=None
        while len(parts)>=6:
            matches=[p for p in hashes if p.endswith('/src/main/java/'+'/'.join(parts)+'.java')]
            if matches:require(len(matches)==1,'unique direct source type');found=matches[0];break
            parts.pop()
        require(found is not None,'unbound NK direct import')
        result[imported]=dict(path=found,sha256=hashes[found],qualification='SOURCE_HASH_ONLY_NOT_WHOLE_REVIEW_OR_EXECUTION')
    return result
def run(plan):
    invocation=capture(__file__);validate_plan(plan)
    out=data.BASE/plan['out'];require(not out.exists() and (data.ROOT/plan['record']).is_file(),'new-only output and saved specification/result record')
    normal,pin=cfg.normal();require(pin==NORMAL_SHA,'fixed normal evidence')
    hashes=normal['begin']['inputHashes']
    for name in hashes:read_known(name,hashes)
    for name,h in plan['design'].items():
        require(data.sha(read_known(name,plan['design']))==h==data.sha(subprocess.check_output(['git','show','origin/main:'+name],cwd=data.ROOT)),'approved design equality')
    measured=data.read_checked(data.BASE/MEASURED[0]/'manifest.json',MEASURED[1]);require(measured['actualExit']==0 and measured['analysisComplete'] and not measured['processingErrors'],'complete original static analysis')
    facts=data.read_checked(data.BASE/MEASURED[0]/'findings.json',measured['findingsSha256'])
    catalog=data.read_checked(data.BASE/ORIGINAL[0],ORIGINAL[1])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    texts={p:read_known(p,hashes).decode() for p in plan['targets']};owners={p:canonical(p,logical) for p in plan['targets']}
    imports={p:related_scope(text,hashes) for p,text in texts.items()}
    for scope in imports.values():
        for item in scope.values():read_known(item['path'],hashes)
    rows=bind_rows(plan,catalog,facts,texts,owners);verify(invocation);out.mkdir()
    data.write(out/'review.json',dict(source=cfg.SOURCE,planSha256=data.sha(wire(plan).encode()),rows=rows,approvedDesignHashes=plan['design'],directNkRelatedSourceScope=imports,importsAreNotRuntimeAllowlist=True))
    data.write(out/'manifest.json',dict(actualExit=0,source=cfg.SOURCE,invocation=invocation,planSha256=data.sha(wire(plan).encode()),reviewSha256=data.sha((out/'review.json').read_bytes()),normalManifestSha256=pin,measurementReference=MEASURED,measurementSource=measured['source'],wholeCurrentStaticMeasurement=False,sourceContexts=len(rows),sourceFiles=len(texts),rawRetained=len(rows),sourceChanged=False,productTestsExecuted=0,coverage=None,nativeQualification=False,qualityGatePass=False,newAccepted=0,formalUpdated=False,effortPercent=None,wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((out/'manifest.json').read_bytes()))
