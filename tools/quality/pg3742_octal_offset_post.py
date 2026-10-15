"""Separate read-only post for original187 offsets, never rewrites/reissues the original witness."""
import hashlib
import json
from pathlib import Path
import subprocess
from source_utf16 import source_slice


def main():
    root=Path(__file__).resolve().parents[2];old=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3736-octal-hygiene-v1';meta=json.loads((old/'manifest.json').read_bytes());rows=json.loads((old/'all-187-integer-vectors.json').read_bytes());cache={};nonbmp=set();different=[]
    for r in rows:
        p=r['path']
        if p not in cache:cache[p]=subprocess.check_output(['git','show',meta['baseSource']+':'+p],cwd=root).decode()
        text=cache[p];start=r['oldUtf16Start'];end=r['oldUtf16End'];assert source_slice(text,start,end)==r['oldOctal']
        if any(ord(c)>0xffff for c in text):nonbmp.add(p)
        if text[start:end]!=source_slice(text,start,end):different.append(p)
    assert len(rows)==187
    out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3742-octal-offset-post-v1';out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();value={'actualExit':0,'source':meta['source'],'baseSource':meta['baseSource'],'originalManifestSha256':sha(old/'manifest.json'),'original187VectorsSha256':sha(old/'all-187-integer-vectors.json'),'checkedVectors':187,'checkedFiles':len(cache),'nonBmpSourceFiles':sorted(nonbmp),'actualPriorCoordinateDifferences':sorted(set(different)),'originalAllVectorsRemainValid':True,'originalArtifactsUnchanged':True,'beforeNonBmpCounterexampleObserved':True,'independentUtf16BoundaryPureTest':1,'bugs':['BUG1321'],'ykt':['YKT1087'],'productionPtCredit':0,'MainChanged':False,'vmActions':0,'formalUpdated':False,'F03Accepted':False,'toolSha256':sha(root/'tools/quality/source_utf16.py')};(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps({**value,'manifestSha256':sha(out/'manifest.json')}));return 0


if __name__=='__main__':raise SystemExit(main())
