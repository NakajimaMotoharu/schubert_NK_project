"""Bounded source-as-data profile assessment; no operator behaviour or type guessed."""
from pathlib import Path
import datetime
import hashlib
import json
import re
R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001/evidence'
OUT=B/'PG22338-g07-two-header-scope-assessment-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not OUT.exists();origin=B/'provisional/PG9888-g07-capture-shape-v1';m=json.loads((origin/'manifest.json').read_bytes());assert sha(origin/'residual-metadata-shapes.json')==m['residualMetadataSha256'];rows=json.loads((origin/'residual-metadata-shapes.json').read_bytes());name='tools/quality/vm/050_s1/NativeStreamInspect531.java';selected=[v for v in rows if v['path']==name and v['startLine']==v['endLine'] and v['startLine'] in [13,15]];assert len(selected)==2 and len({v['inputSha256'] for v in selected})==1 and sha(R/name)==selected[0]['inputSha256'];text=(R/name).read_text();rx=re.compile(json.loads((B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json').read_bytes())['rules']['generic-api-key']['regex'],re.ASCII);assessments=[]
    for row in selected:
        line=row['startLine'];raw=text.splitlines()[line-1];matches=[v for v in rx.finditer(text) if text.count('\n',0,v.start(1))+1==line==text.count('\n',0,v.end(1))+1];assert len(matches)==1;is_import=bool(re.fullmatch(r'\s*import (?:static )?[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+;\s*',raw));assert not is_import
        assessments.append(dict(**{k:row[k] for k in ['path','ruleId','startLine','endLine','inputSha256']},exactCaptures=1,javaImport=False,status='UNCLASSIFIED_NO_TYPE_PROVENANCE_IN_ALLOWED_PROFILE',operatorLogicInvestigated=False))
    OUT.mkdir();(OUT/'assessment.json').write_text(json.dumps(assessments,indent=2)+'\n');(OUT/'manifest.json').write_text(json.dumps(dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),assessedRows=2,sourceHash=sha(R/name),assessmentSha256=sha(OUT/'assessment.json'),newFalsePositives=0,remainingUnclassified=4482,productTestsExecuted=0,scannerExecuted=False,targetsExecuted=False,operatorLogicInvestigated=False,readSetFurtherExpanded=False,privateRawRead=False,valuesOrValueHashesWritten=False,newAccepted=0,currentWholeG07Qualified=False,effortRate=None,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__)))),indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=0,retained=2,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
