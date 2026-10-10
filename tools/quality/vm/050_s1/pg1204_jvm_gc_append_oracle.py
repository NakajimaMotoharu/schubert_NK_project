"""Independent INFO GC append classification; every old journal field retained."""
import json
import re

BOOT='cbca87383b244090b77cbf029677cdd6'
WEB='schubert-nk-web.service'
NUM=r'[0-9]+(?:\.[0-9]+)?'
SIZE=r'[0-9]+[KMG]'
HEADER=r'\[([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+[+-][0-9]{4})\]\[('+NUM+r')s\]\[info\]\[(gc(?:,[a-z]+)? *)\] GC\(([0-9]+)\) (.+)'
BODIES=[r'Pause Young \(Allocation Failure\)',
        r'DefNew: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\) Eden: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\) From: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\)',
        r'Tenured: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\)',
        r'Metaspace: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\) NonClass: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\) Class: '+SIZE+r'\('+SIZE+r'\)->'+SIZE+r'\('+SIZE+r'\)',
        r'Pause Young \(Allocation Failure\) '+SIZE+r'->'+SIZE+r'\('+SIZE+r'\) '+NUM+r'ms',
        r'User='+NUM+r's Sys='+NUM+r's Real='+NUM+r's']
TAGS=['gc,start','gc,heap','gc,heap','gc,metaspace','gc','gc,cpu']


def qualify(old,new):
    if type(old)is not dict or type(new)is not dict or set(old)!=set(new):raise ValueError('whole journal scope required')
    added_count=0
    for unit,previous in old.items():
        prior=json.loads(bytes.fromhex(previous));current=json.loads(bytes.fromhex(new[unit]))
        if current[:len(prior)]!=prior:raise ValueError('all old journal fields and order required')
        extra=current[len(prior):]
        if not extra:continue
        if unit!=WEB or len(extra)%6!=0:raise ValueError('only complete fixed Web GC groups permitted')
        seen={r['__CURSOR']for r in prior};stamp=max(int(r['__MONOTONIC_TIMESTAMP'])for r in prior)
        for offset in range(0,len(extra),6):
            gc=None;uptime=-1
            for index,row in enumerate(extra[offset:offset+6]):
                expected={'_BOOT_ID':BOOT,'_SYSTEMD_UNIT':WEB,'_SYSTEMD_INVOCATION_ID':'898429f0e6a64d4fa7a6c07e4473fe8a','_PID':'526861','_UID':'997','PRIORITY':'6'}
                if type(row)is not dict or any(row.get(k)!=v for k,v in expected.items()):raise ValueError('current Web GC sender required')
                cursor=row.get('__CURSOR');mono=row.get('__MONOTONIC_TIMESTAMP');m=re.fullmatch(HEADER,row.get('MESSAGE',''))
                if type(cursor)is not str or not cursor or cursor in seen or type(mono)is not str or not mono.isdigit()or int(mono)<stamp or m is None:
                    raise ValueError('unique ordered complete GC event required')
                if m[3].strip()!=TAGS[index]or re.fullmatch(BODIES[index],m[5])is None or gc is not None and gc!=m[4]or float(m[2])<uptime:
                    raise ValueError('independent GC grammar and order required')
                gc=m[4];uptime=float(m[2]);seen.add(cursor);stamp=int(mono)
            added_count+=6
    return {'oldAllFieldsAndOrderRetained':True,'qualifiedInfoGcAppended':added_count,'authority':False}
