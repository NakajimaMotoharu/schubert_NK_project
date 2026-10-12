"""BUG1179: current Root13 nine streams; explicit earlier Inspector point excluded."""
import inspect
from pg1839_warning_current_native_catalog import catalog_source as previous,main as previous_main
import pg1839_warning_current_native_catalog as engine

SLOT='pg1840-warning-inspector-native-catalog-v1'


def inspector_window(rows):
    if type(rows)is not list or not rows:raise ValueError('actual sameRoot Inspector journal required')
    fixed={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-inbox-inspector.service','INVOCATION_ID':'6c5bf1041fdf45d992dd2b58afd7df09'}
    cursors=set()
    for row in rows:
        if type(row)is not dict or any(row.get(k)!=v for k,v in fixed.items()):raise ValueError('fixed Inspector generation required')
        stamp=row.get('__MONOTONIC_TIMESTAMP');cursor=row.get('__CURSOR')
        if type(stamp)is not str or not stamp.isdecimal()or not 81404764713<=int(stamp)<=83018953880:raise ValueError('original Root13 window required')
        if type(cursor)is not str or not cursor or cursor in cursors:raise ValueError('unique actual cursor required')
        cursors.add(cursor)
        if row.get('JOB_RESULT')not in (None,'done'):raise ValueError('Inspector must genuinely finish normally')
    groups=[[(r)for r in rows if r.get('MESSAGE_ID')==message and all(r.get(k)==v for k,v in extra.items())]for message,extra in [
        ('7d4958e842da4a758f6c1cdc7b36dcc5',{'JOB_ID':'127856','JOB_TYPE':'start'}),
        ('39f53479d3a045ac8e11786248231fbf',{'JOB_ID':'127856','JOB_TYPE':'start','JOB_RESULT':'done'}),
        ('7ad2d189f7e94e70a38c781354912448',{}),
        ('9d1aaa27d60140bd96365438aad20286',{'JOB_ID':'128003','JOB_TYPE':'stop','JOB_RESULT':'done'})]]
    if any(len(g)!=1 for g in groups):raise ValueError('four exact normal Inspector events required')
    times=[int(g[0]['__MONOTONIC_TIMESTAMP'])for g in groups]
    if times!=[81623098577,81634285835,81635354035,81635354860]:raise ValueError('exact observed generation window required')
    return times[0],times[2]


def catalog_source(receipt):
    raw=previous(receipt)
    marker="for relative,unit in names:"
    extra="""inspector_raw=subprocess.check_output(['journalctl','--boot=3d69f5af6bac46b1a5407591c4a79a0d','_PID=1','UNIT=schubert-nk-inbox-inspector.service','-o','json','--no-pager'],timeout=20)
inspector_rows=[json.loads(l)for l in inspector_raw.splitlines()];inspector_rows=[r for r in inspector_rows if r.get('INVOCATION_ID')=='6c5bf1041fdf45d992dd2b58afd7df09']
inspector_start,inspector_end=inspector_window(inspector_rows)
closing='ordinary-inspector196/6c5bf1041fdf45d992dd2b58afd7df09.closing.exec'
earlier='ordinary-inspector196/6c5bf1041fdf45d992dd2b58afd7df09.terminal.exec'
require(closing not in old and earlier not in old)
names.append((closing,'schubert-nk-inbox-inspector.service'))
"""
    if raw.count(marker)!=1:raise ValueError('one actual stream enumeration boundary required')
    raw=raw.replace(marker,extra+marker)
    raw=raw.replace("if unit=='schubert-nk-backup.service':start=backup_start;end=backup_end","if unit=='schubert-nk-inbox-inspector.service':start=inspector_start;end=inspector_end\n elif unit=='schubert-nk-backup.service':start=backup_start;end=backup_end")
    raw=raw.replace("require(len(selected)==8 and len({v['relative']for v in selected})==8)","require(len(selected)==9 and len({v['relative']for v in selected})==9)\nclosing_item=next(v for v in selected if v['relative']==closing)\nearlier_file=native/earlier;early_stat=earlier_file.lstat();require(stat.S_ISREG(early_stat.st_mode)and early_stat.st_nlink==1 and early_stat.st_size==closing_item['bytes'])\nearly_bytes=earlier_file.read_bytes();require(meta(early_stat)==meta(earlier_file.lstat())and hashlib.sha256(early_bytes).hexdigest()==closing_item['sha256'])")
    raw=raw.replace("if relative in {v['relative']for v in selected}:continue","if relative in {v['relative']for v in selected}or relative==earlier:continue")
    raw=raw.replace("'selected':selected,","'selected':selected,'sameSessionEarlierPointNotImported':[earlier],'sameSessionEarlierPointSameBytes':True,'inspectorPid1GenerationVerified':True,")
    raw=inspect.getsource(inspector_window)+'\n'+raw
    compile(raw,'<current9 plus explicit earlier point, archive20>','exec');return raw


def main():
    # Preserve the actual direct readonly transport, with a distinct unused slot.
    ns={**engine.__dict__,'SLOT':SLOT,'catalog_source':catalog_source}
    exec(compile(inspect.getsource(previous_main),'<new-only current9 transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
