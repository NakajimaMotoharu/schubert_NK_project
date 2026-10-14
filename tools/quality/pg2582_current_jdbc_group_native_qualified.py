"""Current latest-nine CRC/session evidence joined to fresh full3653; no VM replay."""
import json
import subprocess
from pyflakes.api import check
import pg2564_strict_current_native_qualification as previous
from pg2578_current_jdbc_group_full_six import SOURCE, validate
from pg1446_current_cold_stage import W


def qualify_snapshot():
    outer = json.loads((W / 'pg2579-current-jdbc-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(outer.get('actualExit')) is not int or outer['actualExit'] != 0:
        raise ValueError('actual independently qualified grouped full required')
    full = outer['result']
    expected = {'productionSource': SOURCE, 'tests': 3653, 'suites': 540, 'mainClasses': 1643,
                'FESFlakyNotRun': 0, 'staticSixModules': 0}
    if any(type(full.get(k)) is not type(v) or full[k] != v for k, v in expected.items()):
        raise ValueError('exact fresh3653/540/1643/static6 required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(
        ['git', 'diff', '--name-only', full['sourceSnapshot'], 'HEAD', '--',
         'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('clean whole grouped snapshot inputs required')


def server():
    raw = previous.server().replace('PG2564', 'PG2582').replace('PG2510', 'PG2578').replace(
        'qualified2510Tests', 'qualified2578Tests').replace('3650', '3653')
    old = json.loads((W / 'pg2511-strict-reference-full-qualified-v1/manifest.safe.json').read_bytes())
    if type(old.get('actualExit')) is not int or old['actualExit'] != 0 or old['result']['productionSource'] != SOURCE:
        raise ValueError('actual original current Main full authority required')
    marker = "J=B/'tools/jdk-25.0.4/bin';repo=B/'m2/repository';libs=[]"
    if raw.count(marker) != 1:
        raise ValueError('one whole Main byte bridge required')
    bridge = """import zipfile
identical_main=0
for module,old_hash in OLD_JARS.items():
 old=B/'source-full-PG2510/src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
 new=B/'source-full-PG2578/src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
 require(sha(old)==old_hash and sha(new)==qualified['jarHashes'][module])
 images=[]
 for path in [old,new]:
  with zipfile.ZipFile(path)as archive:
   require(len(archive.namelist())==len(set(archive.namelist())))
   images.append({n:hashlib.sha256(archive.read(n)).hexdigest()for n in archive.namelist()})
 require(images[0]==images[1]);identical_main+=sum(n.endswith('.class')for n in images[1])
require(identical_main==1643)
"""
    raw = 'OLD_JARS=' + repr(old['result']['jarHashes']) + '\n' + raw.replace(marker, bridge + marker)
    raw = raw.replace("'sourceChanged0':True", "'sourceChanged0':True,'all1643MainMembersIdentical':identical_main,'allProductionResourceMembersIdentical':True,'retainedQualifiedNativeReused':True")
    if check('ARCHIVE_SHA=""\ncoordinates=lambda a,b:{}\n' + raw, '<current grouped whole bridge>'):
        raise ValueError('whole bridge namespace required')
    compile(raw, '<same current native full3653 CRC/session qualifier>', 'exec')
    return raw


def source():
    raw = previous.source().replace('pg2564-strict-current-native-qualified-v1',
        'pg2582-current-jdbc-group-native-qualified-v1').replace('PG2564', 'PG2582').replace(
        'pg2511-strict-reference-full-qualified-v1', 'pg2579-current-jdbc-group-full-qualified-v1')
    begin = raw.index("    for i,v in enumerate(catalog['selected']):")
    end = raw.index("    root=Path(__file__).parent", begin)
    raw = raw[:begin] + """    previous=W/'pg2564-strict-current-native-qualified-v1'
    authority=json.loads((previous/'manifest.safe.json').read_bytes())
    inputs=json.loads((previous/'input.safe.json').read_bytes())
    if authority['actualExit']!=0 or authority['productionSource']!=SOURCE or inputs['selected']!=catalog['selected'] or authority['result']['currentNativeStreams']!=9 or authority['result']['classByteMismatch']!=0:
        raise ValueError('qualified current native and exact catalog required')
    for i,v in enumerate(catalog['selected']):
        old=previous/(str(i)+'.exec');path=out/(str(i)+'.exec')
        if sha(old)!=v['sha256']or old.stat().st_size!=v['bytes']:
            raise ValueError('immutable retained current native bytes required')
        with path.open('xb')as f:f.write(old.read_bytes());f.flush();os.fsync(f.fileno())
""" + raw[end:]
    if 'SSH+' in raw:
        raise ValueError('no VM recapture permitted')
    compile(raw, '<grouped full current native transport>', 'exec')
    return raw


def entry():
    ns = {**previous.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE,
          'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<current native exact grouped snapshot>', 'exec'), ns)
    return ns['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
