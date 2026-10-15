"""Two eligible current-source Root cohorts, CRC/session proof then eighteen latest streams."""
import inspect
from pyflakes.api import check
import pg3532_outbox_current_native_qualified as current
import pg2908_network_current_native_qualification as transport
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate
from pg3564_current_browser_resume_sources import SOURCE


def inspector_pairs(points,sessions):
    if type(points)is not list or type(sessions)is not list or not len(points)==len(sessions)==20:
        raise ValueError('exact two current ten-point cohorts required')
    groups={}
    for i,(point,session)in enumerate(zip(points,sessions,strict=True)):
        if point['unit']!='schubert-nk-inbox-inspector.service':continue
        name=point['relative']
        suffix=next((s for s in ['.closing.exec','.terminal.exec']if name.endswith(s)),None)
        if suffix is None:raise ValueError('exact Inspector role required')
        key=name[:-len(suffix)];kind='closing'if suffix=='.closing.exec'else'terminal'
        group=groups.setdefault(key,{})
        if kind in group:raise ValueError('duplicate Inspector point')
        group[kind]=(i,session)
    if len(groups)!=2:raise ValueError('two distinct actual Inspector generations required')
    result=[];identities=set()
    for group in groups.values():
        if set(group)!={'closing','terminal'}:raise ValueError('complete Inspector point pair required')
        c,closed=group['closing'];e,early=group['terminal']
        if not(closed['sessionIdSha256']==early['sessionIdSha256']and closed['startMs']==early['startMs']and early['dumpMs']<=closed['dumpMs']):
            raise ValueError('same Inspector session and monotonic dump required')
        identity=closed['sessionIdSha256']
        if identity in identities:raise ValueError('distinct Root Inspector sessions required')
        identities.add(identity);result.append((c,e))
    return result


def server():
    raw=current.server().replace('PG3532-native-input-v3.tar','PG3632-native-input-v1.tar').replace('PG3532-native-v3','PG3632-native-v1')
    raw=raw.replace("len(v['selected'])==10","len(v['selected'])==20")
    start=raw.index('inspector=[(point,session)');end=raw.index("modules=['protocol'",start)
    replacement=inspect.getsource(inspector_pairs)+"\npairs=inspector_pairs(v['selected'],sessions);early_indices=set()\nfor number,(closing_index,early_index)in enumerate(pairs):\n check_point=subprocess.run([str(J/'java'),'-cp',cp,'NativePointDominance',str(streams[early_index]),str(streams[closing_index])],capture_output=True,timeout=30)\n require(check_point.returncode==0 and not check_point.stderr and check_point.stdout==b'sameSessionProbeMonotonic=true;latestClosingOnly=true\\n')\n (O/('inspector-point-dominance-'+str(number)+'.private.log')).write_bytes(check_point.stdout);early_indices.add(early_index)\nstreams=[p for i,p in enumerate(streams)if i not in early_indices];require(len(streams)==18)\n"
    raw=raw[:start]+replacement+raw[end:]
    raw=raw.replace("'currentNativeStreams':9","'currentNativeStreams':18").replace("'validatedNativePoints':10","'validatedNativePoints':20")
    raw=raw.replace("'excludedHistorical':v['excludedHistorical']","'excludedHistorical':v['excludedHistorical'],'exclusionScope':'SECOND_COHORT_ONLY','eligibleCurrentSourceCohorts':2,'previousSameSourceNativeRequalified':True,'historicalSourceNativeImported':False")
    extractor=transport.prior.previous.entry().__globals__['coordinates']
    complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(extractor)+'\n'+raw
    if check(complete,'<two current cohorts full native qualification>'):raise ValueError('complete server globals required')
    compile(raw,'<two current cohorts same3712 qualification>','exec');return raw


def source():
    raw=transport.source()
    for old,new in [('pg2908-network-current-native-qualified-v2','pg3632-current-browser-native-qualified-v1'),('pg2906-network-current-native-catalog-v1','pg3630-current-browser-native-catalog-v1'),('pg2800-jdbc-null-fixed-full-qualified-v1','pg3414-outbox-full-qualified-v1'),('PG2908-native-v2','PG3632-native-v1'),('PG2908-native-input-v2.tar','PG3632-native-input-v1.tar')]:raw=raw.replace(old,new)
    start=raw.index("    for i,v in enumerate(catalog['selected']):")
    end=raw.index("    root=Path(__file__).parent/",start)
    replacement="""    previous=W/'pg3532-outbox-current-native-qualified-v3'
    old_manifest=json.loads((previous/'manifest.safe.json').read_bytes());old_input=json.loads((previous/'input.safe.json').read_bytes());old_catalog=json.loads((W/'pg3530-outbox-current-native-catalog-v1/manifest.safe.json').read_bytes())
    if not(old_manifest['actualExit']==0 and old_manifest['productionSource']==SOURCE and old_input['productionSource']==SOURCE and old_catalog['actualExit']==0 and old_input['selected']==old_catalog['selected']and len(old_input['selected'])==10):raise ValueError('qualified current first cohort cache required')
    catalog['selected']=old_input['selected']+catalog['selected']
    for i,v in enumerate(catalog['selected']):
        path=out/(str(i)+'.exec')
        if i<10:
            content=(previous/(str(i)+'.exec')).read_bytes()
            if hashlib.sha256(content).hexdigest()!=v['sha256']or len(content)!=v['bytes']:raise ValueError('same-current immutable cache mismatch')
            with path.open('xb')as f:f.write(content);f.flush();os.fsync(f.fileno())
        else:
            with path.open('xb')as f:
                r=subprocess.run(SSH+['sudo','-n','cat','/run/schubert-nk/pt-coverage/'+v['relative']],stdout=f,stderr=subprocess.PIPE,timeout=20);f.flush();os.fsync(f.fileno())
            if r.returncode!=0 or r.stderr or sha(path)!=v['sha256']or path.stat().st_size!=v['bytes']:raise ValueError('private new current immutable native read refused')
"""
    raw=raw[:start]+replacement+raw[end:]
    # Capacity covers both preserved first cohort and the newly read cohort;
    # this is not a relaxation of native/input validation or coverage scope.
    raw=raw.replace('require_bytes=10*16777216+805306368','require_bytes=20*16777216+805306368')
    old="'streams':9,'validatedPoints':10"
    if raw.count(old)!=1:raise ValueError('one inherited console-only cohort count boundary required')
    raw=raw.replace(old,"'streams':result['currentNativeStreams'],'validatedPoints':result['validatedNativePoints']",1)
    compile(raw,'<actual same-current two-cohort transport>','exec');return raw


def main():
    ns={**transport.entry().__globals__,'CODE':server(),'SOURCE':SOURCE,'qualify_snapshot':current.qualify_snapshot}
    exec(compile(source(),'<current Browser plus original cohort native qualification>','exec'),ns)
    with management_gate(P/'current-management-critical.lock'):return ns['main']()


if __name__=='__main__':raise SystemExit(main())
