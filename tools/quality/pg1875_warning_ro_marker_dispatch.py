"""New direct RO slot; real emitted producer prequal before any ownership."""
import inspect
import pg1870_warning_candidate_ro_dispatch as prior
from pg1872_warning_ro_marker_sources import sources,TOOLS,CLASS,bind
from pg1873_warning_ro_marker_compile import TARGET

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg1875-fixed-stage-v1'
STAGE=bind(prior.STAGE).replace('pg1870-fixed-stage-v1','pg1875-fixed-stage-v1')


def source():
    raw=bind(inspect.getsource(prior.main)).replace('pg1870-','pg1875-').replace('pg1868-frozen','pg1873-frozen')
    marker="            cp=GUEST+':/opt/schubert-nk/releases/0.1.0-PG1638/operations/batch.jar"
    if raw.count(marker)!=1:raise ValueError('one actual owner-before producer gate required')
    prequal="""            check=subprocess.run(SSH+['sudo','-n','python3','-B',GUEST+'/pg1872_input_preflight.py'],capture_output=True,timeout=20)
            expected=b'PG1872_INPUT_CLOSURE_READY\\n'
            pre={'actualExit':check.returncode,'frozenSource':operator,'producerConsumerLiteralMatched':check.stdout==expected and not check.stderr,'MARefDBMount0':True,'stdoutSha256':hashlib.sha256(check.stdout).hexdigest(),'stderrSha256':hashlib.sha256(check.stderr).hexdigest()}
            with(W/'pg1875-actual-marker-prequal-v1.safe.json').open('x')as f:json.dump(pre,f,sort_keys=True)
            if check.returncode or check.stdout!=expected or check.stderr:raise ValueError('actual fixed producer/consumer mismatch before ownership')
"""
    raw=raw.replace(marker,prequal+marker)
    compile(raw,'<actual new RO preownership producer gate>','exec');return raw


def main():
    ns={**prior.__dict__,'TARGET':TARGET,'GUEST':GUEST,'REMOTE':REMOTE,'STAGE':STAGE,'sources':sources,'TOOLS':TOOLS,'CLASS':CLASS}
    exec(compile(source(),'<direct real producer qualified RO entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
