"""Rebind stable SQL identities by exact catch tokens, not shifted file coordinates."""
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6542_jdbc_catch_inventory import LEX,balanced,sites
from pg6638_current115_receivers import INVENTORY_SHA,review
from pg6670_original4170_artifacts import read_whole

RELOCATED='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java'


def exact_catches(text):
    tokens=[(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    result=[]
    for at,(word,_) in enumerate(tokens):
        if word!='catch':continue
        end=balanced(tokens,at+1,'(',')')
        if 'SQLException' not in [t for t,_ in tokens[at+2:end]]:continue
        last=balanced(tokens,end+1,'{','}')
        result.append(tuple(t for t,_ in tokens[at:last+1]))
    return result


def rebound(priors,old_text,current_text,path):
    old=sites(old_text);now=sites(current_text)
    if len(priors)!=len(old) or len(old)!=len(now) or exact_catches(old_text)!=exact_catches(current_text):
        raise ValueError('all original SQL catch tokens including literals remain exact')
    if old_text!=current_text and path!=RELOCATED:raise ValueError('only explicitly reviewed local producer relocation')
    result=[]
    for prior,before,current in zip(priors,old,now,strict=True):
        if any(prior[k]!=v for k,v in before.items()):raise ValueError('original115 immutable identity')
        if any(before[k]!=v for k,v in current.items() if k!='beginLine'):raise ValueError('exact catch variable/type/body/category identity')
        result.append(dict(prior,**current,originalBeginLine=before['beginLine'],originalSourceSha256=prior['sourceSha256']))
    return result


def main():
    qp,q,cases=read_whole();path=BASE/'PG6624-jdbc-current115-v1/manifest.json'
    if sha(path)!=INVENTORY_SHA:raise ValueError('immutable115 inventory first')
    old=json.loads(path.read_bytes());groups=defaultdict(list)
    for row in old['rows']:groups[row['sourcePath']].append(row)
    current_paths={p for p in q['allSourceHashes'] if p.split('/')[1] in ('schubert-nk-api','schubert-nk-web') and sites((ROOT/p).read_text())}
    if current_paths!=set(groups):raise ValueError('no new SQL catch scope inferred away')
    coverage={m:ET.parse(qp.parent/'coverage'/m/'site/jacoco/jacoco.xml').getroot() for m in ('api','web')}
    for m in coverage:
        if sha(qp.parent/'coverage'/m/'site/jacoco/jacoco.xml')!=q['modules'][m]['coverageXmlSha256']:raise ValueError('genuine original coverage XML')
    rows=[];relocated=[]
    for name,priors in sorted(groups.items()):
        priors.sort(key=lambda r:r['beginLine']);text=(ROOT/name).read_text()
        old_text=subprocess.check_output(['git','show',old['source']+':'+name],cwd=ROOT,text=True)
        import hashlib
        if any(hashlib.sha256(old_text.encode()).hexdigest()!=r['sourceSha256'] for r in priors):raise ValueError('immutable original catch source blob')
        rebased=rebound(priors,old_text,text,name)
        if old_text!=text:relocated.append(name)
        for current in rebased:
            decision=review(current,text);module=name.split('/')[1].removeprefix('schubert-nk-')
            package,file=name.split('/src/main/java/')[1].rsplit('/',1)
            sourcefile=coverage[module].find("package[@name='"+package+"']/sourcefile[@name='"+file+"']")
            if sourcefile is None:raise ValueError('original sourcefile coverage required')
            line=decision['guardLine'];node=sourcefile.find("line[@nr='"+str(line)+"']") if line else None
            cls=package.replace('/','.')+'.'+file.removesuffix('.java')+'Test'
            direct=[{k:c[k] for k in ('testId','class','caseNameSha256','xmlSha256','source')} for c in cases if c['class']==cls]
            rows.append(dict(siteId=current['siteId'],sourcePath=name,sourceSha256=sha(ROOT/name),
                catchLine=current['beginLine'],catchVariable=current['catchVariable'],bodyTokenSha256=current['bodyTokenSha256'],
                originalCatchLine=current['originalBeginLine'],originalSourceSha256=current['originalSourceSha256'],
                identityMapping='EXACT_ORDERED_CATCH_HEADER_BODY_TOKENS_WITH_LITERAL_VALUES',
                originalInventorySha256=INVENTORY_SHA,currentWholeQualificationSha256=sha(qp),
                directClassRegressionRefs=direct,refScope='RELATED_REGRESSION_NOT_PER_SITE_FAULT_CAUSALITY',
                aggregateGuardLineCounter={k:int(node.get(k)) for k in ('ci','mi','cb','mb')} if node is not None else None,**decision))
    if len(rows)!=115 or Counter(r['role'] for r in rows)['DIRECT_GUARD_BEFORE_MAPPING']!=56 or relocated!=[RELOCATED]:
        raise ValueError('all115 explicit scopes/56direct/one actual reviewed file relocation')
    out=BASE/'PG6672-current115-receivers-v1';os.umask(0o077);out.mkdir()
    value=dict(actualExit=0,source=q['productionSource'],sites=115,pgReviewedRoutes=115,
        roles=dict(Counter(r['role'] for r in rows)),rows=rows,relocatedSourcePaths=relocated,acceptedSites=0,
        currentWholeTests=4170,currentWholeQualificationSha256=sha(qp),testsExecuted=0,
        sqlScopeOnly=True,nonSqlScopeNotExhaustive=True,formalAccepted=False,ptAlternativeCompleted=0,vmActions=0)
    target=out/'manifest.json'
    with target.open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,sites=115,manifestSha256=sha(target))))


if __name__=='__main__':main()
