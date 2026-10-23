"""Public frozen POM/label-source review and six semantic rejection vectors; no Maven/PT replay."""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import pg6966_chr_adapter_host as host
from host_tool_invocation import capture,verify
from batch_metric_pom_contract import verify_batch_core_pom

SOURCE='34813cef90b2a5c6b2ad3be835565bf53e96a875'
BASELINE='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'
OUT=host.BASE/'PG7257-batch-metric-pom-review-v1'
POM='src/schubert-nk-batch/pom.xml'
GOLDEN_STEPS={'BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION',
 'CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'}
GOLDEN_STATUSES={'SUCCESS','WARNING','FAILED','SKIPPED'}

def require(value,message):
    if not value:raise ValueError(message)

def main():
    invocation=capture(Path(__file__));require(not OUT.exists(),'new-only public semantic review')
    blob=lambda revision,path:subprocess.check_output(['git','show',revision+':'+path],cwd=host.ROOT)
    before=blob(BASELINE,POM);after=blob(SOURCE,POM)
    require(host.sha(host.ROOT/POM)==__import__('hashlib').sha256(after).hexdigest(),'actual frozen Batch POM')
    positive=verify_batch_core_pom(before,after);negative=[]
    for kind in ('version','scope','exclusions','duplicate','unrelated-version','missing'):
        root=ET.fromstring(after);deps=root.find('{*}dependencies')
        require(deps is not None,'fixed dependency parent')
        node=next(n for n in deps if n.findtext('{*}groupId')=='io.micrometer' and n.findtext('{*}artifactId')=='micrometer-core')
        namespace=node.tag.partition('}')[0]+'}'
        if kind=='version':node.find('{*}version').text='1.17.2'
        elif kind=='scope':ET.SubElement(node,namespace+'scope').text='provided'
        elif kind=='exclusions':ET.SubElement(node,namespace+'exclusions')
        elif kind=='duplicate':deps.append(copy.deepcopy(node))
        elif kind=='unrelated-version':
            other=next(n for n in deps if n.findtext('{*}artifactId')=='jspecify');other.find('{*}version').text='1.0.0'
        else:deps.remove(node)
        try:verify_batch_core_pom(before,ET.tostring(root))
        except ValueError:negative.append(dict(kind=kind,rejected=True))
        else:raise ValueError('semantic POM mutant accepted')
    refs=[]
    for path,pattern,golden in (
      ('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchStep.java',r'\b([A-Z][A-Z_]+)\((?:true|false)\)',GOLDEN_STEPS),
      ('src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchStepResult.java',r'public enum Status\s*\{([^}]+)\}',GOLDEN_STATUSES)):
        current=blob(SOURCE,path);require(current==blob(BASELINE,path),'legacy canonical source byte unchanged')
        if 'BatchStepResult' in path:values=set(re.findall(r'\b[A-Z][A-Z_]+\b',re.search(pattern,current.decode()).group(1)))
        else:values=set(re.findall(pattern,current.decode()))
        require(values==golden,'every declared terminal label canonical, no extra/Morning invented')
        refs.append(dict(path=path,sha256=__import__('hashlib').sha256(current).hexdigest(),values=sorted(values),sourceBytesUnchanged=True))
    value=dict(actualExit=0,source=SOURCE,invocation=invocation,review=positive,negativeGuards=negative,
      supportingCanonicalSource=refs,testsExecuted=0,testStatus='STATIC_REVIEW_NOT_ORDINARY_PT',
      actualBatchInvocations=0,actualVmActions=0,actualDatabaseActions=0,whole451Accepted=False,
      formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);os.umask(0o077);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,negativeGuards=len(negative),canonicalSources=len(refs),manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
