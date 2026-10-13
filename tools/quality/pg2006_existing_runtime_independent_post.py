"""Independent existing-only final runtime/closed-resource oracle; old failed slot immutable."""
import inspect
import pg1986_fresh_resume_independent_post as prior
from pg1877_warning_publication_sources import once

SLOT='pg2006-existing-runtime-independent-post-v1'


def payload():
    raw=prior.payload().replace(prior.SLOT,SLOT).replace("fresh=base/'pg1984-fresh-resume-preparation-v1'","fresh=base/'pg2005-existing-runtime-finish-v1'")
    raw=once(raw,"fresh_private('daemon-reload-reserved.private')==b'one normal runtime daemon-reload; no retry\\n'","fresh_private('daemon-reload-reserved.private')==b'one normal existing-runtime daemon-reload; no retry\\n'")
    raw=once(raw,"hashlib.sha256(fresh_private('before.private.json')).hexdigest()=='ee13ec0b75e1320f4daba711ef90d24b2c05ae588c3b27fedb0224114896fc15'","hashlib.sha256(fresh_private('before.private.json')).hexdigest()=='b3bb209b57ca297b43d5b1fc78e191fcef2dbbf1c9e1645c445b212291a202fe'")
    raw=once(raw,"require(fresh_private('new-runtime.private')==literal)","require(pathlib.Path(target).read_bytes()==literal)")
    raw=once(raw,"lower=(fresh/'before.private.json').stat().st_mtime_ns;upper=(fresh/'runtime-prepared.private.json').stat().st_mtime_ns","lower=(base/'pg1984-fresh-resume-preparation-v1/before.private.json').stat().st_mtime_ns;upper=(base/'pg1995-partial-runtime-recovery-full-post-v1/before.private.json').stat().st_mtime_ns")
    raw=once(raw,"require(runtime_actual==json.loads(fresh_private('runtime-prepared.private.json'))==new['runtime'])","pending_raw=(base/'pg1995-partial-runtime-recovery-full-post-v1/before.private.json').read_bytes()\n    require(hashlib.sha256(pending_raw).hexdigest()=='b3bb209b57ca297b43d5b1fc78e191fcef2dbbf1c9e1645c445b212291a202fe')\n    require(runtime_actual==json.loads(pending_raw)['runtime']==new['runtime'])")
    raw=raw.replace("'freshResumeRuntimePrepared':True","'freshResumeRuntimePrepared':True,'existingFileNoRewrite':True,'old1983CloseUnknownRetained':True")
    from pyflakes.api import check
    if check(raw,'<actual independent existing runtime post>'):raise ValueError('all actual independent post globals required')
    compile(raw,'<existing published runtime exact final post>','exec');return raw


def main():
    raw=inspect.getsource(prior.main).replace('pg1983-prepare-resume-v1.safe.json','pg2003-finish-runtime-v1.safe.json')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<actual existing runtime independent post>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
