"""Read-only actual current six-build TWR/prebuilt Web owner proof, never native acceptance."""
import hashlib
import inspect
import json
import os
import re
from lan_server import run
import pg5138_factory_bytecode as bytecode
from pg5416_ownership_whole_qualification import SOURCE,ROOT,W,SLOT

CLASSES={
 'dev.codex.schubert.nk.api.storage.ApiApplicationPreparation':'api',
 'dev.codex.schubert.nk.api.file.InspectorApplication':'api',
 'dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain':'api',
 'dev.codex.schubert.nk.web.bootstrap.WebNativeRuntime':'web',
 'dev.codex.schubert.nk.web.bootstrap.WebProcessMain':'web',
 'dev.codex.schubert.nk.web.bootstrap.WebRuntimeExecution':'web'}
TWR={
 'dev.codex.schubert.nk.api.storage.ApiApplicationPreparation':{
  'ApiNativeCodecs.create:':1,'OwnedTransferDirectory.open:':2,'OwnedOutboxDispatcher.create:':1},
 'dev.codex.schubert.nk.api.file.InspectorApplication':{
  'OwnedTransferDirectory.open:':2,'InspectorCredentialLoader.loadDatabasePassword:':1,'InspectorDatabaseConnections."<init>":':1},
 'dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain':{
  'OwnedTransferDirectory.open:':1,'InspectorCredentialLoader.readBootstrapUsername:':1,
  'InspectorCredentialLoader.readBootstrapPassword:':1,'ServiceCredentialReader.readPassword:':1,
  'ServiceDatabaseSource."<init>":':1,'ServiceDatabaseSource.getConnection:':1}}


def collector():
    import hashlib
    import json
    from pathlib import Path
    import subprocess
    base=Path('/home/mini/schubert-nk-pgpt');source=base/'source-full-PG5414'
    results={}
    for name,module in CLASSES.items():
        classes=source/('src/schubert-nk-'+module+'/target/classes')
        path=classes/(name.replace('.','/')+'.class')
        before=hashlib.sha256(path.read_bytes()).hexdigest()
        raw=subprocess.check_output([str(base/'tools/jdk-25.0.4/bin/javap'),'-p','-c','-classpath',str(classes),name],text=True)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=before:raise ValueError('immutable class while reading')
        results[name]={'classSha256':before,'javapSha256':hashlib.sha256(raw.encode()).hexdigest(),'javap':raw}
    print(json.dumps(results))


def local_slot(opcode,kind):
    pc,name,arg=opcode
    match=re.fullmatch(kind+r'(?:_([0-9]+))?',name)
    if not match:raise ValueError('immediate compiler '+kind+' local required')
    return int(match[1]) if match[1] is not None else int(arg)


def twr_site(method,index):
    ops=method['ops']
    if index+2>=len(ops):raise ValueError('factory cannot be unprotected method tail')
    slot=local_slot(ops[index+1],'astore');body=ops[index+2][0]
    handlers=[row for row in method['handlers'] if row[0]<=body<row[1] and row[3] in ('any','Class java/lang/Throwable')]
    if not handlers:raise ValueError('next body instruction not protected by compiler finally/Throwable handler')
    closes=[]
    for position,row in enumerate(ops):
        if position and '.close:' in row[2]:
            try:receiver=local_slot(ops[position-1],'aload')
            except ValueError:continue
            if receiver==slot:closes.append(row[0])
    if len(closes)<2:raise ValueError('normal and exceptional close of the same acquired local required')
    return {'factoryPc':ops[index][0],'registeredLocal':slot,'firstProtectedBodyPc':body,'handlers':handlers,'sameResourceClosePcs':closes}


def twr_class(methods,requirements):
    rows=[]
    for needle,count in requirements.items():
        found=[(method,index) for method in methods for index,row in enumerate(method['ops']) if needle in row[2]]
        if len(found)!=count:raise ValueError('all declared TWR acquisition sites '+needle)
        rows.extend({'method':method['header'],'factory':needle,**twr_site(method,index)} for method,index in found)
    return rows


