"""Independent PID1 new-run completion oracle; GC zero/ready is not parent success."""
import datetime

BOOT='cc9ed8747f4f450ea1888de1e42c8441'
INV='267003d6e12845dd8690cd9bd5afcad0'
JOB='76444'
START=57679957905
RUN='b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e'
CUTOFF='2026-10-08T07:36:21.802335Z'
ACT='57f0e73d-d334-4882-9284-04246011da54'


def require(ok):
    if not ok:raise ValueError('genuine current-parent completion rejected')


def completed(rows,done):
    require(type(rows)is list and bool(rows)and all(type(r)is dict for r in rows))
    cursors=set()
    for r in rows:
        require(all(r.get(k)==v for k,v in {'_BOOT_ID':BOOT,'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':INV}.items()))
        stamp=r.get('__MONOTONIC_TIMESTAMP');cursor=r.get('__CURSOR')
        require(type(stamp)is str and stamp.isdigit()and START<=int(stamp)<=START+1800000000)
        require(type(cursor)is str and cursor and cursor not in cursors);cursors.add(cursor)
        require(r.get('JOB_RESULT')in(None,'done'))
    jobs=[r for r in rows if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_ID')==JOB and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']
    success=[r for r in rows if r.get('MESSAGE_ID')=='7ad2d189f7e94e70a38c781354912448']
    require(len(jobs)==len(success)==1)
    require(type(done)is bytes and 140<=len(done)<=141 and done.endswith(b'\n'))
    fields=done.decode('ascii').splitlines();require(len(fields)==6 and fields[:4]==['NKDONE1',RUN,CUTOFF,ACT]and fields[5]=='0')
    end=datetime.datetime.fromisoformat(fields[4].replace('Z','+00:00'))
    real=jobs[0].get('__REALTIME_TIMESTAMP');require(type(real)is str and real.isdigit())
    jobtime=datetime.datetime.fromtimestamp(int(real)/1000000,datetime.timezone.utc)
    require(end.tzinfo is not None and datetime.datetime.fromisoformat(CUTOFF.replace('Z','+00:00'))<=end<=jobtime and (jobtime-end).total_seconds()<=60)
    return {'genuinePid1StartDone':True,'genuineRootDone':True,'endMonotonicUs':int(jobs[0]['__MONOTONIC_TIMESTAMP']),'elapsedSeconds':(int(jobs[0]['__MONOTONIC_TIMESTAMP'])-START)/1000000,'sameRunActivationCutoff':True}
