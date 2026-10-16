"""BUG1334: exact existing dual-stack pair contract; new immutable profile namespace."""
import ast
import inspect
import json
from pg1446_current_cold_stage import W
import pg4058_original_read_profile as previous
import pg3509_tcp_pair_contract as tcp

SLOT = 'pg4060-original-read-profile-v1'


def once(raw, old, new):
    if raw.count(old) != 1: raise ValueError('one diagnostic binding boundary required')
    return raw.replace(old, new)


def payload(action):
    raw = previous.payload(action).replace(previous.SLOT, SLOT)
    if action == 'run':
        old = " table={}\n for line in Path('/proc/net/tcp').read_text().splitlines()[1:]:\n  v=line.split()\n  if v[3]=='01':table[(v[1],v[2])]=v[9]"
        raw = once(raw, old, " table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]")
        old = "  client='0100007F:'+format(row['port'],'04X');server='0100007F:1538'\n  require(table.get((client,server))in inodes(pid)and table.get((server,client))in inodes(row['pid']))"
        raw = once(raw, old, "  tcp_pair(table,row['port'],inodes(pid),inodes(row['pid']))")
        helpers = 'import ipaddress\n' + inspect.getsource(tcp.endpoint) + '\n' + inspect.getsource(tcp.tcp_pair)
        raw = once(raw, 'def peers(value,owned=None):', helpers + '\ndef peers(value,owned=None):')
        frozen = json.loads((W / (SLOT + '-compile') / 'manifest.safe.json').read_bytes())
        if frozen['actualExit'] != 0 or frozen['result']['actualExit'] != 0:
            raise ValueError('actual new hash-complete compile first')
        pins = frozen['result']['classHashes']
        check = "require(compiled['classHashes']==" + repr(pins) + " and {str(p.relative_to(classes)):hashlib.sha256(p.read_bytes()).hexdigest()for p in classes.rglob('*.class')}==" + repr(pins) + ")\n"
        raw = once(raw, "require(not os.path.lexists(save/'run-reserved.private'))", check + "require(not os.path.lexists(save/'run-reserved.private'))")
    else:
        old = "(save/'compile.safe.json').write_text(json.dumps(value,sort_keys=True))"
        raw = once(raw, old, "value['classHashes']={str(p.relative_to(classes)):hashlib.sha256(p.read_bytes()).hexdigest()for p in classes.rglob('*.class')}\nrequire(r.returncode!=0 or bool(value['classHashes']))\n" + old)
    # No role translation may alter the Java diagnostic or pinned annotation bytes.
    def constant(text, name):
        return ast.literal_eval(next(n.value for n in ast.parse(text).body
                                     if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
                                     and t.id == name for t in n.targets)))
    original = previous.payload(action)
    if any(constant(raw, n) != constant(original, n) for n in ['JAVA_B64', 'ANNOTATION_B64']):
        raise ValueError('diagnostic input bytes must be preserved')
    compile(raw, '<dual-stack complete readonly profile>', 'exec')
    return raw


def main():
    namespace = {**previous.__dict__, 'payload': payload, 'SLOT': SLOT}
    exec(compile(inspect.getsource(previous.main), '<new profile compile or run>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
