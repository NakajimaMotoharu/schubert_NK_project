"""Fresh complete failed-current data view; no normal receipt or runtime authority."""
import hashlib
from pyflakes.api import check
import pg3982_literal_invariant_unused_sources as legacy
import pg4434_current_candidate_admission_read as previous
from pg4260_stable_admission_image import execute

SLOT = 'pg4438-failed-current-canonical-view-v1'
PARENT_FIELDS = ('Id', 'LoadState', 'ActiveState', 'SubState', 'MainPID', 'ControlPID', 'Job', 'InvocationID',
                 'ControlGroup', 'Result', 'ExecMainCode', 'ExecMainStatus', 'ExecMainStartTimestampMonotonic',
                 'ExecMainExitTimestampMonotonic', 'Type', 'KillMode', 'SendSIGKILL', 'RemainAfterExit', 'Restart')


CANONICAL = r'''
journal_contract={};exec(JOURNAL_SOURCE,journal_contract)
def canonical_image(value):
 require(len(value)==8 and not value['actors']and not value['database']['peers']and not value['database']['locks']and not value['flocks'])
 units_full={}
 for name in old['units']:
  text=command(['systemctl','show',name,'--property='+','.join(PARENT_FIELDS)],65536).decode('ascii')
  pairs=[line.partition('=')for line in text.splitlines()]
  require(all(sep=='='for _,sep,_ in pairs)and len(pairs)==len(PARENT_FIELDS)and {k for k,_,_ in pairs}==set(PARENT_FIELDS))
  fields_full={k:v for k,_,v in pairs}
  require(all(fields_full[k]==v for k,v in value['units'][name].items()))
  units_full[name]=fields_full
 cfg=config()
 require(declaration_contract['same_configurations'](fixed_config,cfg,CONFIG_CONTRACT['same'],exec_record))
 journal_raw=command(['/usr/bin/journalctl','--boot='+boot.replace('-',''),'_PID=1','UNIT=schubert-nk-morning-controller.service','INVOCATION_ID=bbcdb69957764d489a9c757b441542fd','-o','json','--no-pager'],4194304)
 all_rows=json.loads(journal_contract['project'](journal_raw))
 reduced=[{k:r[k]for k in keys if k in r}for r in all_rows]
 require(reduced==rows)
 parent_contract['classify'](data['source']['commit'],sha,boot,value['units'][parent_contract['UNIT']],reduced,Path('/var/lib/schubert-nk/maintenance/attempts/8314450e-0dd5-4986-875c-81f73e1b50b2.done').read_bytes())
 files={}
 for name,expected in old['unitFilesActual'].items():
  p=Path(name);fields=metadata(p)+[hashlib.sha256(p.read_bytes()).hexdigest()]
  require(metadata(p)==fields[:9]and fields==expected);files[name]=fields
 durable=value['durable']
 result={'units':units_full,'configuration':cfg,'rows':value['database']['rows'],'pid1':all_rows,
   'startup':value['startup'],'originals':durable['originals'],'backup':durable['backup'],
   'extraDurable':{k:durable[k]for k in old['extraDurable']},'unitFilesActual':files,
   'runtime':value['runtime'],'native':value['native']}
 require(len(result)==11 and len(result['rows'])==24)
 return result,journal_raw
'''


def payload():
    raw = previous.payload()
    if hashlib.sha256(raw.encode()).hexdigest() != '5f17f2854524bf649240f605c282d7c27697bf44913ed84e14af8b250b3543e2':
        raise ValueError('actual authenticated failed-current reader bytes required')
    raw = raw.replace(previous.SLOT, SLOT)
    journal = legacy.sources()['pg3982_stable_journal.py']
    marker = 'import dbus\nbus=dbus.SystemBus(private=True)'
    if raw.count(marker) != 1: raise ValueError('one fresh reference acquisition boundary')
    raw = raw.replace(marker, 'JOURNAL_SOURCE=' + repr(journal) + '\nPARENT_FIELDS=' + repr(PARENT_FIELDS) + '\n' + CANONICAL + '\n' + marker, 1)
    marker = "child.stdin.write('CONTINUE\\n');child.stdin.flush();remaining=child.communicate(timeout=20)[0]"
    if raw.count(marker) != 1: raise ValueError('one still-owned final full image boundary')
    extra = """
 full_first,journal_first=canonical_image(post2);full_second,journal_second=canonical_image(snapshot())
 require(full_first==full_second and journal_first==journal_second)
 canonical_sha=save_private('canonical-full11.private.json',full_second)
 before10={k:v for k,v in full_second.items()if k!='native'}
 before10_sha=save_private('canonical-before10.private.json',before10)
 journal_sha=save_private('canonical-journal-raw.private.json',{'hex':journal_second.hex()})
"""
    raw = raw.replace(marker, extra + '\n ' + marker, 1)
    final = "(save/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))"
    raw = raw.replace(final, "value.update(canonicalFull11Sha256=canonical_sha,canonicalBefore10Sha256=before10_sha,canonicalJournalRawSha256=journal_sha,canonicalFields=11,canonicalBeforeFields=10,oldNormalRootImported=False)\n" + final, 1)
    if check(raw, '<complete fresh failed-current canonical image>'): raise ValueError('all emitted static0')
    compile(raw, '<complete fresh failed-current canonical image>', 'exec')
    return raw


def main():
    # Reauthenticate the same current host and forwarding chain before guest read.
    # This is not a replay of previous.main's proof or any recovery action.
    previous.authenticate_host()
    return execute(SLOT, payload(), 220)


if __name__ == '__main__':
    raise SystemExit(main())
