"""Join explicit declared MON references, never infer implementation or execute Source."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess

def references(text,valid_ids):
    if not isinstance(text,str) or len(text)>4096:raise ValueError('bounded declaration text required')
    grammar=re.compile(r'(?<![A-Za-z0-9_-])MON-?([0-9]{3})((?:(?:\.\.|/)[0-9]{3})*)(?![A-Za-z0-9_-]|\.\.|/(?!MON-?[0-9]))')
    result=[]
    for match in grammar.finditer(text):
        parts=re.split(r'(\.\.|/)',match[1]+match[2]);numbers=[int(parts[0])];problem=None
        for i in range(1,len(parts),2):
            end=int(parts[i+1]);previous=numbers[-1]
            if parts[i]=='/':numbers.append(end)
            elif end<previous or end-previous+1>len(valid_ids):problem='INVALID_OR_OVERSIZED_RANGE';break
            else:numbers.extend(range(previous+1,end+1))
        ids=sorted({'MON-'+f'{n:03d}' for n in numbers})
        if problem is None and not set(ids)<=valid_ids:problem='UNKNOWN_CANONICAL_ID'
        if problem is not None:ids=[]
        result.append(dict(start=match.start(),end=match.end(),token=match[0],ids=ids,problem=problem))
    unknown=[]
    for match in re.finditer(r'(?<![A-Za-z0-9_-])MON-?[0-9](?:(?!/MON-?[0-9])[A-Za-z0-9_./-])*',text):
        token=match[0]
        if token.endswith('.') and not token.endswith('..'):token=token[:-1]
        selected=[v for v in result if v['start']==match.start() and v['token']==token]
        if len(selected)!=1:
            result=[v for v in result if v['start']!=match.start()]
            unknown.append(dict(start=match.start(),token=match[0],problem='UNPARSED_OR_PARTIAL_NUMERIC_MON_TOKEN'))
    all_ids={n for v in result for n in v['ids']}
    return dict(ids=sorted(all_ids),tokens=result,unparsedNumericTokens=unknown)

def main():
    R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/555_monitoring112_declared_rd_scope.json';O=B/'evidence/PG23862-monitoring112-declared-rd-join-v1'
    load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cfg=load(C);assert not O.exists();wp=R/cfg['wbsBefore']['path'];assert sha(wp)==cfg['wbsBefore']['sha256'];wb=load(wp)
    op=R/cfg['observations']['path'];assert sha(op)==cfg['observations']['sha256'];obs={v['path']:v for v in load(op)}
    rd=R/cfg['rd']['path'];assert sha(rd)==cfg['rd']['sha256'] and rd.read_bytes()==subprocess.check_output(['git','show','origin/main:'+cfg['rd']['path']],cwd=R)
    requirements={v['id']:v for v in wb['requirements'] if v['id'].startswith('MON-')};assert len(requirements)==13
    text=rd.read_text();assert all(v in text for v in requirements)
    rows=[]
    for n in cfg['selectedSourcePaths']:
        o=obs[n];ref=references(o['classDoc'] or '',set(requirements))
        status='UNKNOWN_DECLARED_TOKEN' if ref['unparsedNumericTokens'] or any(v['problem'] for v in ref['tokens']) else 'EXACT_DECLARED_REFERENCE_ONLY' if ref['ids'] else 'DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING'
        rows.append(dict(path=n,sourceSha256=o['sourceSha256'],classDeclaration=o['classDoc'],declaredProgramReferences=o['declaredProgramReferences'],declaredDocumentReferences=o['declaredDocumentReferences'],parsed=ref,status=status,canonicalRequirementRows={k:requirements[k] for k in ref['ids']},implementationAccepted=False,ptEvidenceInferred=False,coverageQualified=False,metadataOnly=o['metadataOnly']))
    assert len(rows)==112 and sum(bool(v['parsed']['ids']) for v in rows)==12
    assert sum(len(v['parsed']['ids']) for v in rows)==84 and sum(v['status']=='DOCUMENT_OR_OWNER_CONTEXT_ONLY_PRECISE_RD_MAPPING_PENDING' for v in rows)==100
    assert not any(v['status']=='UNKNOWN_DECLARED_TOKEN' for v in rows)
    reverse={k:[v['path'] for v in rows if k in v['parsed']['ids']] for k in requirements}
    O.mkdir()
    for n,v in [('source-declared-refs.json',rows),('requirement-reverse-refs.json',reverse)]:
        (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    files={n:sha(O/n) for n in ('source-declared-refs.json','requirement-reverse-refs.json')}
    key='currentMonitoring112DeclaredRdReferenceJoin20261108';assert key not in wb
    wb[key]=dict(source=cfg['source'],sourcePrograms=112,withExplicitCanonicalReferences=12,docContextOnlyPreciseMappingPending=100,uniqueSourceRequirementLinks=84,distinctReferencedRequirementIds=9,unknownNumericTokens=0,sourceRef=dict(path=str((O/'source-declared-refs.json').relative_to(R)),sha256=files['source-declared-refs.json']),reverseRef=dict(path=str((O/'requirement-reverse-refs.json').relative_to(R)),sha256=files['requirement-reverse-refs.json']),scope=cfg['scope'],implementedRequirementsInferred=False,newAcceptance=0,newProductTests=0,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
    wp.write_text(json.dumps(wb,ensure_ascii=False,indent=2)+'\n')
    out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],observerHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),config=dict(path=str(C.relative_to(R)),sha256=sha(C)),wbsBefore=cfg['wbsBefore'],wbsAfter=dict(path=str(wp.relative_to(R)),sha256=sha(wp)),overlayKey=key,sourcePrograms=112,explicitReferenceSources=12,sourceRequirementLinks=84,distinctRequirementIds=9,docContextOnlyPreciseMappingPending=100,unknownNumericTokens=0,sourceBodiesReread=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,files=files,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,sources=112,explicitSources=12,links=84,pendingPreciseMapping=100,manifestSha256=sha(O/'manifest.json'))))

if __name__=='__main__':main()
