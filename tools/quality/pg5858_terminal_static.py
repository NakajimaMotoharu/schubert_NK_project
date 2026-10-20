"""Exact four admission-halt additions, all851/1666 source/bytes and unfiltered static policy."""
import hashlib
import inspect
import subprocess
import pg5776_jms_primary_static as engine
from pg5804_rollback_static import class_key,signature

OWNERS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'+n+'.java':owner for n,owner in(('SyncRequestConsumers','runtime.halted'),('QuestionWorkConsumers','result.halted'),('WebLogConsumers','result.halted'))}
OWNERS['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java']='halted'
MODIFIED=set(OWNERS)


def expected_source(path,before):
    kind='Reply'if'/schubert-nk-web/'in path else'Inbound';old='} catch (CommittedFatal'+kind+'Exception fatal) {\n'
    if before.count(old)!=1:raise ValueError('one exact committed phase catch')
    start=before.index(old);indent=before[before.rfind('\n',0,start)+1:start]
    if indent.strip():raise ValueError('catch starts on one standalone source line')
    return before.replace(old,old+indent+'  '+OWNERS[path]+'.set(true);\n',1)


def class_contract(old,current):
    outer={class_key(p)for p in MODIFIED};changed={k for k in old if k in current and old[k]!=current[k]}
    if len(old)!=1666 or len(current)!=1666 or set(old)!=set(current)or not outer<=changed or any(not any(k==o or k.startswith(o[:-6]+'$')for o in outer)for k in changed):raise ValueError('all1666 actual classes; only four declared receiver owners')
    return sorted(changed)


def pg_contract(snapshot,value,old):
    sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};before=old['allSourceHashes']
    if len(sources)!=851 or set(sources)!=set(before)or {p for p in sources if sources[p]!=before[p]}!=MODIFIED:raise ValueError('only four declared Main source additions')
    for path,digest in sources.items():
        if hashlib.sha256(subprocess.check_output(['git','show',value['source']+':'+path],cwd=engine.ROOT)).hexdigest()!=digest:raise ValueError('canonical compile source')
    prior=engine.W/'pg5844-protocol-expression-selected105-v1/source'
    for path in MODIFIED:
        if expected_source(path,(prior/path).read_text())!=(snapshot/path).read_text():raise ValueError('one admission halt before committed terminal publication only')
        if signature(prior,path)!=signature(snapshot,path):raise ValueError('public descriptors unchanged')
    return sources,class_contract(old['auxClassHashes'],value['allPhysicalMainSha256'])


def runner_source():
    raw=inspect.getsource(engine.main)
    changes={
      'pg5774-jms-primary-green-v1/manifest.safe.json':'pg5856-terminal-selected70-v1/manifest.safe.json',
      "(v['tests'],v['suites'])==(14,7)":"(v['tests'],v['suites'])==(70,20)",
      'pg5750-exception-static-v1/manifest.safe.json':'pg5848-protocol-expression-static-v1/manifest.safe.json',
      'provisional/PG5750-exception-static-v1/manifest.json':'provisional/PG5848-protocol-expression-static-v1/manifest.json',
      '70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9':'3c2ce6616b6b050543ec7ab9e580f2f2890d8bbf58fc7597da35a913c2f24100',
      '    guards=guard_coverage(snapshot)':'    guards=v["targetCounters"]',
      ";expected_counts=Counter(old['ruleCounts']);expected_counts['CompareObjectsWithEquals']+=3":";expected_counts=Counter(old['ruleCounts'])",
      "'changedSourcePaths':sorted(PATHS)":"'changedSourcePaths':sorted(MODIFIED)",
      "'physicalMain':1664":"'physicalMain':1666", "'unchangedPhysicalClasses':1662":"'unchangedPhysicalClasses':1666-len(classes)",
      "'allFieldAndMethodDescriptorsUnchanged':True":"'existingPublicAbiUnchanged':True,'removedPublicDescriptors':0,'addedPublicDescriptors':0",
      "'inputSourceFiles':849":"'inputSourceFiles':851", "'actualAuxClasses':1664":"'actualAuxClasses':1666",
      "'newGuardsActualCoverage':guards":"'selectedTargetActualCounters':guards", ",'newGuardsActualCoverage','F03Accepted'":",'selectedTargetActualCounters','F03Accepted'",
      "provisional/PG5776-jms-primary-static-v1';target.mkdir()":"provisional/PG5858-terminal-static-v1';target.mkdir()"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact terminal source/static binding: '+old)
        raw=raw.replace(old,new,1)
    a=raw.index('    sources=');b=raw.index("    for name in('pmd.xml','checkstyle.xml'):",a)
    raw=raw[:a]+"    sources,classes=pg_contract(snapshot,v,old)\n    current=v['allPhysicalMainSha256'];before_snapshot=W/'pg5844-protocol-expression-selected105-v1/source'\n"+raw[b:]
    compile(raw,'<all851 terminal source static>','exec');return raw


def main():
    scope={**vars(engine),'SLOT':'pg5858-terminal-static-v1','MODIFIED':MODIFIED,'pg_contract':pg_contract}
    exec(compile(runner_source(),'<all851 terminal source static>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
