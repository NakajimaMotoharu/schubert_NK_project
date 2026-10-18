"""Successful owned paths enter protection without heap/callback work; actual Java25 bytecode."""
import hashlib
import json
import os
import re
import subprocess
import pg5120_root_elf_selected as selected

ROOT = selected.ROOT
RUN = ROOT.parent / 'pgpt-runs/PG379/pg5136-factory-io-green-v4'
OUT = ROOT / 'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5138-factory-bytecode-v1'
JAVAP = selected.TC / 'jdk-25.0.4/bin/javap'


def methods(raw):
    result = []; current = None
    for line in raw.splitlines():
        if line.startswith('  ') and not line.startswith('    ') and '(' in line and line.rstrip().endswith(';'):
            current = {'header':line.strip(), 'ops':[], 'handlers':[]}; result.append(current)
        elif current is not None:
            opcode = re.fullmatch(r'\s+(\d+):\s+(\S+)(?:\s+(.*))?', line)
            handler = re.fullmatch(r'\s+(\d+)\s+(\d+)\s+(\d+)\s+(Class .+|any)', line)
            if opcode: current['ops'].append((int(opcode[1]), opcode[2], opcode[3] or ''))
            elif handler: current['handlers'].append((int(handler[1]), int(handler[2]), int(handler[3]), handler[4]))
    return result


def one(values, why):
    if len(values) != 1: raise ValueError(why)
    return values[0]


def index_of(method, needle):
    return one([i for i, row in enumerate(method['ops']) if needle in row[2]], 'one actual '+needle)


def positive_path(method, first, end, kind):
    lookup = {row[0]:i for i,row in enumerate(method['ops'])}
    i = first; visited = []; seen = set()
    while i < len(method['ops']):
        pc, op, arg = method['ops'][i]
        if end is not None and pc == end: return visited
        if end is None and op in ('return','areturn'): return visited
        if pc in seen: raise ValueError('owned success path cycle')
        seen.add(pc); visited.append(pc)
        if op in ('goto','goto_w') or kind == 'nonnull' and op == 'ifnonnull' or kind == 'nonnegative' and op == 'ifge':
            target = int(arg.split()[0])
            if target not in lookup: raise ValueError('actual branch boundary required')
            i = lookup[target]; continue
        if kind == 'nonnull' and op == 'ifnull' or kind == 'nonnegative' and op == 'iflt':
            i += 1; continue
        if not re.fullmatch(r'(?:a|i)load(?:_\d+)?|(?:a|i)store(?:_\d+)?|putfield|checkcast|nop', op):
            raise ValueError('owned-path allocation/link/callback before protection/return: '+op)
        i += 1
    raise ValueError('owned success path has no protected/returned terminal')


def scope_prefix(method):
    opened = index_of(method, 'ResourceScope$Acquire.open:')
    pc = method['ops'][opened][0]
    starts = {row[0] for row in method['handlers'] if row[0] > pc}
    if not starts: raise ValueError('owned body must have exception handlers')
    protected = min(starts)
    types = {row[3] for row in method['handlers'] if row[0] == protected}
    if not {'Class java/io/IOException','Class java/lang/RuntimeException','Class java/lang/Error'} <= types:
        raise ValueError('IO/Runtime/Error all owned body handlers required')
    path = positive_path(method, opened+1, protected, 'nonnull')
    return {'acquirePc':pc,'protectedPc':protected,'successfulPrefixPcs':path,'handlerTypes':sorted(types)}


def canonical(method):
    labels = {row[0]:i for i,row in enumerate(method['ops'])}
    end = method['ops'][-1][0] + 1
    labels[end] = len(method['ops'])
    ops = []
    for pc, op, arg in method['ops']:
        if op.startswith('if') or op in ('goto','goto_w'):
            arg = '@' + str(labels[int(arg.split()[0])])
        else: arg = re.sub(r'#\d+', '#CP', arg)
        ops.append((op.replace('ldc_w','ldc'),arg))
    handlers = [(labels[a],labels[b],labels[c],kind) for a,b,c,kind in method['handlers']]
    return {'ops':ops,'handlers':handlers}


def decode(snapshot, module, name):
    classes = snapshot / ('src/schubert-nk-'+module+'/target/classes')
    path = classes / (name.replace('.', '/')+'.class')
    raw = subprocess.check_output([str(JAVAP),'-p','-c','-classpath',str(classes),name], text=True)
    return methods(raw), {'classSha256':selected.sha(path), 'javapSha256':hashlib.sha256(raw.encode()).hexdigest()}


