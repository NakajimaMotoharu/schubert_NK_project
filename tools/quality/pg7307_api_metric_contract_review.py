"""Original API8 + exact known harness/POM/DDL data; twelve semantic negative guards, no PT/DB replay."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
from api_monitoring_harness_contract import verify_api_harness
from batch_metric_pom_contract import verify_batch_core_pom
from host_tool_invocation import capture,verify

SOURCE='72b65394206ac449604e4cffc5d703c55d8fc2f7'
BASELINE='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
BATCH='74371ae0b185cee42e9b6930d68e34522640c2d6'
OUT=host.BASE/'PG7307-api-metric-contract-review-v1'
PINS={
 'batchOriginal':('PG7286-transfer-health-host-v1/manifest.json','06138e3987dc1ec606577cc8d4bcb993ef67d10a762c4aa471aa0997aa69b8f5'),
 'apiOriginal':('PG7300-api-async-metric-host-v1/manifest.json','98dcfb9a731a5479085141bec36815e2c7cc750c977fb9fe4ae51f3092e594af')}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only static contract review')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact original public run');proofs[key]=json.loads(file.read_bytes())
    require(proofs['batchOriginal']['source']==BATCH and proofs['apiOriginal']['source']==SOURCE
      and proofs['batchOriginal']['actualExit']==proofs['apiOriginal']['actualExit']==0,'distinct real original sources, not execution union')
    blob=lambda revision,path:subprocess.check_output(['git','show',revision+':'+path],cwd=host.ROOT)
    sha=lambda raw:hashlib.sha256(raw).hexdigest()
    batch_path='tools/quality/harnesses/monitoring-pom.xml';api_path='tools/quality/harnesses/monitoring-api-jobs-pom.xml'
    batch=blob(SOURCE,batch_path);api=blob(SOURCE,api_path)
    require(batch==blob(BATCH,batch_path) and sha(batch)==proofs['batchOriginal']['begin']['inputHashes'][batch_path]
      and sha(api)==proofs['apiOriginal']['begin']['inputHashes'][api_path],'actual executed templates/hash, no inferred template qualification')
    harness=verify_api_harness(batch,api);harness_negatives=[]
    for kind in ('coverage-minimum','skip-tests','remove-werror','remove-spotbugs','wrong-parent','add-exclusion'):
        root=ET.fromstring(api);plugins=root.find('{*}build/{*}plugins')
        compiler=next(p for p in plugins if p.findtext('{*}artifactId')=='maven-compiler-plugin')
        namespace=root.tag.partition('}')[0]+'}'
        if kind=='coverage-minimum':root.find('.//{*}minimum').text='0.99'
        elif kind=='skip-tests':
            sure=next(p for p in plugins if p.findtext('{*}artifactId')=='maven-surefire-plugin')
            ET.SubElement(sure.find('{*}configuration'),namespace+'skipTests').text='true'
        elif kind=='remove-werror':
            args=compiler.find('{*}configuration/{*}compilerArgs');args.remove(next(a for a in args if a.text=='-Werror'))
        elif kind=='remove-spotbugs':plugins.remove(next(p for p in plugins if p.findtext('{*}artifactId')=='spotbugs-maven-plugin'))
        elif kind=='wrong-parent':root.find('{*}parent/{*}relativePath').text='../other/pom.xml'
        else:ET.SubElement(compiler.find('{*}configuration'),namespace+'excludes')
        try:verify_api_harness(batch,ET.tostring(root))
        except ValueError:harness_negatives.append(dict(kind=kind,rejected=True))
        else:raise ValueError('quality harness mutant accepted')
    pom='src/schubert-nk-api/pom.xml';before=blob(BASELINE,pom);after=blob(SOURCE,pom)
    dependency=verify_batch_core_pom(before,after);pom_negatives=[]
    for kind in ('version','scope','exclusions','duplicate','other-version','missing'):
        root=ET.fromstring(after);deps=root.find('{*}dependencies')
        node=next(n for n in deps if n.findtext('{*}groupId')=='io.micrometer' and n.findtext('{*}artifactId')=='micrometer-core')
        namespace=node.tag.partition('}')[0]+'}'
        if kind=='version':node.find('{*}version').text='1.17.2'
        elif kind=='scope':ET.SubElement(node,namespace+'scope').text='provided'
        elif kind=='exclusions':ET.SubElement(node,namespace+'exclusions')
        elif kind=='duplicate':deps.append(copy.deepcopy(node))
        elif kind=='other-version':
            other=next(n for n in deps if n.findtext('{*}artifactId')=='jspecify');other.find('{*}version').text='1.0.0'
        else:deps.remove(node)
        try:verify_batch_core_pom(before,ET.tostring(root))
        except ValueError:pom_negatives.append(dict(kind=kind,rejected=True))
        else:raise ValueError('API dependency mutant accepted')
    ddl='src/schubert-nk-api/src/main/resources/db/migration/V003__business_message_log_and_web_tables.sql'
    sql=blob(SOURCE,ddl);require(sql==blob(BASELINE,ddl),'original SQL history remains byte unchanged')
    check=re.search(r'CONSTRAINT ck_async_jobs_state CHECK \(state IN \(([^)]+)\)\)',sql.decode())
    require(check is not None,'canonical async state constraint required')
    states=re.findall(r"'([A-Z]+)'",check.group(1))
    require(len(states)==5 and set(states)=={'RECEIVED','PROCESSING','COMPLETED','ERROR','CANCELLED'},'exact independent approved five-state oracle')
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,witnesses=PINS,
      harness=dict(review=harness,apiSha256=sha(api),knownBatchSha256=sha(batch),negativeGuards=harness_negatives),
      apiPom=dict(review=dependency,sha256=sha(after),negativeGuards=pom_negatives),
      canonicalDdl=dict(path=ddl,sha256=sha(sql),sourceBytesUnchanged=True,states=states),
      testsExecuted=0,testStatus='STATIC_REVIEW_NOT_ORDINARY_PT',oldTestSuccessTransferred=False,
      actualVmActions=0,actualDatabaseActions=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,harnessNegatives=len(harness_negatives),pomNegatives=len(pom_negatives),
      canonicalStates=len(states),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
