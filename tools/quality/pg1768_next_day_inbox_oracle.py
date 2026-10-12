"""SS324/352 + UI236 USRMUT24 independent authenticated UPW oracle.

PG1767 explicitly refused the unimplemented route, and remains NOT_ACCEPTED.
Independent AESGCM/zlib and literal byte offsets; never a Production call.
"""
import ast
import inspect
import pg1767_next_day_independent_candidates_v2 as prior
from pg553_inbox_oracle import aad,plaintext,require
from pg478_cleanup_oracle import instant


def validate_upw(row,wire,users):
    import datetime,re,uuid
    require(type(wire)is bytearray and len(wire)==280)
    require((row['request_layout_id'],row['response_layout_id'],row['request_version'],row['response_version'],row['processing_state'],row['result_ref_type'])==('UPWREQ01','UPWRSP01','001','001','COMPLETED','USER'))
    require(type(row['owner_user_id'])is int and 1<=row['owner_user_id']<=999999999999 and row['result_ref_uuid']is None)
    require(row['operation_token']is not None and str(uuid.UUID(row['operation_token']))==row['operation_token']and uuid.UUID(row['operation_token']).int!=0)
    require(row['fingerprint_key_version']=='v1'and re.fullmatch('[0-9a-f]{64}',row['request_fingerprint_hmac'])is not None)
    require(instant(row['created_at'])<=instant(row['completed_at'])and instant(row['expires_at'])>=instant(row['completed_at'])+datetime.timedelta(hours=168))
    require(wire[:24]==b'SCHBNK01001UPWRSP01001SS')
    mid=bytes(wire[24:60]).decode('ascii');require(str(uuid.UUID(mid))==mid and uuid.UUID(mid).int!=0)
    require(wire[60:96]==row['message_id'].encode()and re.fullmatch(b'[0-9a-f]{64}',bytes(wire[113:177]))is not None)
    time=instant(row['completed_at']).astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    require(wire[96:113]==(time.strftime('%Y%m%d%H%M%S')+f'{time.microsecond//1000:03}').encode())
    require(wire[177:181]==b'0256'and wire[181:187]==b'000024'and wire[187:193]==b'000000'and wire[193:199]==b'000000'and wire[199:208]==b'000000280'and wire[208:212]==b'0000'and wire[212:256]==b' '*44)
    require(re.fullmatch(b'[0-9]{21}',bytes(wire[256:277]))is not None and wire[277:280]==b' '*3)
    target=int(bytes(wire[256:268]));version=int(bytes(wire[268:277]))
    require(1<=target<=999999999999 and 1<=version<=999999999 and row['result_ref_id']==target)
    found=[u for u in users if u['id']==target]
    require(len(found)==1 and type(found[0]['version'])is int and version<=found[0]['version']<=999999999)


def classify_inbox(rows,selected,key):
    ids=set(selected);found={r['message_id']:r for r in rows['schubert.request_inbox']if r['message_id']in ids}
    require(set(found)==ids);sessions={r['id']for r in rows['schubert.auth_sessions']}
    deleted=[];protected=[]
    for mid,row in found.items():
        if (row['request_layout_id'],row['response_layout_id'],row['processing_state'],row['result_ref_type'],row['owner_user_id'])==('LGNREQ01','LGNRSP01','COMPLETED','AUTH_SESSION',None):
            require(row['result_ref_uuid']is not None and row['result_ref_uuid']not in sessions);protected.append(mid)
        elif row['response_layout_id']=='UPWRSP01':
            wire=plaintext(row,key)
            try:validate_upw(row,wire,rows['schubert.app_users']);deleted.append(mid)
            finally:wire[:]=b'\0'*len(wire)
        else:raise ValueError('separate independent route oracle required')
    return {'deleted':sorted(deleted),'protected':sorted(protected),'basis':'SS324 missing immutable AUTH_SESSION protected; UPW independent AESGCM/UI236/reference-version verified'}


def payload():
    raw=prior.payload()
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='classify_inbox')
    raw=raw.replace(ast.get_source_segment(raw,node),inspect.getsource(require)+'\n'+inspect.getsource(aad)+'\n'+inspect.getsource(plaintext)+'\n'+inspect.getsource(validate_upw)+'\n'+inspect.getsource(classify_inbox))
    raw='import base64,struct,uuid,zlib,stat\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\n'+raw
    raw=raw.replace("inbox=classify_inbox(before['rows'],expected['inbox_scan_candidates'])",r'''
keypath=pathlib.Path('/etc/schubert-nk/credentials/api-inbox-response-aes-current');s=keypath.lstat()
require(stat.S_ISREG(s.st_mode)and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)in [0o400,0o600])
parts=keypath.read_bytes().split(b'\n');require(len(parts)==4 and parts[:2]==[b'NKKEY1',b'v1']and not parts[-1]);key=bytearray(base64.b64decode(parts[2],validate=True));require(len(key)==32)
try:inbox=classify_inbox(before['rows'],expected['inbox_scan_candidates'],key)
finally:key[:]=b'\0'*len(key)
''')
    raw=raw.replace('pg1767-next-day-independent-candidates-v2','pg1768-next-day-inbox-oracle-v1')
    from pyflakes.api import check
    if check(raw,'<actual independent UPW oracle>'):raise ValueError('undefined emitted global refused')
    compile(raw,'<independent two-route before oracle>','exec');return raw


def main():
    raw=inspect.getsource(prior.prior.main).replace('pg1766-next-day-independent-candidates-v1','pg1768-next-day-inbox-oracle-v1')
    ns={**prior.prior.__dict__,'payload':payload};exec(compile(raw,'<independent before-only transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
