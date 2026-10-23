"""YKT1413 non-initializing candidate inventory from the exact fixed six normal Jars, not PT acceptance."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
import pg6966_chr_adapter_host as host
import pg7032_monitoring_six_artifact_post as steps
import pg7406_api_generated_contract_six_compile as compilation
from host_tool_invocation import capture,verify

SLOT=host.W/'pg7416-generated-value-inventory-v1'
OUT=host.BASE/'PG7416-generated-value-inventory-v1'
SOURCE=host.ROOT/'tools/quality/architecture/GeneratedValueInventory.java'
PROBE=host.ROOT/'tools/quality/architecture/GeneratedValueInventoryProbe.java'
PINS={
 'physical':('PG7408-api-generated-contract-six-post-v1/manifest.json','2c4db84ee9a0c354aca88ef4dd03220d8b6ea9cd8eb8b80e44e2b39b9877924b'),
 'api':('PG7404-api-generated-contract-post-v1/manifest.json','1386b27f892336a12b79f1432f0eeccece7d47530743748f866a69f529f3d5f5'),
 'generated':('PG7413-api-generated-value-review-v2/manifest.json','7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e')}

def require(value,message):
    if not value:raise ValueError(message)

def parse(text):
    types={};result=None
    for line in text.splitlines():
        p=line.split('\t');tag=p[0]
        if tag=='RESULT':
            require(len(p)==3 and result is None,'one exact result');result=dict(physical=int(p[1]),types=int(p[2]));continue
        require(len(p)>=3,'bounded symbolic row grammar');key=p[1]+':'+p[2]
        if tag=='TYPE':
            require(len(p)==7 and key not in types and p[3] in ('RECORD','ENUM'),'unique generated type row')
            types[key]=dict(role=p[1],className=p[2],kind=p[3],sha256=p[4],sourceFile=p[5],access=int(p[6]),
              components=[],methods=[],initializationDependencies=[])
        else:
            require(key in types,'type row precedes its members')
            row=types[key]
            if tag=='COMPONENT':
                require(len(p)==5,'component grammar');row['components'].append(dict(name=p[3],descriptor=p[4]))
            elif tag=='METHOD':
                require(len(p)==9,'method grammar');row['methods'].append(dict(name=p[3],descriptor=p[4],access=int(p[5]),
                  shape=p[6],firstLine=int(p[7]),lastLine=int(p[8])))
            else:
                require(tag in ('INITCALL','INITFIELD','INITDYNAMIC') and len(p)==7,'initialization dependency metadata only')
                row['initializationDependencies'].append(dict(kind=tag,declaringMethod=p[3],owner=p[4],name=p[5],descriptor=p[6]))
    require(result is not None and result['types']==len(types),'all actual generated types counted, not omissions')
    return types,result

def main():
    invocation=capture(Path(__file__));require(not SLOT.exists() and not OUT.exists(),'new-only exact inventory, never rerun an existing job')
    proofs={}
    for key,(path,digest) in PINS.items():
        file=host.BASE/path;require(host.sha(file)==digest,'exact immutable previous qualification witness');proofs[key]=json.loads(file.read_bytes())
    require(all(p['source']==compilation.SOURCE for p in proofs.values()) and proofs['physical']['allPhysicalClassCount']==1738,
      'all fixed source identities and actual whole physical inventory')
    raw=json.loads((compilation.SLOT/'manifest.safe.json').read_bytes())
    require(raw['source']==compilation.SOURCE and raw['actualExit']==0 and raw['testsExecuted']==0,'actual completed original normal compile, not new PT')
    snapshot=compilation.SLOT/'snapshot';inputs=raw['begin']['inputHashes']
    require(all(host.sha(snapshot/p)==h for p,h in inputs.items()),'all original Main/Test/POM bytes still fixed')
    libraries=[host.TC/f'm2/repository/org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar' for name in ('asm','asm-tree')]
    require(all(proofs['api']['auditLibraries'].get(str(p))==host.sha(p) for p in libraries),'same qualified official ASM9.10.1 bytes')
    jars={};physical={}
    for role,item in raw['jars'].items():
        file=Path(item['path']);require(host.sha(file)==item['sha256'],'original owned Jar bytes')
        jars[role]=file
        with zipfile.ZipFile(file) as jar:
            for entry in jar.namelist():
                if entry.endswith('.class'):
                    key=role+':'+entry;require(key not in physical,'unique physical class role')
                    physical[key]=hashlib.sha256(jar.read(entry)).hexdigest()
    require(set(jars)=={'protocol','storage','bootstrap','api','web','batch'} and len(physical)==1738,'exact six/1738 physical scope')
    os.umask(0o077);SLOT.mkdir();steps.SLOT=SLOT
    helper=SLOT/'helper';probe=SLOT/'probe';helper.mkdir();probe.mkdir()
    jdk=host.TC/'jdk-25.0.4/bin';classpath=os.pathsep.join(map(str,libraries));receipts=[]
    for name,command in (
      ('helper-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(helper),str(SOURCE)]),
      ('probe-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(probe),str(PROBE)]),
      ('probe-archive',[str(jdk/'jar'),'--create','--file',str(SLOT/'probe.jar'),'-C',str(probe),'.'])):
        receipt,_=steps.step(name,command);receipts.append(receipt);require(receipt['actualExit']==0,'owned tool/probe compile and archive zero')
    runtime_classpath=str(helper)+os.pathsep+classpath
    receipt,stdout=steps.step('probe-inspect',[str(jdk/'java'),'-cp',runtime_classpath,'GeneratedValueInventory','canary='+str(SLOT/'probe.jar')])
    receipts.append(receipt);canary,count=parse(stdout)
    require(receipt['actualExit']==0 and count==dict(physical=3,types=2)
      and {r['kind'] for r in canary.values()}=={'RECORD','ENUM'},'own throwing static-initializer types inspected without target loading')
    require(str(probe) not in runtime_classpath and str(SLOT/'probe.jar') not in runtime_classpath,'probe never on actual helper classpath')
    receipt,stdout=steps.step('six-inspect',[str(jdk/'java'),'-cp',runtime_classpath,'GeneratedValueInventory',
      *[role+'='+str(file) for role,file in sorted(jars.items())]])
    receipts.append(receipt);types,count=parse(stdout)
    require(receipt['actualExit']==0 and count['physical']==1738,'all exact actual Jars inspected, no target class initialization')
    verified={row['className']:row for row in proofs['generated']['generatedTypes']}
    roles={role:dict(record=0,enum=0,independentlyVerified=0,pending=0) for role in jars};rows=[]
    for key,row in sorted(types.items()):
        role=row['role'];name=row['className'];require(physical.get(role+':'+name+'.class')==row['sha256'],'each inventoried type original physical byte identity')
        file=row['sourceFile'];require(file.endswith('.java') and '/' not in file and '\\' not in file and '..' not in file,'bounded actual SourceFile metadata')
        package=name.rpartition('/')[0]
        path='src/schubert-nk-'+role+'/src/main/java/'+(package+'/' if package else '')+file
        require(path in inputs and host.sha(snapshot/path)==inputs[path]==host.sha(host.ROOT/path),'actual source owner/path/hash, not inferred fixture')
        committed=subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=host.ROOT)
        require(hashlib.sha256(committed).hexdigest()==inputs[path],'actual qualified committed source')
        known=role=='api' and name in verified and verified[name]['sha256']==row['sha256']
        row.update(sourcePath=path,sourceSha256=inputs[path],contractStatus='CURRENT_SOURCE_API_CONTRACT_VERIFIED' if known
          else 'PENDING_EVIDENCE_AND_SAFETY_REVIEW_NOT_EXECUTION_AUTHORIZED',
          currentSourceExecutionAccepted=known,metadataEnumerationOnly=not known,
          formalAccepted=False,effortPercent=None)
        if known:row['contractWitness']=dict(path=PINS['generated'][0],sha256=PINS['generated'][1],source=compilation.SOURCE)
        roles[role][row['kind'].lower()]+=1;roles[role]['independentlyVerified' if known else 'pending']+=1;rows.append(row)
    require(sum(v['independentlyVerified'] for v in roles.values())==6,'only six source-specific known generated contracts, no new acceptance from enumeration')
    require(all(host.sha(file)==raw['jars'][role]['sha256'] for role,file in jars.items()),'all original artifact bytes remain unchanged')
    value=dict(actualExit=0,source=compilation.SOURCE,invocation=invocation,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      witnesses=PINS,originalCompileManifestSha256=host.sha(compilation.SLOT/'manifest.safe.json'),
      sourceToolSha256=host.sha(SOURCE),probeToolSha256=host.sha(PROBE),libraryHashes={str(p):host.sha(p) for p in libraries},
      jars=raw['jars'],physicalClassCount=1738,generatedTypeCount=len(rows),roleCounts=roles,generatedTypes=rows,
      receipts=receipts,ownedNoInitializationProbe=dict(physical=3,types=2,actualExit=0),
      targetJarsOnHelperClasspath=False,targetClassInitialized=False,original4222Replayed=False,original44Replayed=False,
      productionTestsExecuted=0,testStatus='STATIC_METADATA_INVENTORY_NOT_PT_PASS',
      newContractAcceptanceFromEnumeration=0,expansionClosed=False,relatedExpansion='YKT-1413',
      actualVmActions=0,actualDatabaseActions=0,formalUpdated=False,newAccepted=0,effortPercent=None)
    verify(invocation);OUT.mkdir();host.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,physical=1738,generatedTypes=len(rows),roleCounts=roles,
      newAccepted=0,expansionClosed=False,manifestSha256=host.sha(OUT/'manifest.json'))))

if __name__=='__main__':main()
