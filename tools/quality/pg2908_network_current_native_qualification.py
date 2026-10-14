"""Newa9 actual latest-nine/all1643 CRC/session + same3680 host input, zero old source import."""
import inspect
import json
import subprocess
from pathlib import Path
import pg2722_operation_native_qualification as prior
import pg2474_question_native_qualified_results as result_guard
from pg2798_jdbc_null_fixed_full_six import SOURCE,validate
from pg1446_current_cold_stage import W

ARTIFACT='program/characterization/reports/nk/PG2900-native-a01-v1/artifacts/CHR-A01.json'


def qualify_snapshot():
    v=json.loads((W/'pg2800-jdbc-null-fixed-full-qualified-v1/manifest.safe.json').read_bytes())
    if v.get('actualExit')!=0:raise ValueError('same3680 actual full required')
    f=v['result'];expected={'productionSource':SOURCE,'tests':3680,'suites':542,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0}
    if any(type(f.get(k))is not type(x)or f[k]!=x for k,x in expected.items()):raise ValueError('exact new3680/542/1643/static6 required')
    validate(f['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean same input and explicitly sanitized result required')
    changes=subprocess.check_output(['git','diff','--name-only',f['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],text=True).splitlines()
    ns={**result_guard.__dict__,'ARTIFACT':ARTIFACT,'SOURCE':SOURCE}
    exec(compile(inspect.getsource(result_guard.result_changes),'<explicit independent real current A01 result>','exec'),ns)
    ns['result_changes'](changes,Path(ARTIFACT).read_bytes(),Path(result_guard.BASELINE).read_bytes(),json.loads((W/'pg2900-chr-a01-native-v1.safe.json').read_bytes()))


def server():
    raw=prior.server().replace('PG2722','PG2908').replace('PG2694','PG2798').replace('qualified2694Tests','qualified2798Tests').replace('3666','3680')
    raw=raw.replace(prior.SOURCE,SOURCE)
    raw=raw.replace('PG2908-native-v1','PG2908-native-v2').replace('PG2908-native-input.tar','PG2908-native-input-v2.tar')
    from pyflakes.api import check
    # Transport supplies exact archive SHA and its independently qualified XML
    # coordinate extractor; validate that complete assembled server, not a stub.
    extractor=prior.previous.entry().__globals__['coordinates']
    complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(extractor)+'\n'+raw
    if check(complete,'<whole a9 1643 CRC actual streams server>'):raise ValueError('complete current native server namespace required')
    compile(raw,'<only current source native stream/CRC/session/dominance>','exec');return raw


def source():
    raw=prior.source()
    for a,b in [('pg2718-operation-native-catalog-v1','pg2906-network-current-native-catalog-v1'),
        ('pg2722-operation-native-qualified-v1','pg2908-network-current-native-qualified-v2'),('PG2722','PG2908'),
        ('pg2695-expiry-fixed-full-qualified-v1','pg2800-jdbc-null-fixed-full-qualified-v1')]:raw=raw.replace(a,b)
    raw=raw.replace('PG2908-native-v1','PG2908-native-v2').replace('PG2908-native-input.tar','PG2908-native-input-v2.tar')
    compile(raw,'<actual newa9 native transport>','exec');return raw


def entry():
    ns={**prior.previous.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<same newa9 actual native qualification>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
