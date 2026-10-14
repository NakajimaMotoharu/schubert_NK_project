"""New-only currentboot candidate input/immutable helper transport, no placement."""
import hashlib
import json
import subprocess
import pg2820_network_current_cold_stage as prior
import pg1446_current_cold_stage as transport
import pg2832_network_cold_unused_sources as s
from pg2834_network_cold_unused_compile import FROZEN
from pg1674_critical_management_gate import management_gate

SLOT='pg2836-network-cold-unused-stage-v1'


def source():
    raw=prior.source()
    for a,b in [('pg2818-network-current-cold-frozen-v1.safe.json',FROZEN),
        ('pg2820', 'pg2836'),('PG2820','PG2836'),(s.current.TOOLS,s.TOOLS)]:
        if a not in raw:raise ValueError('exact new-only stage family required')
        raw=raw.replace(a,b)
    compile(raw,'<immutable candidate helper transport>','exec');return raw


def main():
    s.qualify();frozen=json.loads((transport.W/FROZEN).read_bytes())
    if frozen.get('actualExit')!=0 or frozen.get('candidateSource')!=s.CANDIDATE:
        raise ValueError('qualified cold unused bundle required')
    bundle=transport.P/s.ARCHIVE;signature=transport.P/'pg2802-manifest-v1.sig'
    if hashlib.sha256(bundle.read_bytes()).hexdigest()!=frozen['bundle']['archiveSha256']or hashlib.sha256(signature.read_bytes()).hexdigest()!=s.SIGNATURE:
        raise ValueError('frozen candidate transport bytes required')
    with management_gate(transport.P/'current-management-critical.lock'):
        # Root verifies newboot and absence BEFORE creating the new input namespace.
        code="""import os,pathlib
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT
for p in [INPUT,'/opt/schubert-nk/releases/0.1.0-PG2802','/var/lib/pgpt-s1-preservation/pg2802-manifest.sig']:
 assert not os.path.lexists(p)
os.mkdir(INPUT,0o700);os.chown(INPUT,1000,1000)
"""
        code='BOOT='+repr(s.current.BOOT)+'\nINPUT='+repr('/home/ubuntu/'+s.INPUT)+'\n'+code
        subprocess.run(transport.SSH+['sudo','-n','python3','-B','-'],input=code.encode(),check=True)
        opts=transport.SSH[1:-1];opts.remove('-T');opts[opts.index('-p')]='-P'
        subprocess.run(['scp','-q',*opts,str(bundle),str(signature),str(transport.W/s.TOOLS/'bundle.safe.json'),
            'ubuntu@127.0.0.1:/home/ubuntu/'+s.INPUT+'/'],check=True)
        ns={**transport.__dict__,'OUT':transport.W/SLOT,'TOOLS':transport.W/s.TOOLS}
        exec(compile(source(),'<actual immutable cold unused helper transport>','exec'),ns);ns['main']()
    return 0


if __name__=='__main__':raise SystemExit(main())
