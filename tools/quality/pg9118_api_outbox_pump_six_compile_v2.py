"""New SDK-independent API Outbox source normal six compile; PT0 and no Main/DB/JMS action."""
import pg8504_web_batch_jvm_six_compile as template

if __name__=='__main__':
    stage=template.previous.stage
    stage.SOURCE='f82e3e1ee6d6090b1b81222d18fd35366d0637c1'
    stage.SLOT=stage.host.W/'pg9118-api-outbox-pump-six-compile-v2'
    stage.OUT=stage.host.BASE/'PG9118-api-outbox-pump-six-compile-v2'
    stage.CAPTURE_TEST_CLASSPATH=True
    prepared=stage.host.BASE/'PG8669-standard-sdk-parent-coordinates-v1/manifest.json'
    assert stage.host.sha(prepared)=='1b23b96e7eebf79da8ebe0991e6a47d322bd71e6e67d6e9ce6c9f335a2a1da17'
    rows=template.previous.json.loads(prepared.read_text())['entries']
    stage.DEPENDENCY_JARS={**template.previous.sdk.DEPENDENCIES,**{row['path']:row['sha256'] for row in rows if template.previous.Path(row['path']).suffix=='.jar'}}
    stage.main()
