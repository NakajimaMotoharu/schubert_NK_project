"""Fixed new Web/Batch private standard SDK sources normal six build; PT0 unrun here."""
import pg8504_web_batch_jvm_six_compile as template

if __name__ == '__main__':
    stage=template.previous.stage
    stage.SOURCE='4c97764a913a09fd39d9881eb6e112e66c1547e3'
    stage.SLOT=stage.host.W/'pg8710-web-batch-standard-source-fixed-six-compile-v1'
    stage.OUT=stage.host.BASE/'PG8710-web-batch-standard-source-fixed-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    prepared=stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared)=='1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    rows=template.previous.json.loads(prepared.read_text())['entries']
    stage.DEPENDENCY_JARS={**template.previous.sdk.DEPENDENCIES,**{row['path']:row['sha256'] for row in rows if template.previous.Path(row['path']).suffix=='.jar'}}
    selection=stage.host.BASE/'PG8705-web-batch-external-import-preflight-v1/manifest.json'
    assert stage.host.sha(selection)=='fac825aca5eb0b8359327b48d248a536a186e53157233761dfd2ff66d05fa7df'
    preflight=template.previous.json.loads(selection.read_text())
    assert preflight['source']==stage.SOURCE and preflight['actualExit']==0 and len(preflight['negativeGuards'])==12
    assert all(stage.host.sha(stage.host.ROOT/row['path'])==row['sha256'] for row in preflight['sourceRows'])
    stage.main()
