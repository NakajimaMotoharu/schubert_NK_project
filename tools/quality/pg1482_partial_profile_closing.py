"""Separate full readonly closing of normal Java profile, failed collector1 preserved."""
import inspect
import json
from pathlib import Path
import pg1477_publication_observation_retry as previous
from pg1481_partial_original_profile import valid_receipt

EXTRA=r'''
ROOT=pathlib.Path('/run/schubert-nk')
profile_save=BASE/'pg1481-partial-original-profile-v1'
after_raw=(profile_save/'after.private.json').read_bytes()
require(hashlib.sha256(after_raw).hexdigest()=='c0df5b18f50bd5ecf4ad83ca1ad1c378036fcd4b4eb1cc4874c1124825583de0')
profile_after=json.loads(after_raw);require(profile_after['mutation0'] is True)
require(profile_after['parent']['pid']==90821 and profile_after['parent']['ticks']==1162010 and not pathlib.Path('/proc/90821').exists())
require((profile_save/'complete.private').read_bytes()==b'allScopesReturnedNormally=true\nreadonlyProfile=true\nepochDbBusinessWrites=0\n')
timing_raw=(profile_save/'original-profile.safe.jsonl').read_bytes();require(hashlib.sha256(timing_raw).hexdigest()=='613947cf8195d50c93a5d4a9eee860f2f55718f1622ecacf1b6f7abe3b10b615')
timings=[json.loads(line)for line in timing_raw.splitlines()]
require(len(timings)==4 and all(set(t)=={'twoWholeGraphObservationsNanos','completed'} and type(t['twoWholeGraphObservationsNanos'])is int and t['twoWholeGraphObservationsNanos']>=0 and t['completed'] is False for t in timings))
for path,expected in profile_after['parent']['locks'].items():
 require(metadata(ROOT/path)==expected)
 for line in pathlib.Path('/proc/locks').read_text().splitlines():
  fields=line.split()
  if len(fields)==8 and fields[1]=='FLOCK':
   major,minor,ino=fields[5].split(':')
   require((int(major,16),int(minor,16),int(ino))!=(os.major(expected[0]),os.minor(expected[0]),expected[1]))
'''


def payload():
    raw=previous.payload().replace('pg1477-failed-publication-owner-v1','pg1482-partial-profile-closing-v1').replace('PG1477-failed-publication-owner-v1','PG1482-partial-profile-closing-v1')
    marker='bus=dbus.SystemBus(private=True);'
    assert raw.count(marker)==1
    raw=raw.replace(marker,EXTRA+'\n'+marker)
    marker="first=snapshot();second=snapshot()"
    assert raw.count(marker)==1
    raw=raw.replace(marker,marker+"\n first['brokerActor'].pop('statusSha256');second['brokerActor'].pop('statusSha256');require(first==second==profile_after['current'])")
    # Previous transport also pops this volatile diagnostic; don't repeat it.
    raw=raw.replace("first['brokerActor'].pop('statusSha256');second['brokerActor'].pop('statusSha256');require(first==second)\nfinally:","require(first==second)\nfinally:")
    compile(raw,'<independent partial profile fullclosing>','exec');return raw


def main():
    w=previous.previous.previous.W
    manifest=json.loads((w/'pg1481-partial-original-profile-v1/manifest.safe.json').read_bytes())
    assert manifest['actualExit']==1 and manifest['sshExit']==0
    assert valid_receipt((w/'pg1481-partial-original-profile-v1/profile.private.log').read_bytes())
    original=previous.previous.previous
    entry=inspect.getsource(original.main).replace('pg1464-failed-current-capture-v1','pg1482-partial-profile-closing-v1')
    ns={**original.__dict__,'payload':payload}
    exec(compile(entry,'<new-only readonly closing transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