def web_proof(runtime,entry,execution):
    start=bytecode.one([method for method in runtime if bytecode.named(method,'start')],'one native runtime start')
    targets={'WebBrokerContexts.create:':{'broker'},'WebNativeCodecs.create:':{'codecs'},
        'OwnedTransferDirectory.open:':{'transfer','assets'},'ArtemisReplyConsumers.bind:':{'replies'},
        'WebLogReplayWorker.start:':{'replay'},'RevocationRetryWorker.start:':{'retry'},'WebManagementServer.bind:':{'management'}}
    registered=[]
    for needle,fields in targets.items():
        seen=set()
        for index,row in enumerate(start['ops']):
            if needle not in row[2]:continue
            following=start['ops'][index+1]
            if following[1]!='putfield':raise ValueError('resource return must immediately enter preexisting runtime field')
            field=bytecode.one([name for name in fields if 'Field '+name+':' in following[2]],'exact owned field')
            seen.add(field);registered.append({'factory':needle,'factoryPc':row[0],'field':field,'storePc':following[0]})
        if seen!=fields:raise ValueError('every native runtime acquisition field accounted')
    http=bytecode.one([method for method in runtime if any('Field http:' in row[2] and row[1]=='putfield' for row in method['ops'])],'one prebuilt HTTP owner callback')
    if [row[1] for row in http['ops']]!=['aload_0','aload_1','putfield','return']:
        raise ValueError('HTTP ownership callback stores only the admitted owner')
    call=bytecode.one([method for method in entry if any('WebRuntimeExecution.execute:' in row[2] for row in method['ops'])],'one Web native lifecycle caller')
    point=bytecode.index_of(call,'WebRuntimeExecution.execute:')
    ports=[row for row in call['ops'][:point] if row[1]=='invokedynamic'][-4:]
    if len(ports)!=4 or any(kind not in row[2] for row,kind in zip(ports,('WebRuntimeExecution$Start;','WebRuntimeExecution$Io;','java/lang/Runnable;','WebRuntimeExecution$Io;'))):
        raise ValueError('all start/await/stop/close ports before first native startup')
    constructed=bytecode.index_of(call,'WebNativeRuntime."<init>":')
    if constructed>=call['ops'].index(ports[0]):raise ValueError('whole runtime object/state precede startup ports')
    execute=bytecode.one([method for method in execution if bytecode.named(method,'execute')],'one fixed runtime execution')
    began=bytecode.index_of(execute,'WebRuntimeExecution$Start.run:');pc=execute['ops'][began][0]
    if not any(first<=pc<last and kind=='any' for first,last,_,kind in execute['handlers']):
        raise ValueError('runtime start including partial acquisition must be inside finally protection')
    if not any('holdUnknownInterval:' in row[2] for row in execute['ops']) or not any(
        row[1]=='goto' and int(row[2])<row[0] for row in execute['ops']):
        raise ValueError('existing unknown cleanup still retains frame instead of normal success')
    return {'directResourceFieldStores':registered,'httpPrebuiltOwnerCallback':http['header'],
        'prebuiltLifecyclePortPcs':[row[0] for row in ports],'startInsideFinallyPc':pc,
        'existingUnknownRetainsFrame':True,'nativeOperationsIssued':0}


def main():
    qualification=W/SLOT/'manifest.safe.json';qualified=json.loads(qualification.read_bytes())
    if qualified['actualExit']!=0 or qualified['source']!=SOURCE or qualified['result']['mainClasses']!=1664:
        raise ValueError('same-source actual six qualification first, never partial target/classes')
    out=W/'pg5418-readonly-ownership-bytecode-v1';os.umask(0o077);out.mkdir(mode=0o700)
    raw='CLASSES='+repr(CLASSES)+'\n'+inspect.getsource(collector)+'\ncollector()\n'
    code,output=run("python3 -B - <<'PG5418'\n"+raw+'\nPG5418',timeout=60)
    with(out/'observer.private.log').open('x') as stream:stream.write(output);stream.flush();os.fsync(stream.fileno())
    if code:raise ValueError('read-only current bytecode collection failed; preserve original output')
    rows=json.loads(output.strip())
    if set(rows)!=set(CLASSES):raise ValueError('all exact readonly/control classes required')
    decoded={}
    for name,module in CLASSES.items():
        row=rows[name];key=module+':'+name.replace('.','/')+'.class'
        if row['classSha256']!=qualified['result']['allPhysicalMainSha256'][key] or hashlib.sha256(row['javap'].encode()).hexdigest()!=row['javapSha256']:
            raise ValueError('actual same-source class and exact javap text hashes')
        decoded[name]=bytecode.methods(row['javap'])
    twr={name:twr_class(decoded[name],requirements) for name,requirements in TWR.items()}
    web=web_proof(*(decoded['dev.codex.schubert.nk.web.bootstrap.'+name] for name in ('WebNativeRuntime','WebProcessMain','WebRuntimeExecution')))
    value={'actualExit':0,'source':SOURCE,'wholeQualificationSha256':hashlib.sha256(qualification.read_bytes()).hexdigest(),
        'sourceInputUnchangedAtWholeQualification':True,'readonlyCandidateCount':4,'compilerTwrSites':twr,
        'webPreexistingOwner':web,'classHashes':{name:{key:value for key,value in row.items() if key!='javap'} for name,row in rows.items()},
        'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308'],'formalAccepted':False,'wholeHorizontalComplete':False,
        'newNativeSuccessClaimed':False,'vmActions':0,'testReplays':0,'actualOomReproduced':False}
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5418-readonly-ownership-bytecode-v1';public.mkdir(parents=True)
    with(public/'manifest.json').open('x') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'actualExit':0,'readonlyCandidates':4,'compilerTwrSites':sum(map(len,twr.values())),
        'directWebFieldStores':len(web['directResourceFieldStores']),'httpOwnerCallback':1,'sha256':hashlib.sha256((public/'manifest.json').read_bytes()).hexdigest()}))


if __name__=='__main__':main()
