"""Independent source-name/empty-argument/UTF16 position checks for exact85 AST inventory, no type inference."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import re
import subprocess
R=Path(__file__).resolve().parents[4];P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22502-test-wait85-source-inventory-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22504-test-wait85-source-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
PART=re.compile(r'(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
def mask(text):
    def replace(m):
        value=''.join('\n' if c=='\n' else ' ' for c in m.group());return value if m.group('comment') else 'L'+value[1:]
    return PART.sub(replace,text)
def valid(site,text):
    if site['name'] not in ['get','join'] or site['kind'] not in ['CALL','REF']:return False
    lines=text.splitlines(keepends=True);line=site['line'];column=site['columnUtf16']
    if type(line) is not int or type(column) is not int or not 0<line<=len(lines) or column<1:return False
    try:prefix=lines[line-1].encode('utf-16-le')[:(column-1)*2].decode('utf-16-le')
    except UnicodeError:return False
    at=sum(map(len,lines[:line-1]))+len(prefix);name=site['name']
    if text[at:at+len(name)]!=name:return False
    code=mask(text);tail=code[at+len(name):]
    if site['kind']=='REF':return site['arity'] is None and re.search(r'::\s*(?:<[^<>]*>\s*)?$',code[max(0,at-100):at]) is not None
    if type(site['arity']) is not int or site['arity']<0:return False
    match=re.match(r'\s*\(',tail)
    if not match:return False
    opening=at+len(name)+match.end()-1;depth=1;end=None
    for i in range(opening+1,len(code)):
        if code[i]=='(':depth+=1
        elif code[i]==')':
            depth-=1
            if depth==0:end=i;break
    if end is None:return False
    empty=not code[opening+1:end].strip();return empty==(site['arity']==0)
def main():
    assert not OUT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='ce3214560a0cbed2fba8779833356144c565bf6492c4a8463a80b61609be2cab' and m['actualExit']==0 and m['source']=='3edb9c1322f074ea04109bcc239fa21e66d4d949';allow=R/m['originalAllowlist']['path'];assert sha(allow)==m['originalAllowlist']['sha256'];assert set(m['inputHashes'])==set(load(allow)['begin']['inputHashes']) and len(m['inputHashes'])==85;source={}
    for name,h in m['inputHashes'].items():
        assert '/src/test/java/' in name and not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest();source[name]=(R/name).read_text()
    for path,h in m['files'].items():assert sha(P/path)==h
    for label,stage in m['stages'].items():
        assert stage==load(P/(label+'-exit.safe.json')) and stage['actualExit']==0 and not stage['timedOut']
        for stream in ['stdout','stderr']:assert sha(P/(label+'.'+stream))==stage[stream+'Sha256']
    cmd=m['stages']['parse']['command'];assert cmd[1]=='-cp' and cmd[3]=='TestWaitCandidateAstCheck' and cmd[4]==str(R) and set(cmd[5:])==set(m['inputHashes']);assert not any(x in ':'.join(cmd[:4]) for x in ['schubert-nk-api','schubert-nk-web','junit','postgresql'])
    sites=load(P/'sites.json');assert len(sites)==789 and sum(s['kind']=='CALL' for s in sites)==m['methodInvocationSites']==787 and sum(s['kind']=='REF' for s in sites)==m['methodReferenceSites']==2;assert sum(s['kind']=='CALL' and s['arity']==0 for s in sites)==m['noArgumentInvocationCandidates']==81
    keys=set()
    for s in sites:
        assert s['path'] in source and s['sourceSha256']==m['inputHashes'][s['path']] and s['receiverClassification']=='UNKNOWN_NOT_YET_RESOLVED';assert valid(s,source[s['path']]);key=(s['path'],s['line'],s['columnUtf16'],s['kind']);assert key not in keys;keys.add(key)
    sample=next(s for s in sites if s['kind']=='CALL');negative=[]
    for field,value in [('line',0),('columnUtf16',0),('name','missing'),('kind','OTHER'),('arity',1 if sample['arity']==0 else 0)]:
        bad=copy.deepcopy(sample);bad[field]=value;assert not valid(bad,source[sample['path']]);negative.append(field)
    assert m['allReceiverTypesUnresolved'] and m['noBlockingOrSafeInference'] and not m['waitAuditOrLateralClosureComplete'];OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),checkedSources=85,verifiedSourceNamePositions=789,methodInvocationSites=787,methodReferenceSites=2,independentlyVerifiedZeroArgVsNonzeroCalls=787,nonzeroExactArityNumbersFromParserOnly=True,noArgumentInvocationCandidates=81,allReceiverTypesUnresolved=True,referenceExecutionNotInferred=True,noBlockingOrSafeInference=True,metadataNegativeGuards=negative,sourceBytesUnchanged=True,waitAuditOrLateralClosureComplete=False,bug='BUG-2432',ykt='YKT-2177',yktState='OPEN_RECEIVER_RESOLUTION_AND_DYNAMIC_HOLD',productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sites=789,zeroArgCandidates=81,allReceiverTypes='UNKNOWN',manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
