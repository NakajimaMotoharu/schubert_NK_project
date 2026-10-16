"""Fresh failed current cohort facts, not normal authority; preserve all original files and live owners."""
import inspect
import pg4052_failed_current_capture as previous
from pg4060_original_profile_dual_stack import once
from pg4260_stable_admission_image import live

SLOT='pg4300-current-failed-capture-v1'


def payload():
    b=live();raw=previous.payload().replace(previous.SLOT,SLOT)
    # Bind positive fixed-owner roles only. No embedded historical raw snapshots
    # or oracle capsules occur in this reader; immutable4008 is still pinned.
    for old,new in [('820851b8291a4c958bb34f6c48430ca3',b['invocation']),
                    ('c9444dbf2e6a43dca0d52ab220d59b1d','a2854d416df04461a98aa25182ac6257'),
                    ('af0eb750d72443739bead6a879a51e13','2a74a4cacc484c0bbc3f6dce64f1e566'),
                    ('a0c7fb91c4da42f09faec0f065a87767','25aa7706821f4215bae941e511047c6a'),
                    ('d9d58371-bf80-49f6-bad9-3d1e0916fb04',b['activation'])]:raw=raw.replace(old,new)
    raw=once(raw,"'artemis.service':'9cb091b80682402aaed1d2d1d2d2a5d7'",'')
    marker="if int(v['MainPID'])>1:"
    raw=once(raw,marker,"if name=='artemis.service':require(v['ActiveState']=='active'and v['SubState']=='running'and re.fullmatch('[0-9a-f]{32}',v['InvocationID'])is not None)\n  "+marker)
    raw=once(raw,"require(done_sha=='ca7829dbf4f1f215bc9bc6c60dd02c94137e2157a665ee57905b3c2aa5f0d090')",
      "fields=done.read_bytes().decode('ascii').splitlines();require(len(fields)==6 and fields[:4]==['NKDONE1',"+repr(b['run'])+','+repr(b['cutoff'])+','+repr(b['activation'])+"]and fields[5]in {'0','10'});require(datetime.datetime.fromisoformat(fields[4].replace('Z','+00:00'))>=datetime.datetime.fromisoformat("+repr(b['cutoff'].replace('Z','+00:00'))+"))")
    raw=once(raw,"private={'first':first,", "require(len(first['actors'])==4 and not Path('/proc/"+str(b['rootPid'])+"').exists())\nprivate={'first':first,")
    raw=once(raw,"'parentFailed143':True,","'parentFailed143':True,'originalBudgetSeconds':1800,'elapsedParentSeconds':(int(first['units']['schubert-nk-morning-controller.service']['ExecMainExitTimestampMonotonic'])-int(first['units']['schubert-nk-morning-controller.service']['ExecMainStartTimestampMonotonic']))/1000000,")
    raw=once(raw,"'done10NotParentSuccess':True,","'done10NotParentSuccess':fields[5]=='10','doneCode':int(fields[5]),'doneDataIsNotParentSuccess':True,")
    return raw


def main():
    ns={**vars(previous),'SLOT':SLOT,'payload':payload}
    exec(compile(inspect.getsource(previous.main),'<new failed cohort readonly capture>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
