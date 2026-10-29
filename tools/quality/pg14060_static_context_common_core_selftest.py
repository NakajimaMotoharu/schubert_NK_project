"""Tool-only pure fixtures: no Product classes/tests, filesystem fixtures, Java, VM or service calls."""
import copy
import hashlib
import static_context_reader_v1 as reader
import static_context_post_v1 as post
from host_tool_invocation import capture,verify

OUT=reader.data.BASE/'PG14060-static-context-common-core-tool-selftest-v1'
NAME='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/T.java'
TEXT='final class T {\n  private final Object lock = new Object();\n  void f() {\n    synchronized (lock) {}\n  }\n}\n'
DOC='documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'
def sha(v):return hashlib.sha256(v.encode()).hexdigest()
def fixture(text=TEXT,rule='AvoidSynchronizedStatement'):
    target=dict(sha256=sha(text),owner=None,ids=['PMD-00001'],reason='Synthetic tool metadata, never a Product source result',guards=['private final Object lock = new Object();','synchronized (lock)'],ordered=[['private final Object lock = new Object();','synchronized (lock)']],prefixLines=None,prefixSha256=None,monitor='lock')
    plan=dict(out='PG99990-tool-only-metadata',record='evidence/01_PT/018_NK-OPS-001/2565_共通静的context工具_実装・自己試験仕様.md',rule=rule,targets={NAME:target},design={DOC:'a'*64})
    attrs=dict(beginline='4',endline='4',begincolumn='5',endcolumn='17',rule=rule,method='f',**{'class':'T'})
    catalog=[dict(id='PMD-00001',path=NAME,rule=rule,inputSha256=sha(text),attributes=attrs,rowSha256='b'*64)]
    facts=[dict(path=NAME,rule=rule,sourceSha256=sha(text),attributes=attrs)]
    owners={NAME:dict(canonicalOwner=None,canonicalCostOwner=None,ownershipStatus='UNKNOWN',basis='SYNTHETIC_TOOL_FIXTURE_ONLY')}
    return plan,catalog,facts,{NAME:text},owners
