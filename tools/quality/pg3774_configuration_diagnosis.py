"""Read only exact current config field differences; no placement/readback replay or state repair."""
import hashlib
import json
import os
import subprocess
import sys
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg3766_hygiene_unused_sources_v2 as role


def main():
    if sys.argv[1:]not in [[],['--held']]:raise ValueError('original or separate held-reference diagnosis only')
    held=bool(sys.argv[1:])
    post=json.loads((W/'pg3772-hygiene-unused-post-v1/manifest.safe.json').read_bytes());assert post['actualExit']==1;capture=(W/role.TOOLS/'pg3766_configuration_capture.py').read_text();pins=json.loads((W/'pg3768-frozen-v1.safe.json').read_bytes())['fileHashes'];assert hashlib.sha256(capture.encode()).hexdigest()==pins['pg3766_configuration_capture.py'];os.umask(0o077);out=W/('pg3776-configuration-held-before-v1'if held else 'pg3774-configuration-before-v1');out.mkdir()
    raw='import json,hashlib,subprocess\nfrom pathlib import Path\n'+capture+'\n'+r'''
p=Path('/var/lib/pgpt-s1-preservation/pg3662-native-stop-v1/after.private.json');contents=p.read_bytes();assert hashlib.sha256(contents).hexdigest()=='35f5e07742c6869789f176a3338e9564e2a867039849a6c9230fc4b8147c7317';old=json.loads(contents)['configuration'];values=[]
for unit,expected in old.items():
 r=subprocess.run(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))],capture_output=True,text=True,timeout=10);assert r.returncode==0;actual=complete_configuration(r.stdout,unit)
 fields=[k for k in expected if actual.get(k)!=expected[k]]
 if fields:values.append({'unit':unit,'fields':[{'name':k,'before':expected[k],'after':actual.get(k)}for k in fields]})
print(json.dumps({'actualExit':0,'unitsChecked':len(old),'configurationDifferences':values,'stateActions':0,'dbWrites':0,'formalAccepted':False}))
'''
    if held:
        start=raw.index('for unit,expected in old.items():');end=raw.index("print(json.dumps(",start);body=raw[start:end]
        scope="import dbus\nbus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager');refs=[]\ntry:\n for unit in old:manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)\n"
        raw=raw[:start]+scope+'\n'.join(' '+line if line else line for line in body.splitlines())+'\nfinally:\n try:\n  for unit in reversed(refs):manager.UnrefUnit(unit)\n finally:bus.close()\n'+raw[end:]
        raw=raw.replace("'unitsChecked':len(old)","'unitsChecked':len(old),'newTenReferencesReturnedNormally':len(refs)==10")
    (out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stdout.safe.json').write_bytes(r.stdout);(out/'stderr.private.log').write_bytes(r.stderr);v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:v['result']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps(v));return r.returncode


if __name__=='__main__':raise SystemExit(main())
