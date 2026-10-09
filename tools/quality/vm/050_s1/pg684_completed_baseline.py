"""Fresh completed current21 (old20 + currentBootstrap proofs), read-only no authority."""
from pathlib import Path
from pg661_current_baseline import source as previous

R = Path(__file__).resolve().parent


def source():
    raw = previous()
    pairs = (
        ('pg661-completed-baseline-v1', 'pg684-completed-baseline-v1'),
        ("sealed=strict(base/'pg655-native-stop-v1/after.private.json',0o600,67108864);require(hashlib.sha256(sealed).hexdigest()=='c13792efb16007ad6fbdcec310dc9c8a598d9a5bad1b4680bef93384ab092285');old=json.loads(sealed)",
         "sealed=strict(base/'pg664-bootstrap-existing-v1/after.private.json',0o600,67108864);require(hashlib.sha256(sealed).hexdigest()=='fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98');old=json.loads(sealed)\nactor=json.loads(strict(base/'pg664-bootstrap-existing-v1/actor.private.json',0o600,4096));require(actor['pid']=='2142585'and actor['ticks']=='11164505'and actor['invocation']=='65bfe1da3b9e454997f1d899fea9510e'and not pathlib.Path('/proc',actor['pid']).exists())\ngc_nodes=[n for n in ast.parse(GC_SOURCE).body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=gc_nodes,type_ignores=[]),'<known20 finiteGC only>','exec'),globals())"),
        ("require(strict(base/'pg655-native-stop-v1/complete.private',0o600,4096)==b'genuineParentDone=true\\nallEightOwnedTerminal=true\\nallNewScopesReturnedNormally=true\\noriginalBackupStartupRowsPreserved=true\\nstarts0=true\\noldUnknownNormalized=false\\n')",
         "require(strict(base/'pg664-bootstrap-existing-v1/complete.private',0o600,4096)==b'allNewScopesReturnedNormally=true\\nall24DatabaseUnchanged=true\\nmode=execute\\n')"),
        ("require(v['units']==old['units']and v['configuration']==old['configuration'])",
         "for u,known in old['units'].items():\n   current=v['units'][u];conf=v['configuration'][u]\n   if u=='schubert-nk-bootstrap-admin.service'and current!=known:require(current_gc_after_known20(known,current)and configuration_after_gc(old['configuration'][u],conf,actor))\n   else:require(current==known and conf==old['configuration'][u])"),
        ("old['pid1']", "old['parentPid1']"),
        ("require(len(v)==20);return v",
         "v['currentBootstrapProofs']={n:tree(base/n)for n in ('pg664-bootstrap-tools-v1','pg664-bootstrap-verify-v1','pg664-bootstrap-existing-v1')}\n  require(len(v)==21);return v"),
        ("'full20Fields':True", "'full21Fields':True,'currentBootstrapPrivateProofsPreserved':True"),
        ('input=PAYLOAD.encode()', "input=('GC_SOURCE='+repr((R/'pg537_bootstrap_gc_contract.py').read_text())+'\\n'+PAYLOAD).encode()"),
    )
    for old, new in pairs:
        assert old in raw, old
        raw = raw.replace(old, new)
    return raw


if __name__ == '__main__':
    env = {'__file__': str(R/'pg684_completed_baseline.py'), '__name__': 'current_completed_readonly'}
    exec(compile(source(), '<current completed21 readonly>', 'exec'), env)
    env['main']()
