"""Sanitized source-only witness for actual private190 proof, static result and exact Main apply."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
from lan_server import run
from source_utf16 import source_slice

ROOT=Path(__file__).resolve().parents[2];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proof=json.loads((W/'pg3720-private-field-candidate-v2/manifest.safe.json').read_bytes());fixed=json.loads((W/'pg3722-private-candidate-static-v1/manifest.safe.json').read_bytes());applied=json.loads((W/'pg3724-private-candidate-material-v1/apply.safe.json').read_bytes());stage=json.loads((W/'pg3724-private-candidate-material-v1/stage.safe.json').read_bytes());r=proof['result'];s=fixed['result'];assert proof['actualExit']==fixed['actualExit']==applied['actualExit']==0
    source=subprocess.check_output(['git','log','-1','--format=%H','--',':(glob)src/*/src/main/**'],cwd=ROOT,text=True).strip();files=s['privateRenameDelta']['allSourceSha256'];assert len(files)==849 and {p:sha(ROOT/p)for p in files}==files and len(r['changes'])==90 and s['privateRenameDelta']['actualRawReduction']==190 and s['checkstyle']['findings']==0
    payload='''from pathlib import Path
import json,hashlib
b=Path('/home/mini/schubert-nk-pgpt/runs/PG3720-private-field-candidate-v2');assert hashlib.sha256((b/'manifest.safe.json').read_bytes()).hexdigest()==EXPECTED
rows=[]
for p in sorted((b/'candidate').glob('src/*/src/main/java/.private-field-map.tsv')):
 for line in p.read_text().splitlines():
  file,owner,old,new,position=line.split('\\t');rows.append({'sourceModule':p.parts[-5],'relativeJavaFile':file,'owner':owner,'oldPrivateField':old,'newPrivateField':new,'oldUtf16Position':int(position)})
assert len(rows)==190
print(json.dumps(rows))
'''
    rc,text=run('python3 -c '+shlex.quote('EXPECTED='+repr(r['serverManifestSha256'])+'\n'+payload),timeout=30);assert rc==0
    rows=json.loads(next(x for x in text.splitlines()if x.startswith('[')));assert len(rows)==190
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3728-private-field-hygiene-v1';out.mkdir()
    values={'private-field-map.json':rows,'all-main-source-sha256.json':files,'exact-90-changes.json':r['changes'],'all-six-compiler-proofs.json':r['modules'],'fixed-static.json':{k:s[k]for k in ['pmd','checkstyle','ruleSha256','pinnedToolSha256','auxMeaning','wholeTypedBindingEquivalenceRef']}}
    for name,v in values.items():(out/name).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    value={'programId':'NK-OPS-001/F03','testIds':['PT-3714-001','PT-3714-002','PT-3714-003'],'source':source,'baseSource':proof['baseCandidateSource'],'branch':'dev-foundation','candidateOperator':proof['operatorHead'],'staticOperator':fixed['operatorHead'],'actualExit':0,'sourceFiles':849,'changedMainFiles':90,'renamedPrivateFields':190,'serializedHeld':63,'startUTC':r['startUTC'],'endUTC':s['endUTC'],'os':'Linux dedicated aru host','jdk':'25.0.4','toolchain':'pinned public JDK Compiler API, google-java-format1.36.1, PMD7.28.0 and Checkstyle14.3.0','independentOracle':'literal expected source; constructor/field/method shadow, array/null, type/capture bounds and alias golden; mutation/no-op/serialized/canonical-output canaries; complete normalized tree/literal/type/public ABI and positive new-field set for all6 modules','counts':{'pmdBefore':2217,'pmdAfter':2027,'exactNamingReduction':190,'otherRulesUnchanged':True,'checkstyleAfter':0},'originalRejected':{'PG3714ActualExit':1,'BUG1319':'task-local capture number only; original remains failed'},'candidateManifestSha256':r['serverManifestSha256'],'staticManifestSha256':s['serverManifestSha256'],'exactApplyManifestSha256':sha(W/'pg3724-private-candidate-material-v1/apply.safe.json'),'exactStageManifestSha256':sha(W/'pg3724-private-candidate-material-v1/stage.safe.json'),'bugs':['BUG1317','BUG1318','BUG1319'],'ykt':['YKT1083','YKT1084','YKT1085'],'mainApplied':True,'runtimeDeployed':False,'newWholeAndNativePending':True,'coverage100':False,'F03Accepted':False,'formalAccepted':False,'newProductionPtCredit':0,'acceptedWbsDelta':0,'vmActions':0,'files':{n:sha(out/n)for n in values}}
    (out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps({'actualExit':0,'publicFiles':len(values)+1,'source':source,'manifestSha256':sha(out/'manifest.json'),'rawPMD':2027,'newWholeAndNativePending':True}));return 0


def publish_octal():
    proof=json.loads((W/'pg3726-octal-candidate-v1/manifest.safe.json').read_bytes());fixed=json.loads((W/'pg3730-octal-candidate-static-v1/manifest.safe.json').read_bytes());applied=json.loads((W/'pg3732-octal-candidate-material-v1/apply.safe.json').read_bytes());r=proof['result'];s=fixed['result'];assert proof['actualExit']==fixed['actualExit']==applied['actualExit']==0
    source=subprocess.check_output(['git','log','-1','--format=%H','--',':(glob)src/*/src/main/**'],cwd=ROOT,text=True).strip();files=s['octalDelta']['allSourceSha256'];assert len(files)==849 and {p:sha(ROOT/p)for p in files}==files and len(r['changes'])==30 and s['octalDelta']['actualRawReduction']==187 and s['octalDelta']['onlyOctalRuleChanged']and s['checkstyle']['findings']==0
    payload='''from pathlib import Path
import hashlib,json
b=Path('/home/mini/schubert-nk-pgpt/runs/PG3726-octal-candidate-v1');assert hashlib.sha256((b/'literals.safe.tsv').read_bytes()).hexdigest()==EXPECTED
print(json.dumps((b/'literals.safe.tsv').read_text().splitlines()))
'''
    rc,text=run('python3 -c '+shlex.quote('EXPECTED='+repr(r['tokenReportSha256'])+'\n'+payload),timeout=30);assert rc==0
    lines=json.loads(next(x for x in text.splitlines()if x.startswith('[')));assert lines[-1]=='OCTAL\t187';rows=[]
    for line in lines[:-1]:
        kind,path,start,end,old,new,width,value=line.split('\t');assert kind=='LITERAL'and width in {'INT','LONG'}
        bits=64 if width=='LONG'else 32;number=int(old.lower().removesuffix('l').replace('_',''),8);explicit=int(new.lower().removesuffix('l'),16);signed=number if number<2**(bits-1)else number-2**bits
        assert number==explicit and 0<=number<2**bits and signed==int(value)
        original=subprocess.check_output(['git','show',r['baseCandidateSource']+':'+path],cwd=ROOT).decode();assert source_slice(original,int(start),int(end))==old
        rows.append({'path':path,'oldUtf16Start':int(start),'oldUtf16End':int(end),'oldOctal':old,'explicitHex':new,'javaType':width,'signedValue':signed,'independentBase8HexValueAgrees':True})
    assert len(rows)==187
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3736-octal-hygiene-v1';out.mkdir();values={'all-187-integer-vectors.json':rows,'all-main-source-sha256.json':files,'exact-30-changes.json':r['changes'],'all-six-compiler-proofs.json':r['modules'],'fixed-static.json':{k:s[k]for k in ['pmd','checkstyle','ruleSha256','pinnedToolSha256','auxMeaning','wholeTypedBindingEquivalenceRef']}}
    for name,v in values.items():(out/name).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    value={'programId':'NK-OPS-001/F03','testIds':['PT-OCTAL-001','PT-OCTAL-002','PT-OCTAL-003'],'source':source,'baseSource':r['baseCandidateSource'],'branch':'dev-foundation','candidateOperator':proof['operatorHead'],'staticOperator':fixed['operatorHead'],'actualExit':0,'sourceFiles':849,'changedMainFiles':30,'octalTokens':187,'startUTC':r['startUTC'],'endUTC':s['endUTC'],'os':'Linux aru host','jdk':'25.0.4','toolchain':'fixed public JDK Compiler API, GJF1.36.1, PMD7.28.0, Checkstyle14.3.0','independentOracle':'literal expected source and values; mutation/type/binding/alias/invalid syntax negatives; Java AST values versus BigInteger base8/width, separate Python base8/hex/signed arithmetic over all187 original Git tokens; all6 normalized complete typed tree/literal/public ABI with no renaming','counts':{'pmdBefore':2027,'pmdAfter':1840,'onlyOctalReduction':187,'otherRuleCountsUnchanged':True,'checkstyleAfter':0},'candidateManifestSha256':r['serverManifestSha256'],'staticManifestSha256':s['serverManifestSha256'],'applyManifestSha256':sha(W/'pg3732-octal-candidate-material-v1/apply.safe.json'),'bugs':['BUG1320'],'ykt':['YKT1086'],'newWholeAndNativePending':True,'mainApplied':True,'runtimeDeployed':False,'F03Accepted':False,'formalAccepted':False,'coverage100':False,'newProductionPtCredit':0,'acceptedWbsDelta':0,'vmActions':0,'files':{n:sha(out/n)for n in values}}
    (out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps({'actualExit':0,'source':source,'publicFiles':len(values)+1,'manifestSha256':sha(out/'manifest.json'),'rawPMD':1840}));return 0


if __name__=='__main__':
    import sys
    if sys.argv[1:]not in [[],['--octal187']]:raise ValueError('only original190 or octal187 actual scope')
    raise SystemExit(publish_octal()if sys.argv[1:]else main())
