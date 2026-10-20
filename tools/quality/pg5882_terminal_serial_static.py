"""Exact three serial receiver simplifications, all851/1666 bytes and unchanged static rules."""
import hashlib
import inspect
import re
import subprocess
import pg5776_jms_primary_static as engine
from pg5804_rollback_static import class_key,signature

OWNERS={
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/QuestionWorkConsumers.java':'result.terminal',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/WebLogConsumers.java':'runtime.terminal',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ArtemisReplyConsumers.java':'terminal'}
MODIFIED=set(OWNERS)
COMMENT='// This dedicated session serializes callbacks; halt excludes later deliveries.'


def expected_source(path,before):
    field=OWNERS[path];condition='if ('+field+'.compareAndSet(false, true))'
    if before.count(condition)!=2:raise ValueError('only two original dedicated-session notification guards')
    inline=re.compile(r'(?m)^([ ]*)'+re.escape(condition)+r' onTerminal\.accept\(fatal\);$')
    def replacement(match):
        indent=match.group(1)
        return indent+COMMENT+'\n'+indent+field+'.set(true);\n'+indent+'onTerminal.accept(fatal);'
    result=inline.sub(replacement,before);pattern=re.compile(r'(?m)^([ ]*)'+re.escape(condition)+r' \{\n')
    while(match:=pattern.search(result)):
        indent=match.group(1);end=result.index('\n'+indent+'}',match.end());body=result[match.end():end];lines=body.splitlines()
        if any(line and not line.startswith(indent+'  ')for line in lines):raise ValueError('exact known block indentation')
        unwrapped='\n'.join(line[2:]if line else line for line in lines)
        if body.strip()=='onTerminal.accept(fatal);':prefix=indent+COMMENT+'\n'
        elif 'onFatal.run();'in body and 'if (fatal instanceof Error)'in body:prefix=''
        else:raise ValueError('only committed or existing infrastructure notification')
        result=result[:match.start()]+prefix+indent+field+'.set(true);\n'+unwrapped+result[end+1+len(indent)+1:]
    if condition in result or result.count(field+'.set(true);')!=2 or result.count(COMMENT)!=1:raise ValueError('exact two unconditional serialized decisions')
    return result


def pg_contract(snapshot,value,old):
    sources={p.relative_to(snapshot).as_posix():engine.sha(p)for p in snapshot.glob('src/*/src/main/java/**/*.java')};before=old['allSourceHashes']
    if len(sources)!=851 or set(sources)!=set(before)or{p for p in sources if sources[p]!=before[p]}!=MODIFIED:raise ValueError('only three serialized receiver sources')
    prior=engine.W/'pg5856-terminal-selected81-v3/source'
    for path,digest in sources.items():
        if hashlib.sha256(subprocess.check_output(['git','show',value['source']+':'+path],cwd=engine.ROOT)).hexdigest()!=digest:raise ValueError('canonical compile source')
    for path in MODIFIED:
        if expected_source(path,(prior/path).read_text())!=(snapshot/path).read_text()or signature(prior,path)!=signature(snapshot,path):raise ValueError('only serialized decision simplification; ABI unchanged')
    oldmap,new=old['auxClassHashes'],value['allPhysicalMainSha256'];changed={k for k in oldmap if k in new and oldmap[k]!=new[k]};classes={class_key(p)for p in MODIFIED}
    if len(oldmap)!=1666 or len(new)!=1666 or set(oldmap)!=set(new)or changed!=classes:raise ValueError('exact three Main class differences;1663 unchanged')
    return sources,sorted(classes)


def runner_source():
    raw=inspect.getsource(engine.main)
    changes={'pg5774-jms-primary-green-v1/manifest.safe.json':'pg5880-terminal-serial83-v1/manifest.safe.json',"(v['tests'],v['suites'])==(14,7)":"(v['tests'],v['suites'])==(83,22)",'pg5750-exception-static-v1/manifest.safe.json':'pg5858-terminal-static-v1/manifest.safe.json','provisional/PG5750-exception-static-v1/manifest.json':'provisional/PG5858-terminal-static-v1/manifest.json','70e765032b899a377bd1067846d158496373aec901de559dc0baeaac2121d5d9':'4e5b6cb920bbc01334c6d1ef81f0042db10ca9fe5bbce8a920e2d7bd770cccdf','    guards=guard_coverage(snapshot)':'    guards=v["targetCounters"]',";expected_counts=Counter(old['ruleCounts']);expected_counts['CompareObjectsWithEquals']+=3":";expected_counts=Counter(old['ruleCounts'])","'changedSourcePaths':sorted(PATHS)":"'changedSourcePaths':sorted(MODIFIED)","'physicalMain':1664":"'physicalMain':1666","'unchangedPhysicalClasses':1662":"'unchangedPhysicalClasses':1663","'allFieldAndMethodDescriptorsUnchanged':True":"'existingPublicAbiUnchanged':True,'removedPublicDescriptors':0,'addedPublicDescriptors':0","'inputSourceFiles':849":"'inputSourceFiles':851","'actualAuxClasses':1664":"'actualAuxClasses':1666","'newGuardsActualCoverage':guards":"'selectedTargetActualCounters':guards",",'newGuardsActualCoverage','F03Accepted'":",'selectedTargetActualCounters','F03Accepted'","provisional/PG5776-jms-primary-static-v1';target.mkdir()":"provisional/PG5882-terminal-serial-static-v1';target.mkdir()"}
    for old,new in changes.items():
        if raw.count(old)!=1:raise ValueError('one current serialized static binding')
        raw=raw.replace(old,new,1)
    a=raw.index('    sources=');b=raw.index("    for name in('pmd.xml','checkstyle.xml'):",a)
    raw=raw[:a]+"    sources,classes=pg_contract(snapshot,v,old)\n    current=v['allPhysicalMainSha256'];before_snapshot=W/'pg5856-terminal-selected81-v3/source'\n"+raw[b:]
    compile(raw,'<all851/1666 serialized static>','exec');return raw


def main():
    scope={**vars(engine),'SLOT':'pg5882-terminal-serial-static-v1','MODIFIED':MODIFIED,'pg_contract':pg_contract}
    exec(compile(runner_source(),'<all851/1666 serialized static>','exec'),scope)
    return scope['main']()


if __name__=='__main__':raise SystemExit(main())
