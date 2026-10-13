"""Current pre-Ref RO failure: whole proof and exact no-bus/three-FD child."""
import ast
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,SSH
import pg2138_current_normal_pair_proof as prior

SLOT='pg2158-normal-ro-retained-pair-proof-v1'


class Current(ast.NodeTransformer):
    def visit_Constant(self,n):
        values={676884:680258,12181426:12374022,676882:680256,676916:680289,12181630:12374207,676914:680287}
        v=n.value
        if type(v)is int:v=values.get(v,v)
        elif type(v)is str:
            for a,b in values.items():v=v.replace(str(a),str(b))
            v=v.replace(prior.TOOLS,'pg2152-normal-candidate-ro-tools-v1').replace(prior.SAVE,'pg2155-normal-candidate-host-ro-v1')
        elif type(v)is bytes:
            v=v.replace(b'pg2132-current-normal-unused-tools-v1/pg2132_native_refs.py',b'pg2152-normal-candidate-ro-tools-v1/pg2152_native_refs.py').replace(b'Pg2132UnusedStage',b'Pg2152CandidateRo').replace(b'\x00place\x00',b'\x00prepare-ro\x00').replace(b'676914',b'680287')
            v=v.replace(b'pg2132-current-normal-unused-tools-v1',b'pg2152-normal-candidate-ro-tools-v1')
        return ast.copy_location(ast.Constant(v),n)


def payload():
    raw=prior.payload();raw=raw[:raw.index("tool=base/'"+prior.TOOLS+"'")]
    # No bus connection existed at the exact candidate_bytes failure point.
    tree=ast.parse(raw)
    class Child(ast.NodeTransformer):
        def visit_FunctionDef(self,n):
            if n.name!='refs_actor':return n
            source=ast.unparse(n)
            source=source.replace("set(fds) == {'0', '1', '2', '3'}", "set(fds) == {'0', '1', '2'}")
            source=source.replace(" and fds['3']['target'].startswith('socket:[')", '')
            source=source.replace('len(names) == 1','len(names) == 0')
            return ast.parse(source).body[0]
    tree=Child().visit(tree);tree=Current().visit(tree);ast.fix_missing_locations(tree);raw=ast.unparse(tree)+'\n'
    raw=raw.replace('Pg2132UnusedStage', 'Pg2152CandidateRo')
    # Bind frozen graph identity separately; never accept candidate as current.
    fixed=json.loads((W/'pg2153-frozen-v1.safe.json').read_bytes())
    raw+='\nFILES='+repr(fixed['fileHashes'])+'\n'
    tail=prior.TAIL
    tail=tail.replace("require(not pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126').exists()and not(base/'pg2126-manifest.sig').exists())", "require(pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126').is_dir()and(base/'pg2126-manifest.sig').is_file())")
    old="b'PG2132_READBACK_UNKNOWN type=ValueError\\nPG2132_FRAME method=<module> line=163\\nPG2132_FRAME method=main line=94\\nPG2132_FRAME method=capture_data line=61\\nPG2132_FRAME method=require line=12\\n'"
    new="b'PG2152_READBACK_UNKNOWN type=ValueError\\nPG2152_FRAME method=<module> line=196\\nPG2152_FRAME method=main line=81\\nPG2152_FRAME method=candidate_bytes line=71\\nPG2152_FRAME method=require line=16\\n'"
    if tail.count(old)!=1:raise ValueError('exact current failure boundary required')
    tail=tail.replace(old,new).replace("'candidateNotPlaced':True","'candidatePlacedUnchanged':True").replace("'childFdCount':4","'childFdCount':3")
    tail=tail.replace('__SLOT__',SLOT).replace('__TOOLS__','pg2152-normal-candidate-ro-tools-v1').replace('__SAVE__','pg2155-normal-candidate-host-ro-v1')
    tail=ast.unparse(Current().visit(ast.parse(tail)))+'\n'
    raw+=tail
    from pyflakes.api import check
    if check(raw,'<actual pre-ref RO pair>'):raise ValueError('whole actual namespace required')
    compile(raw,'<actual pre-ref RO pair>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload().encode();(out/'payload.private.py').write_bytes(raw)
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw,capture_output=True,timeout=120)
    (out/'stderr.private.log').write_bytes(r.stderr);v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'signals0':True,'formalAccepted':False}
    if not r.returncode:v['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
