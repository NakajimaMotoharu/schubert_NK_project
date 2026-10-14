"""Reuse sealed a9 native bytes only after all1643 Main/resource members match new Test full."""
import inspect
import json
import subprocess
from pyflakes.api import check
import pg2908_network_current_native_qualification as prior
from pg2918_db_failure_group_full_six import SOURCE,validate,prior as full_prior


def member_counts(old,new):
    if type(old)is not dict or type(new)is not dict or not old or old!=new:
        raise ValueError('every Main/resource/META byte must match the same a9 source')
    if any(type(k)is not str or type(v)is not bytes for k,v in old.items()):
        raise ValueError('literal member byte maps required')
    classes=sum(k.endswith('.class')for k in old)
    return classes,len(old)-classes


def qualify_snapshot():
    value=json.loads((prior.W/'pg2920-db-failure-group-full-qualified-v1/manifest.safe.json').read_bytes())
    full=value['result']
    expected={'productionSource':SOURCE,'tests':3684,'suites':542,'mainClasses':1643,'FESFlakyNotRun':0,'staticSixModules':0}
    if value.get('actualExit')!=0 or any(type(full.get(k))is not type(v)or full[k]!=v for k,v in expected.items()):
        raise ValueError('actual full3684 current source required')
    validate(full['sourceSnapshot'])
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff',full['sourceSnapshot'],'HEAD','--',*full_prior.SCOPE]):
        raise ValueError('clean exact new full scope required')


def server():
    raw=prior.server().replace('PG2798','PG2918').replace('qualified2798Tests','qualified2918Tests').replace('3680','3684').replace('PG2908','PG2922').replace('PG2922-native-v2','PG2922-native-v1').replace('PG2922-native-input-v2.tar','PG2922-native-input-v1.tar')
    marker="local={};host={};union={};gain={};xml_hashes={};gaps={};start="
    if raw.count(marker)!=1:raise ValueError('one whole-member qualification boundary required')
    extra=inspect.getsource(member_counts)+"\n"+"""import zipfile
baseline=v['nativeQualifiedFull'];identical_main=0;identical_resources=0
require(baseline['productionSource']==v['productionSource']and baseline['mainClasses']==1643)
for module in modules:
 oldjar=B/'source-full-PG2798/src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
 require(sha(oldjar)==baseline['jarHashes'][module])
 with zipfile.ZipFile(oldjar)as old,zipfile.ZipFile(jars[module])as new:
  oldnames=[n for n in old.namelist()if not n.endswith('/')];newnames=[n for n in new.namelist()if not n.endswith('/')]
  require(len(oldnames)==len(set(oldnames))and len(newnames)==len(set(newnames)))
  oldmembers={n:old.read(n)for n in old.namelist()if not n.endswith('/')}
  newmembers={n:new.read(n)for n in new.namelist()if not n.endswith('/')}
  main_count,resource_count=member_counts(oldmembers,newmembers)
  identical_main+=main_count
  identical_resources+=resource_count
require(identical_main==1643)
"""
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("'sourceChanged0':True","'sourceChanged0':True,'all1643MainMembersIdentical':identical_main,'allResourceMetaMembersIdentical':identical_resources,'sameA9NativeRetainedOnly':True")
    extractor=prior.prior.previous.entry().__globals__['coordinates']
    prefix='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="a"\n'
    if check(prefix+inspect.getsource(extractor)+'\n'+raw,'<same native new Test full complete server>'):raise ValueError('assembled namespace required')
    compile(raw,'<all members and actual CRC sessions>','exec');return raw


def source():
    raw=prior.source().replace('pg2908-network-current-native-qualified-v2','pg2922-same-a9-native-qualified-v1').replace('pg2800-jdbc-null-fixed-full-qualified-v1','pg2920-db-failure-group-full-qualified-v1').replace('PG2908','PG2922').replace('PG2922-native-input-v2.tar','PG2922-native-input-v1.tar')
    start=raw.index("    for i,v in enumerate(catalog['selected']):")
    end=raw.index("    root=Path(__file__)",start)
    cached="""    previous_out=W/'pg2908-network-current-native-qualified-v2'
    original=json.loads((previous_out/'manifest.safe.json').read_bytes())
    if original.get('actualExit')!=0 or original.get('productionSource')!=SOURCE or original['result']['classByteMismatch']!=0:raise ValueError('actual sealed same a9 native qualification required')
    native_input=json.loads((previous_out/'input.safe.json').read_bytes())
    if native_input['selected']!=catalog['selected']or native_input['productionSource']!=SOURCE:raise ValueError('exact immutable catalog/bytes required')
    for i,v in enumerate(catalog['selected']):
        cached=previous_out/(str(i)+'.exec');data=cached.read_bytes()
        if sha(cached)!=v['sha256']or len(data)!=v['bytes']:raise ValueError('sealed native CRC/session capsule changed')
        with (out/cached.name).open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
"""
    raw=raw[:start]+cached+raw[end:]
    marker="data['libraries']=libs"
    if raw.count(marker)!=1:raise ValueError('one input qualification authority required')
    raw=raw.replace(marker,marker+";data['nativeQualifiedFull']=native_input['qualifiedFull']")
    compile(raw,'<same a9 cached native without guest read/replay>','exec');return raw


def entry():
    ns={**prior.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':qualify_snapshot}
    exec(compile(source(),'<same a9 native rejoin actual>','exec'),ns);return ns['main']


if __name__=='__main__':raise SystemExit(entry()())
