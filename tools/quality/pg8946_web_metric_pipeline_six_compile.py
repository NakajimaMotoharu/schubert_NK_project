"""New caller-held metric contexts normal six build; PT0 unrun here."""
import pg8504_web_batch_jvm_six_compile as template

if __name__ == '__main__':
    stage=template.previous.stage
    stage.SOURCE='fb9fce0f91de3d9fdfa634fe277592700f915e45'
    stage.SLOT=stage.host.W/'pg8946-web-metric-pipeline-six-compile-v1'
    stage.OUT=stage.host.BASE/'PG8946-web-metric-pipeline-six-compile-v1'
    stage.CAPTURE_TEST_CLASSPATH=True
    prepared=stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared)=='1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    rows=template.previous.json.loads(prepared.read_text())['entries']
    stage.DEPENDENCY_JARS={**template.previous.sdk.DEPENDENCIES,**{row['path']:row['sha256'] for row in rows if template.previous.Path(row['path']).suffix=='.jar'}}
    stage.main()
