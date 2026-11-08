"""Exact ledger delimiter/package-kind repair; reusable completion setter validates columns."""
from pathlib import Path
import datetime,hashlib,json,re

def complete_row(row,completed_on):
    if not isinstance(row,str) or '\n' in row or not row.startswith('|') or not row.endswith('|'):
        raise ValueError('one complete Markdown table row required')
    parts=row.split('|')
    if len(parts[1:-1])!=16:raise ValueError('sixteen ledger columns required')
    if not isinstance(completed_on,str) or datetime.date.fromisoformat(completed_on).isoformat()!=completed_on:
        raise ValueError('actual ISO completion date required')
    parts[-3]=' CLOSED ';parts[-2]=' '+completed_on+' '
    return '|'.join(parts)

def repair_date(row):
    parts=row.split('|')
    if len(parts[1:-1])!=15:raise ValueError('expected preserved malformed row required')
    m=re.fullmatch(r'(\s*CLOSED)(\s{2})([0-9]{4}-[0-9]{2}-[0-9]{2})(\s*)',parts[-2])
    if m is None:raise ValueError('exact preserved state/date concatenation required')
    datetime.date.fromisoformat(m[3])
    fixed='|'.join(parts[:-2]+[m[1]+' ',' '+m[3]+m[4],parts[-1]])
    if len(fixed.split('|')[1:-1])!=16:raise ValueError('completion fields must remain separate')
    return fixed

def main():
    R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/565_metadata_schema_scope.json';O=B/'evidence/PG23894-ledger6-package3-schema-correct-v1'
    load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    cfg=load(C);assert not O.exists();lp=R/cfg['ledgerBefore']['path'];wp=R/cfg['wbsBefore']['path'];assert sha(lp)==cfg['ledgerBefore']['sha256'] and sha(wp)==cfg['wbsBefore']['sha256']
    beforeText=lp.read_text();afterText=beforeText;changes=[]
    for ident,row in cfg['dateRowsBefore'].items():
        assert beforeText.splitlines().count(row)==1 and row.startswith('| '+ident+' |');fixed=repair_date(row)
        afterText=afterText.replace(row,fixed,1);changes.append(dict(id=ident,before=row,after=fixed))
    wb=load(wp);byPath={v['path']:v for v in wb['artifacts']};kindChanges=[]
    for old in cfg['kindRowsBefore']:
        n=old['path'];assert byPath[n]==old and old['kind']=='JAVA' and n.endswith('/monitoring/package-info.java')
        byPath[n]['kind']='JAVA_PACKAGE';kindChanges.append(dict(path=n,before=old,after=byPath[n].copy()))
    indexp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(indexp)
    packages=[v for v in wb['artifacts'] if v['path'].endswith('/package-info.java')];assert len(packages)==37
    for v in packages:
        assert v['kind']=='JAVA_PACKAGE';physical=[x for x in index.values() if x['path']==v['path']];assert physical and all(x['hasCode'] is False for x in physical)
    ownRows=[line for line in afterText.splitlines() if re.match(r'\| BUG-(?:2499|250[0-9]) \|',line)]
    assert len(ownRows)==11 and all(len(line.split('|')[1:-1])==16 for line in ownRows)
    assert len(changes)==6 and len(kindChanges)==3
    O.mkdir()
    for n,v in [('ledger-row-changes.json',changes),('package-kind-changes.json',kindChanges)]:
        (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    lp.write_text(afterText);wp.write_text(json.dumps(wb,ensure_ascii=False,indent=2)+'\n')
    out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=cfg['source'],config=dict(path=str(C.relative_to(R)),sha256=sha(C)),ledgerBefore=cfg['ledgerBefore'],wbsBefore=cfg['wbsBefore'],ledgerAfter=dict(path=str(lp.relative_to(R)),sha256=sha(lp)),wbsAfter=dict(path=str(wp.relative_to(R)),sha256=sha(wp)),fixedDateRows=6,fixedKindRows=3,currentTurnLedgerRowsValidated=11,expectedColumns=16,allPackageMetadataRows=37,allPackageMetadataNoCode=True,sourceMutation=False,productTestsExecuted=0,compilerOrJvmExecuted=False,actualBackendActions=0,heldFourInitializations=0,newAcceptance=0,formalUpdated=False,effortRate=None,wholeG13Accepted=False,whole451Accepted=False,files={n:sha(O/n) for n in ('ledger-row-changes.json','package-kind-changes.json')},bugs=['BUG-2508','BUG-2509'],ykts=['YKT-2246','YKT-2247'],tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,dateRows=6,kindRows=3,ledgerRows16Columns=11,packageMetadata37NoCode=True,manifestSha256=sha(O/'manifest.json'))))

if __name__=='__main__':main()
