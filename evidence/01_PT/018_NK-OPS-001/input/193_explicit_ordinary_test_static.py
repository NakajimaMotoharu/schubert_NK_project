"""New static measurement only for the frozen public ordinary85 Test/helper set."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as E
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
OLD=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG21744-explicit-ordinary-test-format-audit-v1/manifest.json'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1';SLOT=RUNS/'pg22382-ordinary85-test-static-v1'
HELD={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'}
def main():
    assert sha(OLD)=='5a5b61a9975861232c92a4af0759484e5d4fdccb083cc202a7fa7ad9d552b52a'
    names=sorted(load(OLD)['begin']['inputHashes']);assert len(names)==85 and len(set(names))==85
    assert all(n.startswith('src/') and '/src/test/java/' in n and n.endswith('.java') and not HELD.intersection(Path(n).parts) for n in names)
    inputs={n:sha(R/n) for n in names};source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    for n,h in inputs.items():assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+n],cwd=R)).hexdigest()==h
    normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['actualExit']==0 and nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
    jars={x['path']:x['sha256'] for x in nm['jars'].values()};console=TC/'junit-platform-console-standalone-1.13.4.jar';jars[str(console)]=sha(console)
    for n,h in jars.items():assert sha(n)==h
    static=TC/'static-gates-20261015';rules=R/'tools/quality/static';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))];cs=static/'checkstyle-14.3.0-all.jar';tools={str(p):sha(p) for p in [*pmd,cs,R.parent/'toolchain/jdk-25.0.4/bin/java',rules/'pmd.xml',rules/'checkstyle.xml']}
    assert not SLOT.exists() and not OUT.exists();SLOT.mkdir();c.SLOT=SLOT;listing=SLOT/'sources.txt';listing.write_text(''.join(str(R/n)+'\n' for n in names))
    begin=dict(source=source,productionCoreMain=nm['source'],inputHashes=inputs,legacyAllowlistManifest=dict(path=str(OLD.relative_to(R)),sha256=sha(OLD)),normalManifest=dict(path=str(normal),sha256=sha(normal)),toolHashes=tools,dependencies=jars,driver=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)),heldNamesExcludedBeforeIO=sorted(HELD),startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productTestsExecuted=0,sourceMutation=False)
    write(SLOT/'begin.json',begin);java=str(TC/'jdk-25.0.4/bin/java');stages={}
    stages['pmd']=c.step('pmd',[java,'-cp',':'.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--aux-classpath',':'.join(jars),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],R,timeout=240)
    stages['checkstyle']=c.step('checkstyle',[java,'-jar',str(cs),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],R,timeout=180)
    write(SLOT/'analysis-exits.safe.json',stages);reports={};rows=[]
    for name,tag in [('pmd','violation'),('checkstyle','error')]:
        tree=E.parse(SLOT/(name+'.xml')).getroot();errors=[dict(x.attrib) for x in tree.iter() if name=='pmd' and x.tag.rsplit('}',1)[-1] in ['error','configerror']];count=0
        for file in tree:
            path=file.get('name');assert path is not None;relative=str(Path(path).relative_to(R));assert relative in inputs
            for node in file:
                if node.tag.rsplit('}',1)[-1]!=tag:continue
                count+=1;rows.append(dict(tool=name,path=relative,sourceSha256=inputs[relative],ordinal=count,attributes=dict(node.attrib),message=' '.join(''.join(node.itertext()).split()),classification='UNCLASSIFIED'))
        reports[name]=dict(raw=count,processingErrors=errors,path=name+'.xml',sha256=sha(SLOT/(name+'.xml')))
    assert not any(x['processingErrors'] for x in reports.values());assert stages['pmd']['actualExit'] in [0,4] and stages['checkstyle']['actualExit']>=0 and all(not v['timedOut'] for v in stages.values())
    assert all(sha(R/n)==h for n,h in inputs.items());write(SLOT/'unclassified-sites.json',rows)
    OUT.mkdir();files={}
    for p in SLOT.iterdir():
        if p.is_file():shutil.copyfile(p,OUT/p.name);files[p.name]=sha(OUT/p.name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,begin=begin,stages=stages,reports=reports,checkedFiles=85,unclassifiedSites=len(rows),files=files,productTestsExecuted=0,newSourceProofs=0,newAcceptance=0,sourceBytesUnchanged=True,wholeF03Accepted=False,whole451Accepted=False,effortRate=None)
    write(OUT/'manifest.json',result);print(json.dumps(dict(actualExit=0,pmd=reports['pmd']['raw'],checkstyle=reports['checkstyle']['raw'],unclassified=len(rows),manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
