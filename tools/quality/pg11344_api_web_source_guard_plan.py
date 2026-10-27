"""API/Web fixed-mode literals and28 Test-owner guards/two executor TWR; no Main changes."""
import difflib
import json
from pathlib import Path
import re
import sys
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
from pg10398_role_view_preflight import canonical
from pg10840_web_view_duplicate_plan import transformed as strings
from pg11318_batch_source_guard_plan import body_span,owner_end

OUT=data.BASE/'PG11344-api-web-source-guard-plan-v1'
FILES=['src/schubert-nk-'+role+'/src/test/java/dev/codex/schubert/nk/'+role+'/monitoring/'+stem+'StandardMetricSourceTest.java'
    for role,stem in [('api','Api'),('web','Web')]]
NAMES={'DEBUG':'DEBUG_MODE','STANDARD':'STANDARD_MODE'}


def inputs():
    normal=data.read_checked(data.BASE/'PG11322-batch-source-guard-six-compile-v1/manifest.json',
        '066e1c301187c43224e8ab120c50889ef8a832f48de3fe4406aa7e533ac14e27')
    assert normal['actualExit']==normal['testsExecuted']==0
    snapshot=Path(normal['jars']['protocol']['path']).parent.parent.parent.parent
    original=data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    table={}
    for path in FILES:
        before=(snapshot/path).read_text()
        rows=[r for r in original if r['path']==path and r['rule']=='AvoidDuplicateLiterals']
        assert len(rows)==2
        constants=[]
        for row in rows:
            assert data.sha(before.encode())==row['inputSha256']==normal['begin']['inputHashes'][path]
            match=re.fullmatch(r'The String literal "(.*)" appears ([0-9]+) times in this file; the first occurrence is on line [0-9]+',row['message'])
            assert match and match[1] in NAMES
            literal=json.dumps(match[1])
            found=[m for m in LEX.finditer(before) if m.group()==literal]
            assert len(found)==int(match[2]) and before[:found[0].start()].count('\n')+1==row['line']
            name=NAMES[match[1]]
            assert name not in canonical(before)
            constants.append(dict(id=row['id'],name=name,literal=literal,references=len(found)))
        cases=re.findall(r'@Test\s+void (\w+)\(\)',before)
        assert len(cases)==len(set(cases))==16
        guarded=[n for n in cases if 'host002' not in n and 'host005' not in n]
        assert len(guarded)==14
        for n in guarded:
            a,b=body_span(before,n)
            compact=''.join(canonical(before[a:b]))
            assert 'owner.close();' in compact
            if 'host016' in n:
                assert 'varexecutor=Executors.newFixedThreadPool(2);try{' in compact
            else:
                assert 'finally' not in canonical(before[a:b])
        table[path]=dict(constants=constants,guardedMethods=guarded,cases=cases)
    return normal,snapshot,table


def transformed(before,stem,item):
    text=strings(before,stem,item['constants'])
    result=text
    for start,end,name in sorted(((*body_span(text,n),n) for n in item['guardedMethods']),reverse=True):
        body=text[start:end]
        split=owner_end(body)
        prefix,rest=body[:split],body[split:]
        if 'host016' in name:
            old='    var executor = Executors.newFixedThreadPool(2);\n    try {'
            assert rest.count(old)==1
            rest=rest.replace(old,'    try (var executor = Executors.newFixedThreadPool(2)) {\n    try {',1)
            rest=rest.rstrip()+'\n    }\n'
        wrapped=prefix+'\n    try {\n'+rest.lstrip('\n').rstrip()+'\n    } finally {\n      owner.close();\n    }\n  '
        result=result[:start]+wrapped+result[end:]
    return result


def emit():
    _,snapshot,table=inputs()
    patch='*** Begin Patch\n'
    for path,item in table.items():
        before=(snapshot/path).read_text()
        assert (data.ROOT/path).read_text()==before
        after=transformed(before,Path(path).stem,item)
        diff=list(difflib.unified_diff(before.splitlines(),after.splitlines(),n=3))[2:]
        patch+='*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if x.startswith('@@') else x for x in diff)+'\n'
    return patch+'*** End Patch\n'


def main():
    invocation=capture(__file__)
    assert not OUT.exists()
    normal,snapshot,table=inputs()
    assert all(data.sha((data.ROOT/p).read_bytes())==h for p,h in normal['begin']['inputHashes'].items() if p not in table)
    changes=[]
    for path,item in table.items():
        before,after=(snapshot/path).read_text(),(data.ROOT/path).read_text()
        assert canonical(after)==canonical(transformed(before,Path(path).stem,item))
        changes.append(dict(path=path,beforeSha256=data.sha(before.encode()),sha256=data.sha(after.encode()),**item))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,sourceBefore=normal['source'],invocation=invocation,
        sourceChanges=changes,stringConstants=4,referencesReplaced=sum(r['references'] for x in table.values() for r in x['constants']),
        ownerGuards=28,executorTwr=2,originalMethods=32,originalSuites=2,allMainAndOtherInputBytesPreserved=True,
        originalOracleInversePending=True,productTestsExecuted=0,coverage=None,externalActions=0,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__=='__main__':
    if sys.argv[1:]==['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:]
        main()
