"""Exact same-source54 Jar byte join, every source delta and static dependency rules."""
import pg7032_monitoring_six_artifact_post as post
import pg7048_monitoring_status_six_compile as compile_stage


if __name__ == '__main__':
    post.compile_stage.SOURCE = compile_stage.SOURCE
    post.compile_stage.SLOT = compile_stage.SLOT
    post.SLOT = post.host.W/'pg7050-monitoring-status-six-post-v1'
    post.OUT = post.host.BASE/'PG7050-monitoring-status-six-post-v1'
    post.COMPONENT_FILE = post.host.BASE/'PG7046-monitoring-status-post-v1/manifest.json'
    post.COMPONENT_SHA = 'bdee1eecf46db2f6df358c80c344d12e04463414d09e9cc1c77e8068bd62ea74'
    post.COMPONENT_TESTS = 54
    post.TOTAL_PHYSICAL = 1685
    post.NEW_PHYSICAL = 16
    post.NEW_EXECUTABLE = 15
    post.SOURCE_DELTA_COUNT = 19
    prefix = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'
    post.EXTRA_TEST_OWNERS = {
      prefix+'SupplementaryUnitTemplateTest.java':'WBS-C02',
      prefix+'ConfigurationTemplateContractTest.java':'WBS-C06'}
    post.main()
