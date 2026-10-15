"""Current4856 eligible native joined only to qualified3712/545 all1643 Main."""
import inspect
import json
import subprocess
from pyflakes.api import check
import pg2908_network_current_native_qualification as previous
import pg3412_outbox_fixed_full as whole
from pg3520_outbox_owned_sources_v2 import SOURCE
from pg1446_current_cold_stage import W


def final_namespace(raw):
    for version in ['v1','v2']:
        raw=raw.replace('PG3532-native-input-'+version+'.tar','PG3532-native-input-v3.tar')
        raw=raw.replace('PG3532-native-'+version,'PG3532-native-v3')
        raw=raw.replace('pg3532-outbox-current-native-qualified-'+version,
                        'pg3532-outbox-current-native-qualified-v3')
    return raw


def qualify_snapshot():
    receipt=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes())
    v=receipt['result']
    expected={'actualExit':0,'productionSource':SOURCE,'tests':3712,'suites':545,
              'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0}
    if receipt['actualExit']!=0 or any(type(v.get(k))is not type(x)or v[k]!=x for k,x in expected.items()):
        raise ValueError('actual current3712/545/1643 required')
    whole.validate(v['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',v['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):
        raise ValueError('clean identical current Main/Test/settings required')


def server():
    raw=previous.server()
    for old,new in [('PG2908','PG3532'),('PG2798','PG3412'),('qualified2798Tests','qualified3412Tests'),
                    ('3680','3712'),(previous.SOURCE,SOURCE)]:raw=raw.replace(old,new)
    original="require(sha(p)==qualified['qualificationInputs'][m]['exec']and sha(jar)==qualified['jarHashes'][m]);executions.append(p);jars[m]=jar"
    replacement="require(sha(p)==sha(B/'runs/PG3412-six-v1'/m/'jacoco.exec')and sha(jar)==qualified['jarHashes'][m]);executions.append(p);jars[m]=jar"
    if raw.count(original)!=1:raise ValueError('one actual saved module exec/hash boundary required')
    raw=raw.replace(original,replacement)
    original="qualified['qualificationInputs'][m]['coverageXml']"
    if raw.count(original)!=1:raise ValueError('one actual independent module XML boundary required')
    raw=raw.replace(original,"qualified['modules'][m]['coverageXmlSha256']")
    # No old source exec/member bridge. Each current native is checked against
    # current3712 signed Jar bytes; both physical deltas were independently
    # qualified by3414/3420, and actual VM all187 were independently read3526.
    if previous.SOURCE in raw or 'PG2798' in raw or 'nativeQualifiedFull'in raw:
        raise ValueError('old source native or old member authority leaked')
    raw=final_namespace(raw)
    extractor=previous.prior.previous.entry().__globals__['coordinates']
    complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(extractor)+'\n'+raw
    if check(complete,'<current4856 native3712 complete server>'):raise ValueError('complete server namespace required')
    compile(raw,'<current4856 native3712 server>','exec');return raw


def source():
    raw=previous.source()
    for old,new in [('pg2906-network-current-native-catalog-v1','pg3530-outbox-current-native-catalog-v1'),
                    ('pg2908-network-current-native-qualified-v2','pg3532-outbox-current-native-qualified-v1'),
                    ('pg2800-jdbc-null-fixed-full-qualified-v1','pg3414-outbox-full-qualified-v1'),
                    ('PG2908','PG3532')]:raw=raw.replace(old,new)
    raw=raw.replace('PG3532-native-v2','PG3532-native-v1').replace('PG3532-native-input-v2.tar','PG3532-native-input-v1.tar')
    start=raw.index("    for i,v in enumerate(catalog['selected']):")
    end=raw.index("    root=Path(__file__).parent/",start)
    cached="""    original=W/'pg3532-outbox-current-native-qualified-v1'
    failed=json.loads((original/'manifest.safe.json').read_bytes());saved=json.loads((original/'input.safe.json').read_bytes())
    if failed['actualExit']!=1 or failed['productionSource']!=SOURCE or saved['productionSource']!=SOURCE or saved['selected']!=catalog['selected']:raise ValueError('exact failed beforeCRC same-source input required')
    for i,v in enumerate(catalog['selected']):
        path=original/(str(i)+'.exec');content=path.read_bytes()
        if sha(path)!=v['sha256']or len(content)!=v['bytes']or saved['files'][path.name]!=v['sha256']:raise ValueError('immutable current native cache refused')
        with(out/path.name).open('xb')as f:f.write(content);f.flush();os.fsync(f.fileno())
"""
    raw=raw[:start]+cached+raw[end:]
    raw=final_namespace(raw)
    # final namespace applies only the new target, not the frozen failed input.
    raw=raw.replace("original=W/'pg3532-outbox-current-native-qualified-v3'",
                    "original=W/'pg3532-outbox-current-native-qualified-v1'",1)
    compile(raw,'<current4856 exact native transport>','exec');return raw


def entry():
    ns={**previous.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<current4856 native qualification entry>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
