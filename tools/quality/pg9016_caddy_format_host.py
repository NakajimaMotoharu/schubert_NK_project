"""New config source ordinary parser three tests; no Root/native/TLS test extraction or execution."""
import re
import scoped_configuration_host as run
SOURCE='f690fa6be336550f8078e2bdde40ef34ab5efe6b'
if __name__=='__main__':
    run.SOURCE=SOURCE
    run.COMPILE=run.host.W/'pg9014-caddy-format-six-compile-v1'
    run.COMPILE_SHA='01bad7736bbef335cb0b8dee60947e5767d57180bb59c631ae4ea9374058c18c'
    run.SLOT=run.host.W/'pg9016-caddy-format-host-v1'
    run.OUT=run.host.BASE/'PG9016-caddy-format-host-v1'
    run.HELPER=run.host.ROOT/'tools/quality/architecture/CaddyFormatJunitLauncher.java'
    run.NEW_TEST=run.host.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CaddyPublicConfigurationTest.java'
    run.COUNTS={'CaddyPublicConfigurationTest':3}
    run.SESSION_ID='PG9016-CADDY-FORMAT'
    run.FIXTURES={}
    assert run.NEW_TEST.read_text().count('@Test')==3
    assert set(re.findall(r'void\s+(caddy455\d{3}[A-Za-z0-9]+)\(',run.NEW_TEST.read_text()))=={'caddy455006Ipv4Ipv6AndFormattingRemainTlsOnly','caddy455007AnyUnexpectedDirectiveOrAddressFailsClosed','caddy455008DeploymentTemplateMatchesIndependentDirectiveSet'}
    run.main()
