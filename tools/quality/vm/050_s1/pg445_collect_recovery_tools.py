"""Fixed-source hashes and sanitized recovery operator negative tests, not formal PT."""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
root = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
work = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
target = root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG445-recovery-tools-v2'
assert not target.exists() and (work/'pg445-compile-v2.log').read_bytes()==b''
tests=[]
for name,identifier,count in [('Pg428ColdBootPreparationTest','PG444-COLD-001',414),
                              ('Pg444TransferPreservationTest','PG444-TRANSFER-001',21),
                              ('Pg444ColdOwnershipTest','PG444-OWNERSHIP-001',25),
                              ('Pg445RecoveryDiagnosticsTest','PG445-DIAG001..016',16),
                              ('pair','ROOTPAIR008-TOOL',199)]:
    data=(work/('pg445-'+name+'-v2.log')).read_bytes()
    text=data.decode();assert re.fullmatch(r'[A-Z0-9_]+ .*\n',text)
    assert 'success=true' in text and f'independentAssertions={count}' in text and 'productionTestCount=0' in text
    tests.append({'testId':identifier,'exitCode':0,'assertions':count,'actual':text.strip(),'logSha256':hashlib.sha256(data).hexdigest()})
assert sum(t['assertions'] for t in tests)==675
before=(work/'pg445-pair-before.log').read_bytes()
assert b'NullPointerException' in before and b'Pg431KnownPairRecovery.known' in before
names=['Pg428ColdBootPreparation.java','Pg428ColdBootPreparationTest.java','Pg431KnownPairRecovery.java',
       'Pg431KnownPairRecoveryTest.java','Pg444TransferPreservationTest.java','Pg444ColdOwnershipTest.java','Pg445RecoveryDiagnosticsTest.java']
record={'id':'PG445-recovery-tools-v2','formal':False,'nativeAccepted':False,
        'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'sourceDirty':True,'branch':'dev-foundation','timeUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'environment':'Linux/JDK25.0.4; javac -Xlint:all -Werror; fixed PG443 source2b418 runtime classes',
        'runtimeProductionSource':'2b41817ca98f4cbd40171ffa459743e5e943fc45','command':'WorkPG379/pg445_tools_v2.sh',
        'exitCode':0,'compileWarnings':0,'operatorAssertions':675,'productionTestCount':0,'tests':tests,
        'sourceFiles':[{'path':'tools/quality/vm/050_s1/'+n,'sha256':hashlib.sha256((root/'tools/quality/vm/050_s1'/n).read_bytes()).hexdigest()} for n in names],
        'classes':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((work/'pg445-tools-v2').glob('*.class'))],
        'before':{'bug':'BUG-599','exitCode':1,'sha256':hashlib.sha256(before).hexdigest(),'npeCaughtAsNormal':False},
        'independentOracle':'literal fixed redacted topology, primary/cause/secondary exact order/type, literal no-message/unknown/16node bounds, all18/receipt null/raw/snapshot divergence plus public Transfer/SHA/inode fixtures',
        'bugs':['BUG-544','BUG-599'],'ykt':['YKT-388','YKT-423'],'ssc':['SSC-174'],'qa':['QA-047'],
        'limits':['new diagnostic source has not been run as native recovery','old boot intents not reconstructed/retired and old close remains UNKNOWN','previous PG444 native applies only fcc cold source; no success reuse to this modified tool','Production source unchanged; formal1964PT53scope/wholePGPT/ITST not accepted'],
        'redaction':'no messages/raw epoch/credential/private watch/DB/backup; public stdout and source/class hashes only'}
assert not re.search(r'(?i)(authorization|cookie|password|session_id|access_token)\s*[:=]\s*["\']?[^\s<>]',json.dumps(record))
target.mkdir(parents=True)
path=target/'manifest.json';path.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'success':True,'operatorAssertions':675,'formal':False,'manifestSha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
