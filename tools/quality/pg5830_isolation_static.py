"""Independent851 source/1666 physical proof and unchanged static rules after isolation PG."""
import hashlib
import inspect
import subprocess
import pg5776_jms_primary_static as engine
from pg5804_rollback_static import class_key,signature

MODIFIED={
 'src/schubert-nk-'+m+'/src/main/java/dev/codex/schubert/nk/'+p+'.java'
 for m,paths in {
  'api':['api/messaging/inbound/'+s for s in('InboundTransactions','SyncRequestConsumers','QuestionWorkConsumers','WebLogConsumers')],
  'web':['web/messaging/ArtemisReplyConsumer','web/messaging/ArtemisReplyConsumers']}.items()for p in paths}
ADDED='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/FailedJmsIsolationException.java'


def class_contract(prior,current):
    changed={k for k in prior if k in current and prior[k]!=current[k]}
    if len(prior)!=1665 or len(current)!=1666 or set(current)-set(prior)!={class_key(ADDED)}or set(prior)-set(current)or changed!={class_key(p)for p in MODIFIED}:raise ValueError('one added, six modified, all1659 other actual Main byte-identical')
    return sorted(changed|{class_key(ADDED)})


def pg_contract(snapshot,value,old):
    sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};before=old['allSourceHashes']
    if len(sources)!=851 or set(sources)-set(before)!={ADDED}or set(before)-set(sources)or{p for p in before if sources[p]!=before[p]}!=MODIFIED:raise ValueError('exact isolation-phase PG source set')
    for path,digest in sources.items():
        if hashlib.sha256(subprocess.check_output(['git','show',value['source']+':'+path],cwd=engine.ROOT)).hexdigest()!=digest:raise ValueError('canonical compile source')
    classes=class_contract(old['auxClassHashes'],value['allPhysicalMainSha256']);prior=engine.W/'pg5800-rollback-selected54-v5/source';abi=[]
    for path in sorted(MODIFIED):
        if signature(prior,path)!=signature(snapshot,path):raise ValueError('existing public descriptors unchanged')
        abi.append({'sourcePath':path,'removedPublicDescriptors':0,'addedPublicDescriptors':0})
    constructor=signature(snapshot,ADDED)
    if len(constructor)!=1 or {d for _,d in constructor}!={'descriptor: (Ljava/lang/Throwable;Ldev/codex/schubert/nk/protocol/codec/PermanentProtocolException;)V'}:raise ValueError('only declared internal phase constructor')
    return sources,classes,abi


def runner_source():
    raw=inspect.getsource(engine.main)
    changes={
      'pg5774-jms-primary-green-v1/manifest.safe.json':'pg5828-isolation-selected66-v1/manifest.safe.json',
      "(v['tests'],v['suites'])==(14,7)":"(v['tests'],v['suites'])==(66,18)",
      'pg5750-exception-static-v1/manifest.safe.json':'pg5810-rollback-static-reauth-v1/manifest.safe.json',
      'provisional/PG5750-exception-static-v1/manifest.json':'provisional/PG5810-rollback-static-reauth-v1/manifest.json',
      '70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9':'68b697ad9162315810ccc0c4adb0cceb200dc60ca44c8686750998742cea5c23',
      '    guards=guard_coverage(snapshot)':'    guards=v["targetCounters"]',
      ";expected_counts=Counter(old['ruleCounts']);expected_counts['CompareObjectsWithEquals']+=3":"",
      " and Counter(r['rule']for r in rows)==expected_counts":"",
      "'changedSourcePaths':sorted(PATHS)":"'changedSourcePaths':sorted(MODIFIED|{ADDED})",
      "'physicalMain':1664":"'physicalMain':1666",
      "'unchangedPhysicalClasses':1662":"'unchangedPhysicalClasses':1659",
      "'allFieldAndMethodDescriptorsUnchanged':True":"'publicAbi':abi,'removedPublicDescriptors':0,'declaredAdditionalOverloads':0",
      "'inputSourceFiles':849":"'inputSourceFiles':851",
      "'actualAuxClasses':1664":"'actualAuxClasses':1666",
      "'newGuardsActualCoverage':guards":"'selectedTargetActualCounters':guards",
      ",'newGuardsActualCoverage','F03Accepted'":",'selectedTargetActualCounters','F03Accepted'",
      "provisional/PG5776-jms-primary-static-v1';target.mkdir()":"provisional/PG5830-isolation-static-v1';target.mkdir()"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one exact851 static predicate: '+old)
        raw=raw.replace(old,new,1)
    a=raw.index('    sources=');b=raw.index("    for name in('pmd.xml','checkstyle.xml'):",a)
    raw=raw[:a]+"    sources,classes,abi=pg_contract(snapshot,v,old)\n    current=v['allPhysicalMainSha256'];before_snapshot=W/'pg5800-rollback-selected54-v5/source'\n"+raw[b:]
    compile(raw,'<all851 isolation static>','exec');return raw


def main():
    scope={**vars(engine),'SLOT':'pg5830-isolation-static-v1','MODIFIED':MODIFIED,'ADDED':ADDED,'pg_contract':pg_contract}
    exec(compile(runner_source(),'<all851 isolation static>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