def main():
    run = json.loads((RUN/'manifest.safe.json').read_bytes())
    if type(run['actualExit']) is not int or run['actualExit'] != 0 or run['phaseExits'] != [0,0]:
        raise ValueError('actual complete same-source selected first')
    snapshot = RUN/'source'
    scope, scope_hash = decode(snapshot,'storage','dev.codex.schubert.nk.storage.ResourceScope')
    acquire = one([m for m in scope if ' T acquire(' in m['header']], 'one typed acquire')
    prefix = scope_prefix(acquire)
    old, old_hash = decode(ROOT.parent/'pgpt-runs/PG379/pg5126-root-guards-green-v1/source',
                           'storage','dev.codex.schubert.nk.storage.ResourceScope')
    old_use = one([m for m in old if ' T use(' in m['header']], 'one old use')
    new_use = one([m for m in scope if ' T use(' in m['header']], 'one current use')
    if canonical(old_use) != canonical(new_use): raise ValueError('old use opcode/handler semantics changed')
    directory, directory_hash = decode(snapshot,'storage','dev.codex.schubert.nk.storage.OwnedTransferDirectory')
    root = one([m for m in directory if ' openRoot(' in m['header']], 'one wrapper root factory')
    opened = index_of(root,'DirectoryCalls.openRoot:')
    constructed = one([i for i,op in enumerate(root['ops']) if '"<init>":(Ldev/codex/schubert/nk/storage/DirectoryCalls;I)V' in op[2]], 'one wrapper constructor')
    if constructed >= opened: raise ValueError('wrapper/stateLock must exist before native root open')
    root_path = positive_path(root, opened+1, None, 'nonnull')
    entry = one([m for m in directory if 'lambda$withEntry$' in m['header'] and any('EntryOpen.open:()I' in op[2] for op in m['ops'])], 'one primitive entry factory')
    entry_open = index_of(entry,'EntryOpen.open:()I')
    allocation = one([i for i,op in enumerate(entry['ops']) if op[1]=='new' and 'OwnedTransferDirectory$EntryHandle' in op[2]], 'one preallocated entry wrapper')
    if allocation >= entry_open: raise ValueError('entry wrapper must exist before primitive acquisition')
    handle, handle_hash = decode(snapshot,'storage','dev.codex.schubert.nk.storage.OwnedTransferDirectory$EntryHandle')
    ctor = one([m for m in handle if '$EntryHandle(' in m['header']], 'one entry constructor')
    if any(op[1] in ('new','newarray','anewarray','multianewarray','invokedynamic','ldc','ldc_w') for op in ctor['ops']):
        raise ValueError('entry constructor allocates after FD argument acquisition')
    descriptor, descriptor_hash = decode(snapshot,'batch','dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmission$RootDescriptor')
    root_ctor = one([m for m in descriptor if '$RootDescriptor(' in m['header']], 'one primitive Root descriptor')
    root_open = index_of(root_ctor,'DirectoryCalls.openRoot:')
    fd_path = positive_path(root_ctor, root_open+1, None, 'nonnegative')
    value = {'source':run['sourceSnapshot'],'actualExit':0,'scopePrefix':prefix,
             'oldUseOpcodeAndHandlerSemanticsEqual':True,'scopeClass':scope_hash,'oldScopeClass':old_hash,
             'directoryClass':directory_hash,'entryHandleClass':handle_hash,'rootDescriptorClass':descriptor_hash,
             'wrapperConstructorBeforeNativeOpen':True,'directorySuccessfulPostOpenPcs':root_path,
             'entryWrapperBeforePrimitiveOpen':True,'entryConstructorAllocationFree':True,
             'rootDescriptorSuccessfulPostOpenPcs':fd_path,'actualHeapOomReproduced':False,
             'selectedManifestSha256':selected.sha(RUN/'manifest.safe.json'),
             'bugs':['BUG1414'],'ssc':['SSC308'],'horizontalComplete':False,
             'formalAccepted':False,'vmActions':0,'testReplays':0}
    os.umask(0o077); OUT.mkdir(parents=True)
    with(OUT/'manifest.json').open('x') as target:
        json.dump(value,target,ensure_ascii=False,indent=2);target.write('\n');target.flush();os.fsync(target.fileno())
    print(json.dumps({'actualExit':0,'source':value['source'],'sha256':selected.sha(OUT/'manifest.json'),
                      'oldUseUnchanged':True,'horizontalComplete':False}))


if __name__=='__main__':
    main()
