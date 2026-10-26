"""Five exact raw findings, source-only validation-effect/fixture classification; no target execution."""
from pathlib import Path
import re
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10726-json-peek-locale-context-v1'
DECISIONS = 'documents/400_PGPT/440_判断/441_実装判断記録.md'
LIBRARY_STUDY = 'tools/quality/vm/050_s1/Pg2498GsonStrictEndContract.java'
GSON_SHA = '2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f'


def parser_context(text,line):
    lines = text.splitlines()
    if not lines[line-1].strip().startswith('reader.peek();'):
        raise ValueError('exact ignored EOF peek statement required')
    prefix = '\n'.join(lines[:line])
    if 'import com.google.gson.stream.JsonReader;' not in text or 'import com.google.gson.Strictness;' not in text:
        raise ValueError('pinned actual Gson types required')
    if len(re.findall(r'reader\.setStrictness\(',text)) != 1 or 'reader.setStrictness(Strictness.STRICT);' not in prefix:
        raise ValueError('one fixed STRICT reader required')
    if prefix.rfind('reader.endObject();') < prefix.rfind('reader.beginObject();'):
        raise ValueError('complete root object before mandatory validation peek')
    return dict(kind='INTENTIONAL_STRICT_EOF_VALIDATION_EFFECT_NOT_UNUSED_PURE_VALUE',
        actualStatement=lines[line-1].strip(),fullCaseOrRuntimeQualified=False)


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG10714-graph-constants-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'b24ac5ef1f85b9ed935e0772ef04040acbd12b78f573a88aa4d9420ae4995676')
    global_path = data.BASE/'PG10690-current-global-static-post-v1/manifest.json'
    global_meta = data.read_checked(global_path,'465c7c64bc75923d275436c72656ddc5b537f2c15982a71a0b4681a19ef03627')
    findings = data.read_checked(global_path.parent/'findings.json',global_meta['findingsSha256'])
    selected = [r for r in findings if r['rule'] in ('UnusedReturnValue','UseLocaleWithCaseConversions')]
    assert len(selected) == 5
    static_meta = data.read_checked(data.BASE/'PG10688-current-global-static-v1/manifest.json',
        'd91104d420967cd34c0d313919b86c7f1745577a1e1fe31d9343927d53dfe636')
    jar, = [p for p in static_meta['dependencyHashes'] if '/gson/' in p]
    assert static_meta['dependencyHashes'][jar] == data.sha(Path(jar).read_bytes()) == GSON_SHA
    with zipfile.ZipFile(jar) as archive:
        class_sha = data.sha(archive.read('com/google/gson/stream/JsonReader.class'))
    decisions = (data.ROOT/DECISIONS).read_text()
    start = decisions.index('## PG-D416')
    end = decisions.index('\n## ',start+1)
    decision = decisions[start:end]
    assert GSON_SHA in decision and 'NONEMPTY_DOCUMENT' in decision and 'checkLenient' in decision
    study = (data.ROOT/LIBRARY_STUDY).read_text()
    assert 'strictEOF4 trailingRejected11 lenientControls2 productionCoverage0' in study
    rows = []
    for original in selected:
        path = original['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == original['inputSha256'] == normal['begin']['inputHashes'][path]
        if original['rule'] == 'UnusedReturnValue':
            review = parser_context(text,original['line'])
            status = 'NOT_APPLICABLE_PURE_UNUSED_RESULT_RULE_TO_REQUIRED_STRICT_VALIDATION_EFFECT'
        else:
            assert path.endswith('/SemanticFieldValueTest.java') and original['line'] == 129
            assert 'UUID_TEXT.toUpperCase()' in text and '123e4567-e89b-12d3-a456-426614174000' in text
            review = dict(kind='EXPLICIT_UPPERCASE_UUID_TEST_VECTOR_NEEDED_FOR_STYLE_INDEPENDENCE',
                observedLocaleFailure=False,productionBehaviorFailure=False,fullCaseOrRuntimeQualified=False)
            status = 'APPLICABLE_TEST_FIXTURE_STYLE_PG_PENDING'
        rows.append(dict(originalFinding=original,sourceSha256=original['inputSha256'],status=status,review=review,
            dynamicQualification=False,productTestsExecuted=0))
    assert sum(r['status'].startswith('NOT_APPLICABLE') for r in rows) == 4
    samples = [('reader.setStrictness(Strictness.LENIENT);\nreader.endObject();\nreader.peek();',3),
        ('reader.setStrictness(Strictness.STRICT);\nreader.beginObject();\nreader.peek();',3)]
    for text,line in samples:
        try:
            parser_context('import com.google.gson.stream.JsonReader;\nimport com.google.gson.Strictness;\n'+text,line+2)
        except ValueError:
            pass
        else:
            raise AssertionError('nonfixed/incomplete parser accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',rows)
    data.write(OUT/'historical-library-contract-reference.json',dict(decisionPath=DECISIONS,section='PG-D416',
        sectionText=decision,sectionSha256=data.sha(decision.encode()),studySource=LIBRARY_STUDY,
        studySourceSha256=data.sha(study.encode()),gsonJar=jar,gsonJarSha256=GSON_SHA,jsonReaderClassSha256=class_sha,
        oldLibraryVectorsNotReexecuted=True,oldProductionResultsNotReassigned=True))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        originalIndexManifestSha256=data.sha(global_path.read_bytes()),rowsSha256=data.sha((OUT/'contexts.json').read_bytes()),
        libraryReferenceSha256=data.sha((OUT/'historical-library-contract-reference.json').read_bytes()),
        rawFindingSites=5,validationEffectContextNotApplicable=4,fixtureLocaleStylePending=1,metadataNegativeVectors=2,
        productTestsExecuted=0,targetProductCodeExecuted=False,libraryContractReexecuted=False,coverage=None,
        externalActions=0,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
