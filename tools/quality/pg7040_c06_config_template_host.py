"""Four new source-template cases, not a runtime parser or actual deployment operation."""
import pg7036_c02_four_template_host as runner

FILES = ('common.yml.template','api.yml.template','web.yml.template','batch.yml.template',
         'api.env.template','web.env.template','inbox-inspector.env.template')
METHODS = {'configSup001AllElevenBatchDefaults','configSup002CommonCrossProcessAndLexicalRootBoundaries',
           'configSup003DedicatedEnvAndInspectorRenderBoundary','configSup004IndependentSourceOracleMutationCanaries'}
SLOT = runner.host.W/'pg7040-c06-config-template-host-v1'
SUITE = 'dev.codex.schubert.nk.batch.platform.ConfigurationTemplateContractTest'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ConfigurationTemplateContractTest.java'
POM = 'tools/quality/harnesses/config-template-pom.xml'


if __name__=='__main__':
    runner.SLOT = SLOT
    runner.OUT = runner.host.BASE/'PG7040-c06-config-template-host-v1'
    runner.POM = POM
    runner.SUITE = SUITE
    runner.TEST = TEST
    runner.FILES = FILES
    runner.METHODS = METHODS
    runner.RESOURCE_DIRECTORY = 'config'
    runner.TARGET_DIRECTORY = 'target-config-template'
    runner.main()
