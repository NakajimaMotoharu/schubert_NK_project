"""Exact typed-interface dependency/quality invariance, six static negative guards; no runtime replay."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
import pg7366_api_pool_observation_six_compile as compilation
from api_pool_observation_harness_contract import verify_harness
from host_tool_invocation import capture,verify

OUT=host.BASE/'PG7369-api-pool-harness-review-v1'
PINS={
 'before':('PG7348-api-pool-metric-host-v1/manifest.json','57af716e3c9ca07fda2e963f4d029a4eb4e93838a7e98fff74e166f1dd66afc5'),
 'after':('PG7362-api-pool-observation-host-v1/manifest.json',None)}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only original harness quality review')
    witnesses={};proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;sha=host.sha(file);require(digest is None or sha==digest,'original run pin')
        proofs[key]=json.loads(file.read_bytes());witnesses[key]=(path,sha)
    require(proofs['before']['source']=='d23758f47c80e1c90baacfe4fade12b968dda2fa'
      and proofs['after']['source']==compilation.SOURCE and proofs['before']['actualExit']==proofs['after']['actualExit']==0,
      'actual unchanged prior execution and current source actual terminal, not start-only')
    blob=lambda source,path:subprocess.check_output(['git','show',source+':'+path],cwd=host.ROOT)
    path='tools/quality/harnesses/monitoring-api-jobs-pom.xml'
    before=blob(proofs['before']['source'],path);after=blob(compilation.SOURCE,path)
    require(hashlib.sha256(before).hexdigest()==proofs['before']['begin']['inputHashes'][path]
      and hashlib.sha256(after).hexdigest()==proofs['after']['begin']['inputHashes'][path],
      'both actual executed immutable harness input hashes')
    result=verify_harness(before,after);guards=[]
    for kind in ('version','scope','exclusion','coverage','skip-tests','remove-werror'):
        root=ET.fromstring(after);deps=root.find('{*}dependencies')
        node=next(n for n in deps if n.findtext('{*}artifactId')=='HikariCP')
        ns=node.tag.partition('}')[0]+'}'
        if kind=='version':node.find('{*}version').text='7.1.1'
        elif kind=='scope':ET.SubElement(node,ns+'scope').text='provided'
        elif kind=='exclusion':ET.SubElement(node,ns+'exclusions')
        elif kind=='coverage':root.find('.//{*}minimum').text='0.99'
        elif kind=='skip-tests':
            plugins=root.find('{*}build/{*}plugins')
            sure=next(p for p in plugins if p.findtext('{*}artifactId')=='maven-surefire-plugin')
            ET.SubElement(sure.find('{*}configuration'),ns+'skipTests').text='true'
        else:
            plugin=next(p for p in root.find('{*}build/{*}plugins') if p.findtext('{*}artifactId')=='maven-compiler-plugin')
            args=plugin.find('{*}configuration/{*}compilerArgs');args.remove(next(n for n in args if n.text=='-Werror'))
        try:verify_harness(before,ET.tostring(root))
        except ValueError:guards.append(dict(kind=kind,rejected=True))
        else:raise ValueError('dependency/quality mutation accepted')
    root_pom=blob(compilation.SOURCE,'pom.xml');require(root_pom==blob('e7d64fda2453e906ee6ccc5fe718e5c29841e4aa','pom.xml'),'original parent quality and SLF dependency management bytes')
    api_pom=blob(compilation.SOURCE,'src/schubert-nk-api/pom.xml')
    require(ET.fromstring(api_pom).findtext('{*}properties/{*}hikaricp.version')=='7.1.0','same existing API Hikari version')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,witnesses=witnesses,
      harness=result,beforeHarnessSha256=hashlib.sha256(before).hexdigest(),afterHarnessSha256=hashlib.sha256(after).hexdigest(),
      parentPomSha256=hashlib.sha256(root_pom).hexdigest(),apiPomSha256=hashlib.sha256(api_pom).hexdigest(),
      negativeGuards=guards,additionalAuxiliaryPins=copy.deepcopy(compilation.host.EXTRA),newDependenciesDownloaded=False,
      oldTwelveGuardHarnessBytesNotSubstituted=True,testsExecuted=0,testStatus='STATIC_REVIEW_NOT_ORDINARY_PT',
      actualPoolOrConfigCreated=0,actualVmActions=0,actualDatabaseActions=0,actualManagementOperations=0,
      whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,negativeGuards=len(guards),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
