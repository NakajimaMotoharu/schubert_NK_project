"""Correct only future summary rendering; preserve the actually qualified original tool/run."""
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    base = data.BASE/'PG10177-cancel-source-quality-post-v2'
    out = data.BASE/'PG10179-cancel-summary-binding-v1'
    assert not out.exists()
    value = data.read_checked(base/'manifest.json','53b5cd969c1531b63772cdb50a211d48b776e6de2acded15f5609d75b810b989')
    original = (base/'qualified-original-tool.py').read_bytes()
    assert data.sha(original) == value['invocation']['entrypointSha256']
    before = '''    print(json.dumps(dict(actualExit=0,mainUnchanged=1843,otherTestUnchanged=1930,
'''
    after = '''    saved = json.loads((out/'manifest.json').read_bytes())
    print(json.dumps(dict(actualExit=saved['actualExit'],mainUnchanged=saved['mainClassesByteIdentical'],
        otherSourceTestUnchanged=saved['otherSourceTestClassesByteIdentical'],generatedDebugOnly=saved['generatedClassDebugOnly'],
'''
    assert original.decode().count(before) == 1
    assert (data.ROOT/'tools/quality/pg10177_cancel_source_quality_post_v2.py').read_text() == original.decode().replace(before,after)
    assert value['otherSourceTestClassesByteIdentical'] == 1929 and value['changedSourcePhysicalTestClasses'] == 2
    assert value['generatedClassDebugOnly'] and value['actualExit'] == 0
    verify(invocation)
    out.mkdir()
    data.write(out/'manifest.json',dict(actualExit=0,source=value['source'],invocation=invocation,
        qualifiedOriginalSourceSha256=data.sha(original),originalResultSha256='53b5cd969c1531b63772cdb50a211d48b776e6de2acded15f5609d75b810b989',
        otherSourceTestClassesByteIdentical=1929,changedSourcePhysicalTestClasses=2,generatedClassDebugOnly=True,
        originalSummary1930PreservedAsHistoricalWrongDisplay=True,allNonDisplayToolBytesUnchanged=True,
        productTestsExecuted=0,externalActions=0,newAccepted=0,formalUpdated=False))
    print(data.sha((out/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
