"""SSC256 source-fixed recovery family; no old invocation or file is reused.

Reuse independently tested finite recovery mechanics, bind this source/boot/
original/preserved snapshot exactly. Only the sole live broker can be stopped.
"""
import ast
import inspect
from pathlib import Path
from pg870_ordinary_before import parser_source
import pg1133_fixed_broker_policy as policy

HERE = Path(__file__).resolve().parent
SOURCE = 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'
BOM = '0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'
BASE = '/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/failed-capture-v6/observed.private.json'
BASE_HASH = 'df0b989893adbddd6a539b963c07029222c47e1b557cd572f44fdb8864f1fb01'
BOOT = 'cbca8738-3b24-4090-b77c-bf029677cdd6'


def replace(text, old, new):
    if old not in text: raise ValueError('fixed current recovery source insertion refused')
    return text.replace(old, new)


def common(text):
    for old, new in [('Pg515SingleApiRecovery', 'Pg1134SingleApiRecovery'),
                     ('Pg515IssuedApiRecovery', 'Pg1134IssuedApiRecovery'),
                     ('Pg513SingleApiIntent', 'Pg1134SingleApiIntent'),
                     ('pg515_single_api_refs.py', 'pg1134_single_api_refs.py'),
                     ('pg515_confirm_ma.py', 'pg1134_confirm_ma.py'),
                     ('pg515-issued-api-recovery-v1', 'pg1134-issued-api-recovery-v1'),
                     ('pg515-issued-api-tools-v3', 'pg1134-issued-api-tools-v1'),
                     ('PG515', 'PG1134'),
                     ('cc9ed874-7f4f-450e-a188-8de1e42c8441', BOOT),
                     ('bbb6dc1276a4459da65143db3e4ee3f0', '21f20c0cdbe34ce99431a55b10f92285'),
                     ('5872', '242818'), ('380665', '3465834'), ('38602', '253968'), ('396578', '3477622')]:
        text = text.replace(old, new)
    return text


def java_files():
    result = {}
    names = ['Pg515SingleApiRecovery.java', 'Pg515IssuedApiRecovery.java',
             'Pg515IssuedApiRecoveryTest.java', 'Pg513SingleApiIntent.java', 'Pg513SingleApiIntentTest.java']
    for name in names:
        text = common((HERE / name).read_text())
        name = common(name)
        if name == 'Pg1134SingleApiRecovery.java':
            text = 'import dev.codex.schubert.nk.batch.file.Pg1134SingleApiIntent;\nimport dev.codex.schubert.nk.batch.file.Pg1134IssuedApiRecovery;\n' + text
            text = replace(text, 'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c', SOURCE)
            text = replace(text, 'f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44', BOM)
            text = text.replace('PG495', 'PG1068').replace('pg495', 'pg1068')
            text = replace(text, '91a748b4-1abe-484c-9682-44f46429b324', '343a5a1b-d064-47d5-88c2-31c36d7ba7a4')
            text = replace(text, 'List.of("schubert-nk-expiry-cleanup.service","schubert-nk-cleanup.service","artemis.service")', 'List.of("artemis.service")')
            text = replace(text, 'original24TablesAnd452BatchPreserved', 'original24TablesAnd604BatchPreserved')
        result[name] = text
    return result


def refs_source():
    text = common((HERE / 'pg515_single_api_refs.py').read_text())
    text = replace(text, '/var/lib/pgpt-s1-preservation/pg505-parent-failure-v1/observed.private.json', BASE)
    text = replace(text, 'd60070bd92c13b10b129e2793edb39a2436dad730e3dae6d4d7733c5e5ffd21d', BASE_HASH)
    text = text.replace('0.1.0-PG495', '0.1.0-PG1068')
    text = replace(text, "ORDER=['schubert-nk-expiry-cleanup.service','schubert-nk-cleanup.service','artemis.service']", "ORDER=['artemis.service']")
    start = text.index('def namespace_failure_proof():')
    end = text.index('def cohort():', start)
    text = text[:start] + '''def namespace_failure_proof():
 rows=json.loads(bytes.fromhex(baseline['journals']['schubert-nk-api.service']))
 require(len(rows)==33 and all(r.get('_BOOT_ID')==BOOT.replace('-','')for r in rows))
 failed=[r for r in rows if '/run/schubert-nk/pt-coverage/ordinary-api193' in r.get('MESSAGE','') and 'No such file or directory'in r.get('MESSAGE','')]
 require(len(failed)==5 and all(r.get('_UID')=='0'for r in failed))
 require(sum('Failed at step NAMESPACE'in r.get('MESSAGE','')for r in rows)==5)
 require(not pathlib.Path('/run/schubert-nk/pt-coverage/ordinary-api193').exists())
''' + text[end:]
    text = replace(text, "baseline=json.loads(raw)", "baseline=json.loads(raw);normalize_baseline()")
    text = replace(text, '87a7556e280c58a61d1390d69f5ecde78c430fd807f8a025c401af8bd17dd21e',
                   'c7614d2f61288c2ce330a464030738c0e05e8b50ee388faa9ff9a152323d45f6')
    text = replace(text, "require({u:show(u,configuration_fields()) for u in UNITS}==baseline['configuration'])", '''actual={u:show(u,configuration_fields())for u in UNITS}
 for unit in UNITS:
  if unit=='artemis.service':broker_policy.configuration(baseline['configuration'][unit],actual[unit],baseline['units'][unit],show(unit,FIELDS),exec_record)
  else:require(actual[unit]==baseline['configuration'][unit])
 require({name:tree(pathlib.Path(name))[name]for name in baseline['unitFiles']}==baseline['unitFiles'])''')
    # Existing helper lacks global configuration parser; insert a qualified independent full-field projection.
    extra = '''
def normalize_baseline():
 global FIELDS
 require(set(baseline['units'])==set(UNITS)and len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==604)
 FIELDS=set(baseline['units'][UNITS[0]])
 baseline['trees']={min(v,key=len):v for v in baseline['durable'].values()}
 baseline['trees'][STARTUP]=baseline['startup']
 baseline['trees']['/run/schubert-nk/pt-coverage']=baseline['native']
 baseline['actors']={'artemis.service':{'pid':'253968','invocation':'0f751fba26c94b22ac693a839fced07d','ticks':3477622,
  'argvSha256':'2a7089f6e2bbbbe31a74253fab119bd63b0055019e386c3a6f372a19d6e004b6','cgroup':'0::/system.slice/artemis.service\\n',
  'authority':{'Uid':'994\\t994\\t994\\t994','Gid':'979\\t979\\t979\\t979','Groups':'979',
    'CapInh':'0000000000000000','CapPrm':'0000000000000000','CapEff':'0000000000000000',
    'CapBnd':'0000000000000000','CapAmb':'0000000000000000','NoNewPrivs':'1'}}}
 require(baseline['actor']=={k:baseline['actors']['artemis.service'][k]for k in ['ticks','argvSha256','cgroup']})
'''
    text = text.replace('import dbus', 'import dbus,re,types\nbroker_policy=types.ModuleType("fixed-broker-policy")\nexec(' + repr(inspect.getsource(policy)) + ',broker_policy.__dict__)\n' + parser_source() + extra)
    ast.parse(text); return text


def files():
    result = java_files()
    result['pg1134_single_api_refs.py'] = refs_source()
    result['pg1134_confirm_ma.py'] = common((HERE / 'pg515_confirm_ma.py').read_text())
    for name, text in result.items():
        if name.endswith('.py'): ast.parse(text)
    return result
