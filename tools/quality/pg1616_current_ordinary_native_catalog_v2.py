"""Strict actual native-before bytes/sha256 schema; preserve failed1614 slot."""
import inspect
import hashlib
import re
import pg1614_current_ordinary_native_catalog as prior

def archive_record(value,raw):
    if type(value)is not dict or set(value)!={'bytes','sha256'}or type(value['bytes'])is not int or not 0<value['bytes']<=16777216 or type(value['sha256'])is not str or re.fullmatch('[0-9a-f]{64}',value['sha256'])is None:raise ValueError('strict actual native archive record refused')
    if type(raw)is not bytes or len(raw)!=value['bytes']or hashlib.sha256(raw).hexdigest()!=value['sha256']:raise ValueError('actual private archive byte identity refused')

def catalog_source():
    raw=prior.catalog_source()
    old="p=archive/'native-before-private'/relative;require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])"
    if raw.count(old)!=1:raise ValueError('actual archive schema correction boundary refused')
    raw=raw.replace(old,"p=archive/'native-before-private'/relative;archive_record(v,p.read_bytes())")
    raw='import re\n'+inspect.getsource(archive_record)+'\n'+raw
    compile(raw,'<current strict bytes archive native catalog>','exec');return raw

def main():
    raw=inspect.getsource(prior.prior.prior.prior.main).replace('pg1584-current-native-catalog-v1','pg1616-current-ordinary-native-catalog-v2').replace('pg1583-current-terminal-post-v1','pg1613-current-ordinary-terminal-post-v1')
    marker="    payload=('SEALS='+repr(seals)+'\\n'+CODE).encode();(out/'payload.private.py').write_bytes(payload)"
    if raw.count(marker)!=1:raise ValueError('actual complete catalog static gate insertion refused')
    raw=raw.replace(marker,marker+"\n    from pyflakes.api import check\n    if check(payload.decode(),'<actual strict ordinary native catalog>'):raise ValueError('actual generated catalog static gate refused')")
    env={**prior.prior.prior.prior.__dict__,'CODE':catalog_source()};exec(compile(raw,'<current strict native transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
