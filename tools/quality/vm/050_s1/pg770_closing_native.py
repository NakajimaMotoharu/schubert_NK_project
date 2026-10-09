"""Current750 eight plus one latestclosing session; terminal retained, never unioned."""
import json
from pathlib import Path
import re
from pg739_native import source as previous
from pg768_sources import current,actual
from pg769_final import source as qualify_meta
from pg662_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source(proof,baseline,meta,eight_sha):
    qualify_meta(proof,baseline,meta)
    assert type(eight_sha)is str and re.fullmatch('[0-9a-f]{64}',eight_sha)
    raw=current(previous(),proof,baseline)
    raw=replace(raw,(
        ('pg739','pg770'),('PG739','PG770'),('pg738','pg769'),
        ('2f575a4bbd2dd3ae83eb493c12aef0899c3702b6f9bf04bdf5bd46449facb500',eight_sha),
        ('5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a','d4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e'),
        ('82316ed36abbedd2f85f1e26ca35cd2f10e4c1ac5c7deabc4454bcc5203257d4',meta['beforeSha256']),
        ('25e00f13202b08b8db34a8c95b77933ff44cd71d5c37de0fa3cc9aacd5c0609e',meta['afterSha256']),
        ('0d42d02df3a44b7bb036140f6cc076cf',meta['invocation']),
        ('130424890693',str(meta['startMonotonicUs'])),('130426534781',str(meta['endMonotonicUs'])),
        ('2793207',meta['pid']),('13042489',meta['ticks']),('138755',meta['pid1Job']),
        ("relative='ordinary-bootstrap196/'+inv+'.terminal.exec';", "terminal_relative='ordinary-bootstrap196/'+inv+'.terminal.exec';relative='ordinary-bootstrap196/'+inv+'.closing.exec';"),
        ("assert str(p)not in b['native']and set(a['native'])==set(b['native'])|{str(p)}", "terminal_path=pathlib.Path('/run/schubert-nk/pt-coverage')/terminal_relative;terminal_value=a['native'][str(terminal_path)]\nts=terminal_path.lstat();assert meta(ts)==terminal_value['metadata']and stat.S_ISREG(ts.st_mode)and (ts.st_uid,ts.st_gid,stat.S_IMODE(ts.st_mode),ts.st_nlink)==(999,981,0o600,1)and 5<=ts.st_size<=16777216 and not __import__('os').listxattr(terminal_path)\nassert hashlib.sha256(terminal_path.read_bytes()).hexdigest()==terminal_value['sha256']and meta(terminal_path.lstat())==meta(ts)and (ts.st_dev,ts.st_ino)!=(s.st_dev,s.st_ino)\nassert {str(p),str(terminal_path)}.isdisjoint(b['native'])and set(a['native'])==set(b['native'])|{str(p),str(terminal_path)}"),
        ("'relative':relative,'sha256':value['sha256']", "'terminalRelative':terminal_relative,'terminalSha256':terminal_value['sha256'],'terminalBytes':ts.st_size,'relative':relative,'sha256':value['sha256']"),
        ("'point':'TERMINAL'", "'point':'CLOSING'"),
        ("stream=target/'bootstrap.exec'", "stream=target/'bootstrap-closing.exec'")))
    marker="    helper=W/'pg571-current-ten-native-v2/classes'"
    addition="""    terminal=target/'bootstrap-terminal.exec'
    with terminal.open('xb')as f:
        result=subprocess.run(ssh+['sudo -n cat /run/schubert-nk/pt-coverage/'+selected['terminalRelative']],stdout=f,stderr=subprocess.PIPE,timeout=20);f.flush();os.fsync(f.fileno())
    assert result.returncode==0 and not result.stderr and terminal.stat().st_size==selected['terminalBytes']and sha(terminal)==selected['terminalSha256']
"""
    raw=replace(raw,((marker,addition+marker),))
    marker="    result=subprocess.run([java,'-cp',':'.join(cp),'NativeSessions571'"
    addition="""    oracle=W/'pg746-closing-oracle-v1';oracle_record=json.loads((oracle/'manifest.safe.json').read_bytes())
    assert sha(oracle/'manifest.safe.json')=='26cb3b18f8542af5819f1f3a28496a2e3351bed6048fb9ae0fe66ecefa14530c'and oracle_record['actualExit']==0
    assert all(sha(Path(path))==digest for path,digest in oracle_record['files'].items())
    frozen=[host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')for m in ('protocol','storage','bootstrap','api','web','batch')]
    assert all(sha(jar)==h['moduleResults'][m]['jarSha256']for m,jar in zip(('protocol','storage','bootstrap','api','web','batch'),frozen))
    check=subprocess.run([java,'-cp',str(oracle/'classes')+':'+':'.join(cp),'NativeClosing746','BOOTSTRAP',INV,str(selected['lowerMs']),str(selected['upperMs']),str(terminal),str(stream),*map(str,frozen)],capture_output=True,timeout=45)
    with(target/'closing-qualification.safe.json').open('xb')as f:f.write(check.stdout);f.flush();os.fsync(f.fileno())
    assert check.returncode==0 and not check.stderr
    closing=json.loads(check.stdout);assert closing['latestOnly']is True and closing['singleSession']is True and closing['monotonicProbes']is True and type(closing['classByteMismatch'])is int and closing['classByteMismatch']==0
"""
    raw=replace(raw,((marker,addition+marker),
        ("'bootstrap':selected,'bootstrapSession':session", "'bootstrap':selected,'bootstrapSession':session,'closingQualification':closing,'terminalIncludedInCounter':False,'closingOnlyIncludedInCounter':True")))
    return raw


if __name__=='__main__':
    import hashlib
    proof,baseline=actual();meta=json.loads((W/'pg769-actual-admin-meta-v1.safe.json').read_bytes())
    eight_sha=hashlib.sha256((W/'pg766-current-eight-native-v1/manifest.safe.json').read_bytes()).hexdigest()
    env={'__file__':str(R/'pg770_closing_native.py'),'__name__':'latestclosingcurrent750'}
    exec(compile(source(proof,baseline,meta,eight_sha),'<current latestclosing only>','exec'),env);env['main']()
