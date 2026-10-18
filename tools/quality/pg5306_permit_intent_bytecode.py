"""Actual entire Permit/Intent assembly chain; original four and extra two never conflated."""
import json
import subprocess
import pg5138_factory_bytecode as bytecode
import pg5142_storage_callers_bytecode as caller
import pg5265_owned_factory_proof as proof
import pg5304_permit_intent_selected as entry
from pg5290_morning_launch_bytecode import enclosing

SOURCE='c29752dbe4de7b24ee92bfa4fb71f2e164c16515'
OUT='PG5306-permit-intent-bytecode-v1'


def returned_owner(method,index):
    declared=method['header'].split('(',1)[0].split()[-2]
    tail=method['ops'][index+1:]
    if len(tail)!=2 or [o[1] for o in tail]!=['checkcast','areturn'] or tail[0][2].partition('//')[2].strip()!='class '+declared.replace('.','/'):
        raise ValueError('only exact declared return-type cast and immediate return after handoff')
    return {'declaredReturnType':declared,'checkcastPc':tail[0][0],'returnPc':tail[1][0]}


def handoffs(methods):
    found=[]
    for method in methods:
        for i,row in enumerate(method['ops']):
            if 'ResourceScope.handoff:' not in row[2]:continue
            ports=[o for o in method['ops'][:i] if o[1]=='invokedynamic'][-3:]
            if len(ports)!=3 or any('ResourceScope$'+kind+';' not in op[2] for op,kind in
                zip(ports,('Acquire','Release','OwnedAction'))):
                raise ValueError('all three handoff ports precede any acquisition')
            returned=returned_owner(method,i)
            found.append({'method':method['header'],'handoffPc':row[0],'portPcs':[o[0] for o in ports],**returned})
    return found


def main():
    run,value=proof.prove(entry=entry,run_name='pg5304-permit-intent-green-v1',
        prior_name='pg5296-handoff-green-v1',source=SOURCE,tests=1038,suites=126,
        package='dev.codex.schubert.nk.batch.file.',
        scopes={'MorningPermitPublication':4,'BackupStartIntentFiles':0},
        kinds={'MorningPermitPublication':{'OwnedTransferDirectory.open:':1,
                    'BackupStartIntentFiles.createPublication:':1},'BackupStartIntentFiles':{}},out_name=OUT,
        qualification_path=entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5304-permit-intent-green-v1/qualification.safe.json')
    package='dev.codex.schubert.nk.batch.file.';details={}
    prior=entry.selected.ROOT.parent/'pgpt-runs/PG379/pg5296-handoff-green-v1/source'
    for name,count in [('MorningPermitPublication',3),('BackupStartIntentFiles',2)]:
        methods,hashed=bytecode.decode(run/'source','batch',package+name)
        actual=handoffs(methods)
        if len(actual)!=count:raise ValueError('exact complete assembly boundary count '+name)
        details[name]={'handoffs':actual,'class':hashed}
        verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-v','-classpath',
            str(run/'source/src/schubert-nk-batch/target/classes'),package+name],text=True)
        if name=='MorningPermitPublication':
            for owner,method,result in [('OpenStore','open','Store'),('OpenIntent','open','Intents')]:
                needle='REF_invokeInterface dev/codex/schubert/nk/batch/file/MorningPermitPublication$'+owner+'.'+method+':()Ldev/codex/schubert/nk/batch/file/MorningPermitPublication$'+result+';'
                if needle not in verbose:raise ValueError('direct raw owner-port factory reference')
            for simple,needle in [('Publication','class dev/codex/schubert/nk/batch/file/MorningPermitPublication'),
                                  ('Intents','class dev/codex/schubert/nk/batch/file/MorningPermitPublication$1'),
                                  ('Store','class dev/codex/schubert/nk/batch/file/MorningPermitPublication$2')]:
                constructors=[m for m in methods if any(o[1]=='new' and o[2].partition('//')[2].strip()==needle for o in m['ops'])]
                method=bytecode.one(constructors,'one protected assembly '+simple)
                if 'lambda$' not in method['header']:raise ValueError('constructor must be inside protected owned action')
                details[name][simple+'AssemblyMethod']=method['header']
        else:
            raw=[m for m in methods if any('OwnedTransferDirectory.open:' in o[2] for o in m['ops']) and not bytecode.named(m,'createService')]
            if len(raw)!=2:raise ValueError('only two extra Directory factories')
            details[name]['rawDirectoryTails']=[{'method':m['header'],'returnPcs':caller.tail(m,'OwnedTransferDirectory.open:')} for m in raw]
            old,_=bytecode.decode(prior,'batch',package+name)
            before=bytecode.one([m for m in old if bytecode.named(m,'createService')],'old manual contract')
            after=bytecode.one([m for m in methods if bytecode.named(m,'createService')],'current manual contract')
            if before['header']!=after['header'] or bytecode.canonical(before)!=bytecode.canonical(after):
                raise ValueError('existing service manual try/compound precedence must not change')
            details[name]['manualCreateServiceOpcodesAndHandlersUnchanged']=True
    for row in value['nestedDebugEquivalent']:
        before=enclosing(prior,row['class']);after=enclosing(run/'source',row['class'])
        row.update(enclosingMethodBefore=before,enclosingMethodAfter=after,enclosingMethodEqual=before==after,
            pureDebugDifferenceNotAsserted=True)
    value.update(completeAssemblyProofs=details,originalScopeSites=4,internalAssemblyHandoffs=3,
        extraDirectoryOwnerFactories=2,protectedAcquisitionBoundaries=9,physicalDirectoryFactorySites=3,
        nativeOwnerExecutionQualified=False)
    result=json.loads((run/'manifest.safe.json').read_bytes())
    value['storageFourCounters']=result['storageFourCounters']
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