def main():
    invocation=capture(__file__);assert not OUT.exists()
    positives=[];negatives=[]
    def rejected(label,action):
        try:action()
        except ValueError:negatives.append(label)
        else:raise AssertionError('invalid pure tool fixture accepted: '+label)
    data=fixture();plan,catalog,facts,texts,owners=data
    assert reader.validate_plan(plan)=={'PMD-00001'};positives.append('exact-plan')
    row,=reader.bind_rows(*data)
    assert row['id']=='PMD-00001' and row['typeToken']=='synchronized' and row['occurrenceOrdinal']==0
    post.preserved_truth(row);positives.append('raw-binding-and-typed-pending')
    start,end,token=post.independent_location(TEXT,catalog[0]['attributes'])
    assert TEXT[start:end]==token=='synchronized' and (start,end)==(77,89);positives.append('independent-location-golden')
    dup=copy.deepcopy(data);dup[0]['targets'][NAME]['ids'].append('PMD-00002');dup[1].append({**copy.deepcopy(dup[1][0]),'id':'PMD-00002','rowSha256':'c'*64});dup[2].append(copy.deepcopy(dup[2][0]))
    rows=reader.bind_rows(*dup);assert len(rows)==2 and [r['occurrenceOrdinal'] for r in rows]==[0,1] and all(r['rawDiagnosticMultiplicity']==2 for r in rows);positives.append('duplicate-two-retained')
    dropped=copy.deepcopy(dup);dropped[0]['targets'][NAME]['ids'].pop();rejected('duplicate-not-deduplicated',lambda:reader.bind_rows(*dropped))
    generic='final class T {\n  void f() { try {\n  } catch (RuntimeException failure) {}\n  }\n}\n'
    gen=fixture(generic,'AvoidCatchingGenericException');gen[0]['targets'][NAME].update(guards=['catch (RuntimeException failure)'],ordered=[],monitor=None)
    for v in [gen[1][0]['attributes'],gen[2][0]['attributes']]:v.update(beginline='3',endline='3',begincolumn='12',endcolumn='28')
    g,=reader.bind_rows(*gen);assert g['typeToken']=='RuntimeException';positives.append('generic-catch-bounded-token')
    suffix=TEXT+'// '+chr(92)+'u2028'+chr(10);pre=fixture(suffix);prefix=''.join(suffix.splitlines(keepends=True)[:4])
    pre[0]['targets'][NAME].update(prefixLines=4,prefixSha256=sha(prefix))
    p,=reader.bind_rows(*pre);assert p['coordinateScope']['prefixLines']==4 and p['coordinateScope']['wholeJavaUnicodeTranslationValidated'] is False
    assert post.independent_location(suffix,pre[1][0]['attributes'],4,sha(prefix))==(start,end,'synchronized');positives.append('original-prefix-only')
    calls=[]
    def spy(name):calls.append(name);return TEXT.encode()
    assert reader.read_known(NAME,{NAME:sha(TEXT)},spy)==TEXT.encode() and calls==[NAME];positives.append('known-public-read-spy')
    for bad in [*sorted(reader.HELD),'../private/data','/private/data','src/../private/data','unknown-file']:
        known={NAME:sha(TEXT)} if bad=='unknown-file' else {bad:sha(TEXT)}
        before=len(calls);rejected('no-io:'+bad,lambda bad=bad,known=known:reader.read_known(bad,known,spy));assert len(calls)==before
    relation={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/Foo.java':'d'*64}
    imports=reader.related_scope('import dev.codex.schubert.nk.api.Foo.Inner;\n',relation)
    assert imports['dev.codex.schubert.nk.api.Foo.Inner']['path'] in relation;positives.append('nested-type-source-import-not-execution')
    rejected('unknown-nk-import',lambda:reader.related_scope('import dev.codex.schubert.nk.api.Missing;\n',relation))
    mutations=[
      ('extra-permission-key',lambda p:p.update(qualityGatePass=True)),
      ('unsafe-output',lambda p:p.update(out='../../private')),
      ('unsafe-record',lambda p:p.update(record='/private/data')),
      ('unsupported-rule',lambda p:p.update(rule='Other')),
      ('duplicate-id',lambda p:p['targets'][NAME]['ids'].append('PMD-00001')),
      ('malformed-id',lambda p:p['targets'][NAME].update(ids=['UNKNOWN'])),
      ('boolean-prefix',lambda p:p['targets'][NAME].update(prefixLines=True,prefixSha256='a'*64)),
      ('prefix-without-hash',lambda p:p['targets'][NAME].update(prefixLines=4)),
      ('no-reason',lambda p:p['targets'][NAME].update(reason='')),
      ('no-guard',lambda p:p['targets'][NAME].update(guards=[])),
      ('unknown-target-field',lambda p:p['targets'][NAME].update(runtimeAllowed=True)),
      ('monitor-expression',lambda p:p['targets'][NAME].update(monitor='this.lock')),
      ('missing-monitor',lambda p:p['targets'][NAME].update(monitor=None)),
      ('unsafe-design',lambda p:p.update(design={'../private.md':'a'*64})),
    ]
    for label,change in mutations:
        bad=copy.deepcopy(plan);change(bad);assert reader.wire(bad)!=reader.wire(plan)
        rejected(label,lambda bad=bad:reader.validate_plan(bad))
    for label,mutate in [
      ('wrong-owner',lambda d:d[0]['targets'][NAME].update(owner='WBS-F03')),
      ('missing-original',lambda d:d[0]['targets'][NAME].update(ids=['PMD-00003'])),
      ('wrong-source',lambda d:d[3].update({NAME:TEXT+' '})),
      ('missing-current-xml',lambda d:d[2].clear()),
      ('wrong-original-input',lambda d:d[1][0].update(inputSha256='0'*64)),
      ('owner-runtime-override',lambda d:d[4][NAME].update(qualityGatePass=True)),
    ]:
        bad=copy.deepcopy(data);mutate(bad);rejected(label,lambda bad=bad:reader.bind_rows(*bad))
    for key,value in [('rawRetained',False),('rawRetained',0),('currentWholeJoinPending',False),('sourceChanged',True),('nativeRuntimeProven',True),('qualityGatePass',True),('productTestsExecuted',False),('productTestsExecuted',None),('productTestsExecuted',1)]:
        bad=copy.deepcopy(row);bad[key]=value;assert reader.wire(bad)!=reader.wire(row)
        rejected('truth:'+key+':'+type(value).__name__,lambda bad=bad:post.preserved_truth(bad))
    for field,value in [('beginline','0'),('begincolumn','0'),('endcolumn','999'),('beginline',True),('endcolumn',17),('endline','5')]:
        attrs=copy.deepcopy(catalog[0]['attributes']);attrs[field]=value
        rejected('coordinate:'+field+':'+type(value).__name__,lambda attrs=attrs:post.independent_location(TEXT,attrs))
    rejected('whole-source-unicode-unproved',lambda:post.independent_location(suffix,catalog[0]['attributes']))
    rejected('prefix-digest',lambda:post.independent_location(suffix,catalog[0]['attributes'],4,'0'*64))
    rejected('prefix-before-target',lambda:post.independent_location(suffix,catalog[0]['attributes'],3,sha(''.join(suffix.splitlines(keepends=True)[:3]))))
    target=plan['targets'][NAME]
    for phrase in target['guards']:
        rejected('removed-guard:'+phrase,lambda phrase=phrase:reader.guard_text(target,TEXT.replace(phrase,'REMOVED')))
    reversed_target=copy.deepcopy(target);reversed_target['ordered'][0].reverse()
    rejected('source-order',lambda:reader.guard_text(reversed_target,TEXT))
    verify(invocation);OUT.mkdir()
    reader.data.write(OUT/'manifest.json',dict(actualExit=0,source=reader.cfg.SOURCE,invocation=invocation,toolPositiveVectors=len(positives),positiveLabels=positives,toolNegativeVectors=len(negatives),negativeLabels=negatives,pureMetadataFixturesOnly=True,filesystemFixtureCreated=False,productTestsExecuted=0,productClassesLoaded=False,oldSuccessfulContextReplayed=False,currentContext22Replayed=False,actualExternalActions=0,coverage=None,newAccepted=0,formalUpdated=False,effortPercent=None,toolStatus='PURE_CORE_QUALIFIED_FIRST_NEW_CONTEXT_IO_POST_PENDING',whole451Accepted=False))
    print(reader.data.sha((OUT/'manifest.json').read_bytes()))
    print(reader.wire(dict(positive=len(positives),negative=len(negatives),productTestsExecuted=0)))
if __name__=='__main__':main()
