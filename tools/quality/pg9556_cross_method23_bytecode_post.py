"""Independent javap method/JUnit annotation proof; no target loading, HTTP, JDBC or JUnit run."""
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9556-cross-method23-bytecode-post-v1'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9556-cross-method23-bytecode-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
PATHS={'API':'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/BorrowedJdbcFatal329Test.java',
 'WEB':'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/TargetBusinessControllerTest.java'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('exact method/TestID/requirement and actual Main responsibility roles required')

def method_annotations(text):
    lines=text.splitlines();starts=[]
    for i,line in enumerate(lines):
        if re.fullmatch(r'  .+\([^;]*\)(?: throws [^;]+)?;',line):starts.append(i)
    observed={}
    for index,start in enumerate(starts):
        block='\n'.join(lines[start:starts[index+1] if index+1<len(starts) else len(lines)])
        if not re.search(r'(?m)^        org\.junit\.jupiter\.api\.Test$',block):continue
        name=lines[start].split('(',1)[0].rsplit(' ',1)[-1]
        assert name not in observed and re.search(r'(?m)^    descriptor: \(\)V$',block)
        line_numbers=[int(x) for x in re.findall(r'(?m)^        line (\d+): \d+$',block)]
        assert line_numbers;observed[name]=dict(lineNumbers=line_numbers,methodMetadataSha256=sha(block.encode()))
    return observed

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    spec=(ROOT/'evidence/01_PT/018_NK-OPS-001/1936_G13CrossMethod23_TestID・責任対応仕様.md').read_bytes()
    assert sha(spec)=='c87fe5eb73645d2f8a0055ffc8d7cc65bf8d0ceff68b61d8552ba85a94209aef'
    oracle={}
    for line in spec.decode().splitlines():
        if not line.startswith(('|API|','|WEB|')):continue
        _,alias,name,ids,business,mains,note,_=line.split('|');key=(PATHS[alias],name);assert key not in oracle
        oracle[key]=dict(existingTestFamilies=ids.split(','),businessContractWbs=business.split(','),
          reviewedMainSubjects=dict(v.split(':') for v in mains.split(',')),independentOracleReference=note,
          oracleDocument='evidence/01_PT/018_NK-OPS-001/1431_SSC329_green23原資格・借用repository仕様.md' if alias=='API' else 'evidence/01_PT/016_NK-WEB-002/083_NK-WEB-002_通知取消・質問削除単体テスト仕様書.md')
    assert len(oracle)==23
    subject=BASE/'PG9554-cross-method23-source-ast-v1';sr=(subject/'manifest.json').read_bytes()
    assert sha(sr)=='1894885ded2b7d5bab5fc3ee741a8ea2bb0b1bc49665b5417c62158c01224f78'
    primary=json.loads(sr);assert primary['source']==SOURCE and primary['actualExit']==0 and primary['syntaxVectors']==7
    trace_raw=(subject/'method-trace.json').read_bytes()
    assert sha(trace_raw)==primary['methodTraceSha256']=='5b4c58d10f86a2c0857f4a2575328e53c62d165ad7f6f8cae149af2df7d2a824'
    rows=json.loads(trace_raw);assert len(rows)==23 and {(r['path'],r['method']) for r in rows}==set(oracle)
    gd=BASE/'PG9386-composite-reference-graph-v3';gr=(gd/'manifest.json').read_bytes()
    assert sha(gr)=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15';graph=json.loads(gr)
    cl=(gd/'test-class-metadata.json').read_bytes();mm=(gd/'main-class-sources.json').read_bytes()
    assert sha(cl)==graph['testMetadataSha256'] and sha(mm)==graph['mainMapSha256']
    classes=json.loads(cl);mains=json.loads(mm);dirs={Path(p).parent.parent.name.removeprefix('schubert-nk-'):Path(p) for p in graph['treePins']}
    nr=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes()
    assert sha(nr)==primary['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(nr)['begin']['inputHashes']
    logical={r['path']:r for r in json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    os.umask(0o077);SLOT.mkdir();receipts=[];byte_methods={};main_proofs={}
    for path in PATHS.values():
        assert sha((ROOT/path).read_bytes())==hashes[path]==primary['inputHashes'][path]
        matched=[c for c in classes if c['path']==path and c['className'].endswith('/'+Path(path).stem)]
        assert len(matched)==1;c=matched[0];directory=dirs[c['module']]
        assert sha((directory/c['entry']).read_bytes())==c['sha256']
        argv=[str(ROOT.parent/'toolchain/jdk-25.0.4/bin/javap'),'-v','-p','-classpath',str(directory),c['className'].replace('/','.')]
        start=dt.datetime.now(dt.timezone.utc).isoformat()
        child=subprocess.Popen(argv,cwd=SLOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        with (SLOT/(c['module']+'-process.safe.json')).open('x') as f:json.dump(dict(pid=child.pid,ownerPid=os.getpid(),command=argv,startUTC=start),f,sort_keys=True,indent=2);f.write('\n')
        timed_out=False
        try:stdout,stderr=child.communicate(timeout=120)
        except subprocess.TimeoutExpired:timed_out=True;child.kill();stdout,stderr=child.communicate(timeout=15)
        receipt=dict(command=argv,startUTC=start,endUTC=dt.datetime.now(dt.timezone.utc).isoformat(),actualExit=child.returncode,timedOut=timed_out,
          stdoutSha256=sha(stdout),stderrSha256=sha(stderr),rawOutputPersisted=False)
        receipts.append(receipt)
        with (SLOT/(c['module']+'-exit.safe.json')).open('x') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n')
        assert child.returncode==0 and not timed_out and not stderr
        text=stdout.decode();assert re.findall(r'(?m)^SourceFile: "([^"]+)"$',text)==[Path(path).name]
        parsed=method_annotations(text);assert set(parsed)=={name for p,name in oracle if p==path}
        source_lines=(ROOT/path).read_text().splitlines()
        for name,proof in parsed.items():
            candidates=[i+1 for i,line in enumerate(source_lines) if re.match(r'  void '+re.escape(name)+r'\(\)',line)]
            assert len(candidates)==1 and source_lines[candidates[0]-2].strip()=='@Test'
            ast=next(r for r in rows if r['path']==path and r['method']==name)
            assert ast['startLine']==candidates[0]-1 and candidates[0]<=ast['endLine']<=len(source_lines)
            assert all(ast['startLine']<=line<=ast['endLine'] for line in proof['lineNumbers'])
            byte_methods[path+'#'+name+'()']=dict(className=c['className'],classSha256=c['sha256'],declarationLine=candidates[0],**proof)
    expected=[]
    for row in rows:
        path=row['path'];name=row['method'];literal=oracle[(path,name)];proof=byte_methods[path+'#'+name+'()']
        assert row['className']==proof['className'].replace('/','.') and row['parameterCount']==0
        for subject_name,owner in literal['reviewedMainSubjects'].items():
            matches=[v for k,v in mains.items() if k.rsplit('/',1)[-1]==subject_name]
            assert len(matches)==1;main=matches[0];mp=main['path']
            assert main['owner']==logical[mp]['owner']==logical[mp]['costOwner']==owner
            assert sha((ROOT/mp).read_bytes())==hashes[mp]
            main_proofs[mp]=dict(owner=owner,sourceSha256=hashes[mp],classMetadataSha256=main['sha256'])
        expected.append(dict(path=path,sourceSha256=hashes[path],methodKey=path+'#'+name+'()',className=proof['className'].replace('/','.'),
          method=name,parameterCount=0,startLine=proof['declarationLine']-1,endLine=row['endLine'],**literal))
    validate(rows,expected);rejected=[]
    for label,edit in (('family-forged',lambda v:v[0].update(existingTestFamilies=['FORGED'])),
      ('business-owner-forged',lambda v:v[0].update(businessContractWbs=['WBS-G13.07'])),
      ('main-owner-forged',lambda v:v[0].update(reviewedMainSubjects={'UserQueryRepository':'WBS-G13.07'})),
      ('method-forged',lambda v:v[0].update(method='forged')),
      ('declaration-line-forged',lambda v:v[0].update(startLine=0)),
      ('source-byte-forged',lambda v:v[0].update(sourceSha256='0'*64)),
      ('wrong-class',lambda v:v[0].update(className='p.Foreign')),
      ('execution-invented',lambda v:v[0].update(executed=True)),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed);assert changed!=rows
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged method trace accepted')
    verify(invocation);OUT.mkdir()
    for name,value in [('method-bytecode-proofs.json',byte_methods),('main-owner-proofs.json',main_proofs)]:
        with (OUT/name).open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=sha(sr),specSha256=sha(spec),methodTraceSha256=sha(trace_raw),sourceFiles=2,methodDeclarations=23,
      existingDistinctTestFamilies=26,methodCaseFamilyRelations=34,independentMainSubjects=len(main_proofs),receipts=receipts,
      methodBytecodeProofsSha256=sha((OUT/'method-bytecode-proofs.json').read_bytes()),mainOwnerProofsSha256=sha((OUT/'main-owner-proofs.json').read_bytes()),
      sourcePositionScope='DECLARATION_START_FROM_CURRENT_TEXT_AND_BYTECODE_LINE_TABLE_WITHIN_AST_END_NOT_SECOND_EXACT_END_AST',
      calleeResolutionOrFullOracleQualification=False,metadataCounterexamples=rejected,productTestsExecuted=0,newTestIds=0,coverage=None,
      newAccepted=0,formalUpdated=False,filePrimaryOwnersReassigned=False)
    with (OUT/'manifest.json').open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(dict(actualExit=0,methods=23,mainSubjects=len(main_proofs),metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
