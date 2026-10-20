"""Independent actual JVM acquisition order/unchanged lifecycle proof; never invokes Main."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pg5940_private_lock_compile import W, BASE, TC, sha
from pg6114_http_owner_qualification import SOURCE
from pg6112_http_owner_selected import OWNERS
from pg6056_expiry_read_methods import methods
from pg6084_web_factory_order import instructions, narrow_or_wide_literal_body
from classfile_field_flags import fields


def resolved_body(code, verbose):
    """Resolve actual bootstrap handles/arguments,not a blanket InvokeDynamic-number waiver."""
    bindings = []
    for index in re.findall(r'// InvokeDynamic #(\d+):', code):
        section = verbose.split('BootstrapMethods:', 1)[1]
        match = re.search(r'(?m)^  '+index+r':[^\n]*\n(?:(?!  \d+:|\S)[^\n]*\n)*', section)
        if match is None:
            raise ValueError('actual bootstrap handle/all arguments required')
        binding = re.sub(r'^  \d+:', '  index:', match.group(0))
        binding = re.sub(r'#\d+(?=\s)', '#CP', binding)
        bindings.append(binding)
    normalized = re.sub(r'InvokeDynamic #\d+:', 'InvokeDynamic #resolved:', code)
    return narrow_or_wide_literal_body(normalized), bindings


def prepared_owner(blocks, cls, field_names, factory, final_field):
    constructors = [(k, v) for k, v in blocks.items() if k.startswith('  private '+cls+'(')]
    if len(constructors) != 1:
        raise ValueError('one prepared private constructor')
    name, code = constructors[0]
    ops = instructions(code)
    calls = [i for i, (_, op, arg) in enumerate(ops) if op == 'invokeinterface' and factory in arg]
    if len(calls) != 1 or any(factory in v for k, v in blocks.items() if k != name):
        raise ValueError('single factory acquisition only inside prepared owner')
    before, after = ops[:calls[0]], ops[calls[0]+1:]
    for field in field_names:
        if sum(op == 'putfield' and '// Field '+field+':' in arg for _, op, arg in before) != 1:
            raise ValueError('every required owner/state field initialized before acquisition: '+field)
    stores = []
    for _, op, arg in after:
        if op in ('ldc', 'ldc_w', 'checkcast', 'return'):
            continue
        if op == 'invokestatic' and 'java/util/Objects.requireNonNull:' in arg:
            continue
        if op == 'putfield' and '// Field '+final_field+':' in arg:
            stores.append(arg)
            continue
        raise ValueError('no allocation/callback/unknown call/branch after acquisition: '+op)
    if len(stores) != 1 or not after or after[-1][1] != 'return':
        raise ValueError('one final resource store and return')
    return {'constructor': name, 'preparedFields': list(field_names), 'factoryOffset': ops[calls[0]][0],
            'postAcquireOpcodes': [op for _, op, _ in after],
            'constructorSha256': hashlib.sha256(code.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--qualification-sha256', required=True)
    args = parser.parse_args()
    qp = BASE/'PG6114-http-owner-qualification-v1/manifest.json'
    if sha(qp) != args.qualification_sha256:
        raise ValueError('genuine same-source original1939 qualification first')
    q = json.loads(qp.read_bytes())
    if q['source'] != SOURCE or q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (1939, 318, 1667):
        raise ValueError('one current source/1939/318/1667')
    roots = [W/'pg6106-locked-flag-web925-v1/source/src', W/'pg6112-http-owner-selected-v1/source/src']
    def jar(module, current):
        return roots[int(current)]/f'schubert-nk-{module}/target/schubert-nk-{module}-0.1.0-SNAPSHOT.jar'
    def read(module, cls, current, flags=('-p', '-c', '-s')):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), *flags, '-classpath', str(jar(module, current)), cls], text=True)
    proofs = []
    for module, names in OWNERS.items():
        for name in names:
            cls = 'dev.codex.schubert.nk.'+name.replace('/', '.')
            old, new = [methods(read(module, cls, now)) for now in (False, True)]
            management = cls.endswith('ManagementServer')
            required = ['healthy', 'information', 'executor', 'promoted', 'promotionAttempted', 'closed'] if management else ['mvc', 'lifecycleLock']
            if name.endswith('WebManagementServer'):
                required += ['stopping', 'stopLock']
            factory = '$Factory.create:' if management else 'java/util/function/Supplier.get:'
            resource = 'server' if management else 'tomcat'
            proof = prepared_owner(new, cls, required, factory, resource)
            with zipfile.ZipFile(jar(module, True)) as archive:
                ff = fields(archive.read(cls.replace('.', '/')+'.class'))
            if ff[resource.encode()]['flags'] != 0x12:
                raise ValueError('private final owned resource')
            before_abi = read(module, cls, False, ('-public', '-s'))
            if before_abi != read(module, cls, True, ('-public', '-s')):
                raise ValueError('public ABI unchanged')
            abi = lambda d: sorted(k for k in d if not k.startswith('  private '))
            if abi(old) != abi(new):
                raise ValueError('all public/package method signatures unchanged')
            changed, unchanged = [], []
            old_verbose, new_verbose = [read(module, cls, now, ('-p', '-v')) for now in (False, True)]
            for signature in old.keys() & new.keys():
                if resolved_body(old[signature], old_verbose) == resolved_body(new[signature], new_verbose):
                    unchanged.append(signature)
                else:
                    changed.append(signature)
            permitted = ' open(' if name.endswith('ApiManagementServer') else ' bind(' if management else ' startWithOwner('
            if len(changed) != 1 or permitted not in changed[0]:
                raise ValueError('only declared acquisition caller changes;all shared lifecycle methods unchanged')
            old_private = set(old)-set(new)
            new_private = set(new)-set(old)
            if not old_private or not new_private or any(not k.startswith('  private ') for k in old_private | new_private):
                raise ValueError('constructor/private thread lambda relocation only')
            if (len(old_private), len(new_private)) != ((2, 2) if management else (1, 1)) or any(
                    not (k.startswith('  private '+cls+'(') or management and 'lambda$' in k)
                    for k in old_private | new_private):
                raise ValueError('no undeclared extra private method change')
            if management:
                old_lambda = [old[k] for k in old_private if 'lambda$' in k]
                new_lambda = [new[k] for k in new_private if 'lambda$' in k]
                if len(old_lambda) != 1 or len(new_lambda) != 1 or resolved_body(old_lambda[0], old_verbose) != resolved_body(new_lambda[0], new_verbose):
                    raise ValueError('relocated daemon-thread lambda instructions unchanged')
            proof.update(className=cls, unchangedMethods=sorted(unchanged), changedCaller=changed,
                         oldPrivateSignatures=sorted(old_private), newPrivateSignatures=sorted(new_private), publicAbiUnchanged=True)
            proofs.append(proof)
    nested = [key for key in q['changedPhysical'] if '$' in key]
    for key in nested:
        module, member = key.split(':', 1)
        cls = member[:-6].replace('/', '.')
        if methods(read(module, cls, False)) != methods(read(module, cls, True)):
            raise ValueError('any changed nested class must have identical executable methods')
    result = {'actualExit': 0, 'source': SOURCE, 'qualificationSha256': sha(qp), 'owners': proofs,
              'nestedDebugOnly': nested,
              'testsExecuted': 0, 'additionalBuildsIssued': 0, 'dynamicOomExecuted': False,
              'vmActions': 0, 'formalAccepted': False, 'nativeQualified': False, 'ptAlternativeCompleted': 0}
    os.umask(0o077)
    out = BASE/'PG6116-http-owner-order-v1'
    out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'actualExit': 0, 'source': SOURCE, 'owners': len(proofs), 'manifestSha256': sha(out/'manifest.json')}))


if __name__ == '__main__':
    main()
