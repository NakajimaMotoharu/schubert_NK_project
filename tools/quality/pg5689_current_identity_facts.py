"""Current849 typed self-suppression guard facts; never broad equality exemption."""
import datetime
import hashlib
import json
import os
import subprocess
from source_suppression_identity_inventory_test import facts
from pg5592_current_failure_facts import inputs,JDK,ROOT,W,SOURCE

SLOT='pg5689-current-identity-facts-v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    mirror,classpath,identity=inputs();tool=ROOT/'tools/quality/SourceSuppressionIdentityInventory.java';tool_sha=sha(tool.read_bytes())
    fixture=ROOT/'tools/quality/source_suppression_identity_inventory_test.py';fixture_sha=sha(fixture.read_bytes())
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'toolclasses';classes.mkdir()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    phases=[['python3','-B','-m','unittest','source_suppression_identity_inventory_test'],
      [str(JDK/'javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(tool)]]
    for i,command in enumerate(phases):
        with(out/('phase-'+str(i)+'.private.log')).open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=60)
        if r.returncode:raise ValueError('independent identity/JDK fixture and typed helper lint0 first')
    command=[str(JDK/'java'),'-Xmx1536m','-cp',str(classes),'SourceSuppressionIdentityInventory',str(mirror),classpath]
    r=subprocess.run(command,capture_output=True,text=True,timeout=180)
    with(out/'typed.private.log').open('x')as f:f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
    if r.returncode:raise ValueError('all current source/type resolution; preserve original failed result')
    rows=facts(r.stdout)
    if any(row['path']not in identity['sourceHashes']for row in rows):raise ValueError('only current source files')
    if inputs()!=(mirror,classpath,identity)or sha(tool.read_bytes())!=tool_sha or sha(fixture.read_bytes())!=fixture_sha:raise ValueError('all typed inputs fixed before and after')
    value={'actualExit':0,'source':SOURCE,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'identity':identity,'helperSha256':tool_sha,'fixtureSha256':fixture_sha,'independentJdkFixtureExit':0,'compileExit':0,
      'rows':rows,'command':command,'outputSha256':sha(r.stdout.encode()),'F03Accepted':False,'formalAccepted':False,
      'productionChanges':0,'vmActions':0,'dispositions':'FACTS_ONLY_PENDING_INDIVIDUAL_CURRENT_DIAGNOSTIC_BINDING'}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'typedGuardSites':len(rows),'sha256':sha((out/'manifest.safe.json').read_bytes()),'F03Accepted':False}))


if __name__=='__main__':main()
