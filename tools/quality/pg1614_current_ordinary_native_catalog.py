"""Current ordinary eight native streams; previous ten preserved, not imported."""
import inspect
import pg1588_current_native_catalog_v3 as prior
from pg1609_current_ordinary_owned_stop_sources import bind

def catalog_source():
    raw=bind(prior.catalog_source())
    for old,new in [('d479dcdf4d784f898979844b130dd450','1c085a5e6e874ba1b0d647c92ab3c34c'),('51019','71347'),('51166','71494'),('32060797641','38378028532'),('32061771845','38380559450'),('32062391348','38381232981'),('32062392052','38381233265'),('pg1573-current-resume-once-v1','pg1600-current-ordinary-once-v2'),('len(old)==6','len(old)==10'),('oldSixArchiveUnchanged','oldTenArchiveUnchanged')]:
        if old not in raw:raise ValueError('ordinary native actual window/archive boundary refused')
        raw=raw.replace(old,new)
    old="require(set(excluded)=={'ordinary-inspector196/d69f0f99b48a47a5b51ad571ac996c31.closing.exec','ordinary-inspector196/d69f0f99b48a47a5b51ad571ac996c31.terminal.exec'})"
    expected={'ordinary-inspector196/d69f0f99b48a47a5b51ad571ac996c31.closing.exec','ordinary-inspector196/d69f0f99b48a47a5b51ad571ac996c31.terminal.exec','ordinary-api193/2111873a431743359c0627a8f5e394c8.terminal.exec','root-api193/2111873a431743359c0627a8f5e394c8.before-exec.exec','ordinary-web193/fb683eeb6d3b4e90b66c1576f9108a0c.terminal.exec','root-web193/fb683eeb6d3b4e90b66c1576f9108a0c.before-exec.exec'}
    if raw.count(old)!=1:raise ValueError('ordinary excluded-generation exact set boundary refused')
    raw=raw.replace(old,'require(set(excluded)=='+repr(expected)+')')
    compile(raw,'<ordinary current eight/oldTen native catalog>','exec');return raw

def main():
    raw=inspect.getsource(prior.prior.prior.main).replace('pg1584-current-native-catalog-v1','pg1614-current-ordinary-native-catalog-v1').replace('pg1583-current-terminal-post-v1','pg1613-current-ordinary-terminal-post-v1')
    marker="    payload=('SEALS='+repr(seals)+'\\n'+CODE).encode();(out/'payload.private.py').write_bytes(payload)"
    if raw.count(marker)!=1:raise ValueError('actual complete catalog static gate insertion refused')
    raw=raw.replace(marker,marker+"\n    from pyflakes.api import check\n    if check(payload.decode(),'<actual ordinary native catalog>'):raise ValueError('actual generated catalog static gate refused')")
    env={**prior.prior.prior.__dict__,'CODE':catalog_source()};exec(compile(raw,'<ordinary current native catalog transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
