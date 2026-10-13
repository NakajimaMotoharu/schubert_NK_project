"""Qualified current nine streams reused against fresh full3649; no VM recapture or actions."""
import json
import subprocess
import pg2468_question_current_native_qualification as prior
from pg2494_current_boundary_full_six import SOURCE, validate
from pg1446_current_cold_stage import W
from pyflakes.api import check


def qualify_snapshot():
    m = json.loads((W / 'pg2495-current-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    f = m['result']
    if m['actualExit'] != 0 or any(f.get(k) != v for k, v in {'productionSource': SOURCE,
            'tests': 3649, 'suites': 540, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}.items()):
        raise ValueError('actual fresh whole3649/540/1643/static6 required')
    validate(f['sourceSnapshot'])
    if subprocess.check_output(['git', 'status', '--porcelain']) or subprocess.check_output(['git', 'diff', '--name-only', f['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', 'mvnw', '.mvn', 'program/characterization']):
        raise ValueError('fixed unchanged current production and test inputs required')


def server():
    raw = prior.server().replace('PG2468', 'PG2500').replace('PG2404', 'PG2494').replace('qualified2404Tests', 'qualified2494Tests').replace('3637', '3649')
    old = json.loads((W / 'pg2405-question-jdbc-full-qualified-v1/manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['result']['productionSource'] != SOURCE:
        raise ValueError('actual original Main artifact authority required')
    marker = "J=B/'tools/jdk-25.0.4/bin';repo=B/'m2/repository';libs=[]"
    bridge = """import zipfile
identical_main=0
for module,old_hash in OLD_JARS.items():
 old=B/'source-full-PG2404/src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
 new=B/'source-full-PG2494/src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
 require(sha(old)==old_hash and sha(new)==qualified['jarHashes'][module])
 images=[]
 for path in [old,new]:
  with zipfile.ZipFile(path)as archive:
   require(len(archive.namelist())==len(set(archive.namelist())))
   images.append({n:hashlib.sha256(archive.read(n)).hexdigest()for n in archive.namelist()})
 require(images[0]==images[1]);identical_main+=sum(n.endswith('.class')for n in images[1])
require(identical_main==1643)
"""
    if raw.count(marker) != 1:
        raise ValueError('single full/Main bridge boundary required')
    raw = 'OLD_JARS=' + repr(old['result']['jarHashes']) + '\n' + raw.replace(marker, bridge + marker)
    raw = raw.replace("'sourceChanged0':True", "'sourceChanged0':True,'all1643MainMembersIdentical':identical_main,'allProductionResourceMembersIdentical':True,'jarWrapperHashesDifferButMembersIdentical':True,'retainedQualifiedNativeReused':True")
    if check('ARCHIVE_SHA=""\ncoordinates=lambda a,b:{}\n' + raw, '<PG2500 actual full native bridge>'):
        raise ValueError('actual bridge namespace required')
    compile(raw, '<PG2500 same production full native>', 'exec')
    return raw


def source():
    raw = prior.source().replace('PG2468', 'PG2500').replace('pg2468-question-current-native-qualified-v1', 'pg2500-current-boundary-native-qualified-v1').replace('pg2405-question-jdbc-full-qualified-v1', 'pg2495-current-boundary-full-qualified-v1')
    begin = raw.index("    for i,v in enumerate(catalog['selected']):")
    end = raw.index("    root=Path(__file__).parent", begin)
    raw = raw[:begin] + """    previous=W/'pg2474-question-current-native-qualified-v1'
    authority=json.loads((previous/'manifest.safe.json').read_bytes())
    inputs=json.loads((previous/'input.safe.json').read_bytes())
    if authority['actualExit']!=0 or authority['productionSource']!=SOURCE or inputs['selected']!=catalog['selected'] or authority['result']['currentNativeStreams']!=9 or authority['result']['classByteMismatch']!=0:
        raise ValueError('existing current native authority and exact catalog required')
    for i,v in enumerate(catalog['selected']):
        old=previous/(str(i)+'.exec');path=out/(str(i)+'.exec')
        if sha(old)!=v['sha256']or old.stat().st_size!=v['bytes']:
            raise ValueError('retained immutable native bytes required')
        with path.open('xb')as f:f.write(old.read_bytes());f.flush();os.fsync(f.fileno())
""" + raw[end:]
    if "SSH+" in raw:
        raise ValueError('no VM/native recapture allowed')
    compile(raw, '<PG2500 retained bytes only>', 'exec')
    return raw


def entry():
    namespace = {**prior.entry().__globals__, 'CODE': server(), 'SOURCE': SOURCE, 'qualify_snapshot': qualify_snapshot}
    exec(compile(source(), '<PG2500 immutable full bridge transport>', 'exec'), namespace)
    return namespace['main']


if __name__ == '__main__':
    raise SystemExit(entry()())
