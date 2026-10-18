"""Independent 6-site caller/factory tail proof; failed source evidence remains failed."""
import argparse
import json
import os
import subprocess
import pg5138_factory_bytecode as bytecode
import pg5120_root_elf_selected as selected

CLASSES = {'StorageRootInspection':1,'ExistingFileAccess':2,'ServiceConfigFiles':2,'LinuxFilesystemClassifier':1}
FACTORIES = {
 'StorageRootInspection':['OwnedTransferDirectory.open:'],
 'ExistingFileAccess':['ExistingFileAccess$Io.openReadOnly:','OwnedTransferDirectory.openExistingChild:'],
 'ServiceConfigFiles':['ServiceConfigFiles$Io.openReadOnly:','OwnedTransferDirectory.open:'],
}


def tail(method, needle):
    position = bytecode.index_of(method, needle)
    remaining = method['ops'][position+1:]
    if len(remaining) != 1 or remaining[0][1] != 'areturn':
        raise ValueError('factory must directly return owned result: '+needle)
    return [op[0] for op in remaining]


def callers(methods):
    found = []
    for method in methods:
        for i, row in enumerate(method['ops']):
            if 'ResourceScope.acquire:' not in row[2]: continue
            ports = [op for op in method['ops'][:i] if op[1] == 'invokedynamic'][-3:]
            if len(ports) != 3 or any('ResourceScope$'+kind+';' not in op[2]
                                      for op,kind in zip(ports,('Acquire','Release','OwnedAction'))):
                raise ValueError('all three ordered ports before factory entry')
            found.append({'method':method['header'],'acquirePc':row[0],'portPcs':[p[0] for p in ports]})
    if any('ResourceScope.use:' in op[2] for method in methods for op in method['ops']):
        raise ValueError('reviewed owned callers still have legacy gap candidates')
    return found


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',choices=('v2','v3'),required=True)
    parser.add_argument('--revision',choices=('original','parser-v2'),default='original')
    args=parser.parse_args()
    run=selected.ROOT.parent/('pgpt-runs/PG379/pg5140-storage-callers-green-'+args.version)
    manifest=json.loads((run/'manifest.safe.json').read_bytes())
    if manifest['actualExit'] != 0 or manifest['phaseExits'] != [0,0]:
        raise ValueError('complete selected run first, never source substitution')
    snapshot=run/'source'; proofs={}; failures=[]
    for name,count in CLASSES.items():
        methods,hashes=bytecode.decode(snapshot,'storage','dev.codex.schubert.nk.storage.'+name)
        try:
            sites=callers(methods)
            if len(sites)!=count: raise ValueError('exact caller count')
            tails={}
            for needle in FACTORIES.get(name,[]):
                method=bytecode.one([m for m in methods if any(needle in op[2] for op in m['ops'])], 'one fixed factory')
                tails[needle]=tail(method,needle)
            proofs[name]={'sites':sites,'factoryReturnPcs':tails,**hashes}
        except ValueError as failure:
            failures.append(name+': '+str(failure));proofs[name]=hashes
    classes=snapshot/'src/schubert-nk-storage/target/classes'
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-c','-v','-classpath',str(classes),
        'dev.codex.schubert.nk.storage.LinuxFilesystemClassifier'],text=True)
    if 'REF_invokeStatic java/lang/foreign/Arena.ofConfined:()Ljava/lang/foreign/Arena;' not in verbose:
        failures.append('Arena factory method reference must directly return actual confined Arena')
    borrowed,borrowed_hash=bytecode.decode(snapshot,'storage','dev.codex.schubert.nk.storage.LinuxExecDescriptors')
    inherit=bytecode.one([m for m in borrowed if ' void inherit(' in m['header']], 'one borrowed inherit')
    use=bytecode.index_of(inherit,'ResourceScope.use:')
    if any('Method set:' in op[2] for op in inherit['ops'][:use]):
        failures.append('borrowed FD flag mutation precedes scope')
    if not any('FcntlCall.call:' in op[2] for op in inherit['ops'][:use]):
        failures.append('borrowed initial flags read missing')
    value={'source':manifest['sourceSnapshot'],'selectedManifestSha256':selected.sha(run/'manifest.safe.json'),
       'actualExit':int(bool(failures)),'failures':failures,'classes':proofs,
       'borrowedNonApplicable':{'class':'LinuxExecDescriptors','reason':'No acquired resource or changed flags before existing use; mutations under protection',**borrowed_hash},
       'wholeHorizontalComplete':False,'actualHeapOomReproduced':False,'formalAccepted':False,
       'vmActions':0,'testReplays':0,'bugs':['BUG1414'],'ykt':['YKT1178'],'ssc':['SSC308']}
    suffix='' if args.revision=='original' else '-'+args.revision
    out=selected.ROOT/('evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5142-storage-callers-bytecode-'+args.version+suffix)
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':value['actualExit'],'failures':failures,'sha256':selected.sha(out/'manifest.json')}))
    return value['actualExit']


if __name__=='__main__':
    raise SystemExit(main())
