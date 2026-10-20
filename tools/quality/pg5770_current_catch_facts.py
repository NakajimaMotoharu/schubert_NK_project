"""Existing catch fact parser on current immutable849; no Production/runtime execution."""
import datetime
import json
import os
import shutil
import subprocess
from pg5766_reference_identity_facts import inputs,SOURCE,ROOT,W,TC,sha
from source_catch_context_inventory_test import facts

SLOT='pg5770-current-catch-facts-v1'


def main():
    snapshot,classpath,identity=inputs();helper=ROOT/'tools/quality/SourceCatchContextInventory.java';fixture=ROOT/'tools/quality/source_catch_context_inventory_test.py';helper_sha=sha(helper);fixture_sha=sha(fixture)
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);classes=out/'toolclasses';classes.mkdir()
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for i,command in enumerate((['python3','-B','-m','unittest','source_catch_context_inventory_test'],[str(TC/'jdk-25.0.4/bin/javac'),'--release','25','-Xlint:all','-Werror','-d',str(classes),str(helper)])):
        with(out/('phase-'+str(i)+'.private.log')).open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=60)
        if r.returncode:raise ValueError('existing independent fixture/compile lint0 first')
    mirror=out/'input';mirror.mkdir()
    for name in identity['sourceHashes']:
        dest=mirror/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(snapshot/name,dest)
    if {p.relative_to(mirror).as_posix():sha(p)for p in mirror.rglob('*.java')}!=identity['sourceHashes']:raise ValueError('all849 Main-only immutable inputs')
    command=[str(TC/'jdk-25.0.4/bin/java'),'-Xmx1536m','-cp',str(classes),'SourceCatchContextInventory',str(mirror),classpath]
    r=subprocess.run(command,capture_output=True,text=True,timeout=180)
    with(out/'typed.private.log').open('x')as f:f.write(r.stdout+r.stderr);f.flush();os.fsync(f.fileno())
    if r.returncode:raise ValueError('every catch symbol must resolve; preserve failure')
    rows=facts(r.stdout)
    if any(row['path']not in identity['sourceHashes']for row in rows)or inputs()!=(snapshot,classpath,identity)or sha(helper)!=helper_sha or sha(fixture)!=fixture_sha:raise ValueError('all source/type/helper inputs unchanged')
    value={'actualExit':0,'source':SOURCE,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'identity':identity,'helperSha256':helper_sha,'fixtureSha256':fixture_sha,'independentFixtureExit':0,'compileExit':0,'command':command,'rows':rows,'F03Accepted':False,'formalAccepted':False,'sourceSymbolsAreNotTestSuccess':True,'productionChanges':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'source':SOURCE,'typedCatchSites':len(rows),'manifestSha256':sha(out/'manifest.safe.json'),'F03Accepted':False}))
    return 0


if __name__=='__main__':raise SystemExit(main())
