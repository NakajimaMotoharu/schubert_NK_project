"""QA052: one online active child56→72GiB, same guest/QEMU, all backing read-only."""
import inspect
from pyflakes.api import check
import pg2012_online_capacity_grow as runner
import pg2868_network_online_capacity_grow as previous
from pg2814_network_newboot_readonly import one
from pg4434_current_candidate_admission_read import authenticate_host

SLOT='pg4572-capacity-online-grow-v1'
NEW_SIZE=77309411328


def lan_payload():
    raw=previous.lan_payload().replace('PG2868-grow-v1','PG4572-grow-v1')
    for old,new in [
        ("old['image']['virtual-size']==51539607552","old['image']['virtual-size']==60129542144"),
        ("new['image']['virtual-size']==60129542144","new['image']['virtual-size']==77309411328"),
        ("'oldSize':51539607552,'newSize':60129542144","'oldSize':60129542144,'newSize':77309411328"),
        ("{'device':'virtio0','size':60129542144}","{'node-name':old['node-name'],'size':77309411328}"),
        ("'virtualBytesBefore':51539607552,'virtualBytesAfter':60129542144","'virtualBytesBefore':60129542144,'virtualBytesAfter':77309411328")]:
        raw=one(raw,old,new)
    raw=one(raw,'>=20*1024**3','>=(16+10)*1024**3')
    raw=one(raw,"persist('before.private.json',", "assert old['node-name']=='#block113'\npersist('before.private.json',")
    if check(raw,'<same QEMU online active56to72>'):raise ValueError('host payload static0')
    return raw


def guest_payload():
    raw=runner.GUEST
    for old,new in [('51539607552','77309411328'),('42949672960','60129542144'),('81561567','115115999'),('16777216','33554432'),
        ('3d69f5af-6bac-46b1-a540-7591c4a79a0d',previous.BOOT),('PG1846','PG4432'),('pg2012-online-grow-v1',SLOT)]:raw=raw.replace(old,new)
    raw=one(raw,'import fcntl,json,os,pathlib,stat,subprocess,sys,time','import dbus,fcntl,hashlib,json,os,pathlib,stat,subprocess,sys,time')
    raw=one(raw,'held=[]\ntry:',"""expected=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg4570-capacity-current-before-v1/second-full11.private.json').read_bytes())
assert len(expected)==11 and len(expected['units'])==10
assert hashlib.sha256(pathlib.Path('/opt/schubert-nk/current/RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de'
bus=dbus.SystemBus(private=True);manager=dbus.Interface(bus.get_object('org.freedesktop.systemd1','/org/freedesktop/systemd1'),'org.freedesktop.systemd1.Manager')
held=[];refs=[]
try:"""
    )
    raw=one(raw,' quiescent()\n before=table();',""" for unit in sorted(expected['units']):manager.LoadUnit(unit);manager.RefUnit(unit);refs.append(unit)
 assert len(refs)==10
 quiescent()
 before=table();"""
    )
    raw=one(raw," persist('partition-before.private.json',before)",""" saved=json.loads(pathlib.Path('/var/lib/pgpt-s1-preservation/pg4570-capacity-current-before-v1/partition-observed.private.json').read_bytes())
 assert before==saved
 assert subprocess.check_output(['/usr/sbin/blkid','-s','UUID','-o','value','/dev/vda1'],text=True).strip()=='92978eec-7925-481e-8629-5b963d59ced1'
 persist('partition-before.private.json',before)"""
    )
    raw=one(raw,' for fd in reversed(held):os.close(fd)'," for unit in reversed(refs):manager.UnrefUnit(unit)\n bus.close()\n for fd in reversed(held):os.close(fd)")
    raw=one(raw," print(json.dumps({'actualExit':0,", " result={'actualExit':0,")
    raw=one(raw,"'privateRoot':str(root)}))", "'privateRoot':str(root)}")
    raw+='\nprint(json.dumps(result))\n'
    if check(raw,'<owned same guest online partition filesystem grow>'):raise ValueError('guest payload static0')
    return raw


def main():
    authenticate_host()
    raw=inspect.getsource(runner.main)
    raw=one(raw,"W/'pg2006-existing-runtime-independent-post-v1/manifest.safe.json'","W/'pg4570-capacity-current-before-v1/manifest.safe.json'")
    raw=one(raw,"prior['actualExit']!=0 or prior['allClientAdvisoryFlock0']is not True","prior['actualExit']!=0 or prior['result']['allClientAdvisoryFlock0']is not True or prior['result']['newSourceParentNotStarted']is not True")
    # Persist the exact generated programs before either side can reserve a mutation.
    raw=one(raw,"guest_output=b''", "(out/'host-payload.private.py').write_text(LAN);(out/'guest-payload.private.py').write_text(GUEST)\n    guest_output=b''")
    ns={**vars(runner),'SLOT':SLOT,'LAN':lan_payload(),'GUEST':guest_payload(),'NEW_SIZE':NEW_SIZE}
    exec(compile(raw,'<one current capacity grow dispatcher>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
