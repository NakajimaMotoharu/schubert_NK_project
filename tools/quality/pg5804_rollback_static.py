"""Declared rollback PG delta, immutable850 source/1665 Main and full unfiltered static input."""
import inspect
import hashlib
import subprocess
import pg5776_jms_primary_static as engine

MODULE_BASE='src/schubert-nk-'
PATHS={
 'api':['api/messaging/inbound/'+s for s in('InboundTransactions','SyncRequestConsumers','QuestionWorkConsumers','WebLogConsumers')],
 'web':['web/messaging/'+s for s in('ArtemisReplyConsumer','ArtemisReplyConsumers')]+['web/bootstrap/WebNativeRuntime','web/bootstrap/WebLogApplicationRuntime']}
MODIFIED={MODULE_BASE+m+'/src/main/java/dev/codex/schubert/nk/'+s+'.java'for m,paths in PATHS.items()for s in paths}
ADDED=MODULE_BASE+'protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/UnconfirmedJmsRollbackException.java'


def class_key(path):
    return path.split('/')[1].removeprefix('schubert-nk-')+':'+path.split('/src/main/java/')[1][:-5]+'.class'


def class_contract(prior,current):
    changed={k for k in prior if k in current and prior[k]!=current[k]}
    if len(prior)!=1664 or len(current)!=1665 or set(current)-set(prior)!={class_key(ADDED)}or set(prior)-set(current)or changed!={class_key(p)for p in MODIFIED}:raise ValueError('one added, exactly eight modified actual Main; all other1656 byte-identical')
    return sorted(changed|{class_key(ADDED)})


def signature(snapshot,path):
    member=path.split('/src/main/java/')[1][:-5].replace('/','.')
    lines=subprocess.check_output([str(engine.TC/'jdk-25.0.4/bin/javap'),'-public','-s','-classpath',str(snapshot/('src/'+path.split('/')[1]+'/target/classes')),member],text=True).splitlines();pairs=set()
    for i,line in enumerate(lines[:-1]):
        if line.strip().startswith('public ')and line.strip().endswith(';'):
            if not lines[i+1].strip().startswith('descriptor:'):raise ValueError('actual public descriptor following declaration')
            pairs.add((line.strip(),lines[i+1].strip()))
    return pairs


def pg_contract(snapshot,value,old):
    sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')}
    before=old['allSourceHashes']
    if len(sources)!=850 or set(sources)-set(before)!={ADDED}or set(before)-set(sources)or{p for p in before if sources[p]!=before[p]}!=MODIFIED:raise ValueError('one added and eight exact changed Main sources')
    for path,digest in sources.items():
        raw=subprocess.check_output(['git','show',value['source']+':'+path],cwd=engine.ROOT)
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('compiled canonical source, no dirty success borrowing')
    classes=class_contract(old['auxClassHashes'],value['allPhysicalMainSha256']);prior=engine.W/'pg5774-jms-primary-green-v1/source';abi=[]
    for path in sorted(MODIFIED):
        a=signature(prior,path);b=signature(snapshot,path)
        if not a<=b:raise ValueError('no public descriptor removed or changed')
        extra=b-a
        if path.endswith('/ArtemisReplyConsumers.java'):
            wanted={
             'descriptor: (Ldev/codex/schubert/nk/web/messaging/JmsContextFactory;Ldev/codex/schubert/nk/web/messaging/ArtemisReplyConsumer;Ljava/util/function/Consumer;Ljava/lang/Runnable;)Ldev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers;',
             'descriptor: (Ldev/codex/schubert/nk/web/messaging/ArtemisReplyConsumer;Ljava/util/function/Consumer;Ljava/lang/Runnable;)V'}
            if len(extra)!=2 or {descriptor for _,descriptor in extra}!=wanted:raise ValueError('only two declared additive fatal-signal overloads')
        elif extra:raise ValueError('all other existing public signatures unchanged')
        abi.append({'sourcePath':path,'removedPublicDescriptors':0,'addedPublicDescriptors':len(extra)})
    extra=signature(snapshot,ADDED)
    if len(extra)!=1 or {d for _,d in extra}!={'descriptor: (Ljava/lang/Throwable;Ljava/lang/Throwable;)V'}:raise ValueError('only the declared internal outcome constructor')
    return sources,classes,abi


def runner_source():
    raw=inspect.getsource(engine.main)
    replacements={
      "pg5774-jms-primary-green-v1/manifest.safe.json":"pg5800-rollback-selected54-v4/manifest.safe.json",
      "(v['tests'],v['suites'])==(14,7)":"(v['tests'],v['suites'])==(54,15)",
      "pg5750-exception-static-v1/manifest.safe.json":"pg5776-jms-primary-static-v1/manifest.safe.json",
      "provisional/PG5750-exception-static-v1/manifest.json":"provisional/PG5776-jms-primary-static-v1/manifest.json",
      '70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9':'aa0368e648a0d1e25d2413e9aa8c08966a30feeea5ea87b3841e78fc66abf72f',
      '    guards=guard_coverage(snapshot)':'    guards=v["targetCounters"]',
      ";expected_counts=Counter(old['ruleCounts']);expected_counts['CompareObjectsWithEquals']+=3":"",
      " and Counter(r['rule']for r in rows)==expected_counts":"",
      "'changedSourcePaths':sorted(PATHS)":"'changedSourcePaths':sorted(MODIFIED|{ADDED})",
      "'physicalMain':1664":"'physicalMain':1665",
      "'unchangedPhysicalClasses':1662":"'unchangedPhysicalClasses':1656",
      "'allFieldAndMethodDescriptorsUnchanged':True":"'publicAbi':abi,'removedPublicDescriptors':0,'declaredAdditionalOverloads':2",
      "'inputSourceFiles':849":"'inputSourceFiles':850",
      "'actualAuxClasses':1664":"'actualAuxClasses':1665",
      "'newGuardsActualCoverage':guards":"'selectedTargetActualCounters':guards",
      ",'newGuardsActualCoverage','F03Accepted'":",'selectedTargetActualCounters','F03Accepted'",
      'provisional/PG5776-jms-primary-static-v1\';target.mkdir()':'provisional/PG5804-rollback-static-v1\';target.mkdir()'}
    for old,new in replacements.items():
        if raw.count(old)!=1:raise ValueError('one exact current850 static runner predicate: '+old)
        raw=raw.replace(old,new,1)
    a=raw.index('    sources=');b=raw.index("    for name in('pmd.xml','checkstyle.xml'):",a)
    raw=raw[:a]+"    sources,classes,abi=pg_contract(snapshot,v,old)\n    current=v['allPhysicalMainSha256'];before_snapshot=W/'pg5774-jms-primary-green-v1/source'\n"+raw[b:]
    compile(raw,'<all850 rollback source actual static>','exec')
    return raw


def main():
    namespace={**vars(engine),'SLOT':'pg5804-rollback-static-v1','MODIFIED':MODIFIED,'ADDED':ADDED,'pg_contract':pg_contract}
    exec(compile(runner_source(),'<all850 rollback source actual static>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
