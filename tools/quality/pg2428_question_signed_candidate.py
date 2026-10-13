"""BUG1238: exact qualified containers, timestamp-only metadata and one JS payload delta."""
import inspect
import struct
import zipfile
import pg2406_question_signed_candidate as previous

W,P,T=previous.W,previous.P,previous.T
OLD=previous.OLD
NEXT=W/'pg2428-release-v1'
FROZEN=W/'pg2428-frozen-six-v1'
SIG=P/'pg2428-manifest-v1.sig'


def masked(raw,ranges):
    value=bytearray(raw)
    for a,b in ranges:
        value[a:b]=bytes(b-a)
    return bytes(value)


def verify_container(before,after,changed=frozenset()):
    """Compare every compressed member and header; only DOS timestamps may drift.

    A changed JS payload additionally changes its CRC/size, subsequent offsets,
    and EOCD central offset. No arbitrary ZIP extra/comment/trailing bytes.
    """
    with zipfile.ZipFile(before) as a,zipfile.ZipFile(after) as b:
        aa,bb=a.infolist(),b.infolist();ar,br=before.read_bytes(),after.read_bytes()
        if [i.filename for i in aa]!=[i.filename for i in bb] or len({i.filename for i in aa})!=len(aa) or a.comment!=b.comment or not aa:
            raise ValueError('same ordered complete Jar inventory required')
        if aa[0].header_offset!=0 or bb[0].header_offset!=0:
            raise ValueError('no foreign archive prefix allowed')
        actual_changed=set()
        for index,(i,j) in enumerate(zip(aa,bb,strict=True)):
            for field in ['compress_type','create_system','create_version','extract_version',
                          'flag_bits','volume','internal_attr','external_attr','extra','comment']:
                if getattr(i,field)!=getattr(j,field):
                    raise ValueError('foreign Jar metadata delta refused')
            if a.read(i)!=b.read(j):actual_changed.add(i.filename)
            fragments=[]
            for archive,raw,info,rows in [(a,ar,i,aa),(b,br,j,bb)]:
                offset=info.header_offset
                if raw[offset:offset+4]!=b'PK\x03\x04':raise ValueError('local header required')
                n,e=struct.unpack_from('<HH',raw,offset+26);end=offset+30+n+e
                limit=rows[index+1].header_offset if index+1<len(rows) else archive.start_dir
                header=raw[offset:end];content=raw[end:end+info.compress_size]
                descriptor=raw[end+info.compress_size:limit]
                if info.flag_bits&8:
                    expected=struct.pack('<III',info.CRC,info.compress_size,info.file_size)
                    if descriptor not in [expected,b'PK\x07\x08'+expected]:
                        raise ValueError('exact data descriptor required')
                elif descriptor:
                    raise ValueError('foreign local record tail refused')
                fragments.append((header,content,descriptor))
            ranges=[(10,14)]+([(14,26)] if i.filename in changed else [])
            if masked(fragments[0][0],ranges)!=masked(fragments[1][0],ranges):
                raise ValueError('foreign local header bytes refused')
            if i.filename not in changed and fragments[0][1:]!=fragments[1][1:]:
                raise ValueError('unchanged compressed payload/descriptor required')
        if actual_changed!=set(changed):raise ValueError('exact approved payload differences required')
        central=[]
        for archive,raw,rows in [(a,ar,aa),(b,br,bb)]:
            offset=archive.start_dir;headers=[]
            for info in rows:
                if raw[offset:offset+4]!=b'PK\x01\x02':raise ValueError('complete central header required')
                n,e,c=struct.unpack_from('<HHH',raw,offset+28);end=offset+46+n+e+c
                ranges=[(12,16),(42,46)]+([(16,28)] if info.filename in changed else [])
                headers.append(masked(raw[offset:end],ranges));offset=end
            tail=raw[offset:]
            if len(tail)!=22+len(archive.comment) or tail[:4]!=b'PK\x05\x06':
                raise ValueError('no foreign central directory tail allowed')
            central.append((headers,masked(tail,[(16,20)])))
        if central[0]!=central[1]:raise ValueError('foreign central metadata delta refused')


def receive(module):
    raw=inspect.getsource(previous.prior.transfer.receive).replace('PG1532','PG2404').replace('pg1535','pg2428')
    namespace={**previous.prior.transfer.__dict__,'FROZEN':FROZEN}
    exec(compile(raw,'<qualified new-only six jars>','exec'),namespace)
    path=namespace['receive'](module)
    old_path={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}.get(module)
    if old_path is None:
        import json
        rows=json.loads((OLD/'RELEASE-MANIFEST.json').read_bytes())['artifacts']
        old_path=next(r['path'] for r in rows if r['path'].endswith('/'+path.name))
    changed={previous.RESOURCE} if module=='web' else set()
    verify_container(OLD/old_path,path,changed)
    if module=='web':previous.verify_web_resource(OLD/old_path,path)
    return path


def main_source():
    raw=previous.main_source().replace('pg2406','pg2428').replace('PG2406','PG2428')
    marker="{'VERSION', 'web/web.jar'} == changed"
    if raw.count(marker)!=1:raise ValueError('one old incorrect container-only assertion required')
    raw=raw.replace(marker,"{'VERSION', 'web/web.jar'} <= changed")
    return raw


def main():
    namespace={**previous.prior.__dict__,'__file__':__file__,'PRODUCTION':previous.production(),
               'OLD_SOURCE':previous.OLD_SOURCE,'OLD_BOM':previous.OLD_BOM,'OLD':OLD,'NEXT':NEXT,
               'FROZEN':FROZEN,'SIG':SIG,'receive':receive,'validate_gate':previous.validate_gate,
               'verify_delta':previous.verify_delta}
    exec(compile(main_source(),'<strict container classified new candidate>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':
    raise SystemExit(main())
