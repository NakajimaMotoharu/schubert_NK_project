"""Current70 source all six Jars, physical byte/owner join and unchanged architecture rules."""
import pg7032_monitoring_six_artifact_post as post
import pg7072_timed_filesystem_six_compile as compile_stage


if __name__=='__main__':
    post.compile_stage.SOURCE=compile_stage.SOURCE
    post.compile_stage.SLOT=compile_stage.SLOT
    post.SLOT=post.host.W/'pg7074-timed-filesystem-six-post-v1'
    post.OUT=post.host.BASE/'PG7074-timed-filesystem-six-post-v1'
    post.COMPONENT_FILE=post.host.BASE/'PG7070-timed-filesystem-post-v2/manifest.json'
    post.COMPONENT_SHA='55456e2cb24d49f35766b3a17179c56a0e133a484592235529eb4eb7f61ac25a'
    post.COMPONENT_TESTS=70
    post.TOTAL_PHYSICAL=1689
    post.NEW_PHYSICAL=20
    post.NEW_EXECUTABLE=19
    post.SOURCE_DELTA_COUNT=24
    prefix='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
    post.EXTRA_TEST_OWNERS={prefix+'SupplementaryUnitTemplateTest.java':'WBS-C02',
                            prefix+'ConfigurationTemplateContractTest.java':'WBS-C06'}
    post.main()
