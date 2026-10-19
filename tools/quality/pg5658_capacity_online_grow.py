"""QA052 approved single72→80GiB active-child growth; no deletion, reboot or shrink."""
import inspect
import re
from pyflakes.api import check
import pg4572_capacity_online_grow as previous
from pg2814_network_newboot_readonly import one
from pg4996_resume_connection import authenticate_host
import pg5632_new_current_readonly as current
import pg5656_capacity_current_post as post

SLOT=post.GROW
NEW_SIZE=85899345920


def replace_all(raw,changes):
    pattern='|'.join(re.escape(k)for k in sorted(changes,key=len,reverse=True))
    return re.sub(pattern,lambda match:changes[match.group()],raw)


def lan_payload():
    raw=replace_all(previous.lan_payload(),{
      "old['image']['virtual-size']==60129542144":"old['image']['virtual-size']==77309411328",
      "new['image']['virtual-size']==77309411328":"new['image']['virtual-size']==85899345920",
      "'oldSize':60129542144,'newSize':77309411328":"'oldSize':77309411328,'newSize':85899345920",
      "'size':77309411328":"'size':85899345920",
      "'virtualBytesBefore':60129542144,'virtualBytesAfter':77309411328":"'virtualBytesBefore':77309411328,'virtualBytesAfter':85899345920",
      'PG4572-grow-v1':'PG5658-grow-v1','>=(16+10)*1024**3':'>=(8+10)*1024**3'})
    if check(raw,'<same QEMU72to80>'):raise ValueError('completehoststatic0')
    return raw


def guest_payload():
    raw=replace_all(previous.guest_payload(),{'77309411328':'85899345920','60129542144':'77309411328',
      '115115999':'148670431','33554432':'16777216','PG4432':'PG5598',
      'pg4572-capacity-online-grow-v1':SLOT,
      '/var/lib/pgpt-s1-preservation/pg4570-capacity-current-before-v1/second-full11.private.json':current.AFTER,
      'pg4570-capacity-current-before-v1':'pg5656-capacity-current-before-v1',
      '93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de':current.BOM})
    marker="expected=json.loads(pathlib.Path("+repr(current.AFTER)+").read_bytes())"
    if raw.count(marker)!=1:raise ValueError('one full11 reference')
    raw=raw.replace(marker,"assert hashlib.sha256(pathlib.Path("+repr(current.AFTER)+").read_bytes()).hexdigest()=="+repr(current.context())+'\n'+marker,1)
    if check(raw,'<same guest owned72to80>'):raise ValueError('completegueststatic0')
    return raw


def main():
    authenticate_host()
    # Preserve original coordinated ready/one-QMP/one-partition/one-filesystem protocol.
    raw=inspect.getsource(previous.main)
    raw=raw.replace('pg4570-capacity-current-before-v1','pg5656-capacity-current-before-v1')
    raw=raw.replace("prior['result']['newSourceParentNotStarted']","prior['result']['newRootNotStarted']")
    ns={**vars(previous),'SLOT':SLOT,'NEW_SIZE':NEW_SIZE,'lan_payload':lan_payload,'guest_payload':guest_payload,
      'authenticate_host':authenticate_host,'one':one}
    exec(compile(raw,'<single coordinated approved8GiB growth>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
