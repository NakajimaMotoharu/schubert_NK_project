"""Newsource latest nine/current CRCs from own campaign/full3666; no oldexec bridge."""
import inspect
import json
import subprocess
from pathlib import Path
import pg2564_strict_current_native_qualification as previous
from pg2694_expiry_fixed_full_six import validate,SOURCE
from pg1446_current_cold_stage import W

ARTIFACT='program/characterization/reports/nk/PG2720-native-a01-v1/artifacts/CHR-A01.json'


def result_changes(changes,artifact,baseline,receipt):
    ns={**previous.previous.__dict__,'ARTIFACT':ARTIFACT,'SOURCE':SOURCE}
    exec(compile(inspect.getsource(previous.previous.result_changes),'<new A01 result only independent qualifier>','exec'),ns)
    return ns['result_changes'](changes,artifact,baseline,receipt)


def qualify_snapshot():
    outer=json.loads((W/'pg2695-expiry-fixed-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(outer.get('actualExit'))is not int or outer['actualExit']!=0:raise ValueError('actual new full source authority required')
    full=outer['result'];expected={'productionSource':SOURCE,'tests':3666,'suites':541,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0}
    if any(type(full.get(k))is not type(v)or full[k]!=v for k,v in expected.items()):raise ValueError('exact new full3666/541/1643/static6 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean actual new result/input qualification required')
    changes=subprocess.check_output(['git','diff','--name-only',full['sourceSnapshot'],'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization'],text=True).splitlines()
    if changes:result_changes(changes,Path(ARTIFACT).read_bytes(),Path(previous.previous.BASELINE).read_bytes(),json.loads((W/'pg2720-chr-a01-native-v1.safe.json').read_bytes()))


def server():
    raw=previous.server().replace('PG2564','PG2722').replace('PG2510','PG2694').replace('qualified2510Tests','qualified2694Tests').replace('3650','3666').replace(previous.SOURCE,SOURCE)
    compile(raw,'<newsource own native streams all1643 CRC/session>','exec');return raw


def source():
    raw=previous.source().replace('pg2562-strict-current-native-catalog-v1','pg2718-operation-native-catalog-v1').replace('pg2564-strict-current-native-qualified-v1','pg2722-operation-native-qualified-v1').replace('PG2564','PG2722').replace('pg2511-strict-reference-full-qualified-v1','pg2695-expiry-fixed-full-qualified-v1')
    compile(raw,'<newsource actual native transport>','exec');return raw


def entry():
    ns={**previous.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<actual new candidate native full3666 qualifier>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
