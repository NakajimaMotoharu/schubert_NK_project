"""Whole Caddy public grammar class, exact unchanged Main, no service/VM operation."""
import inspect
import pg3044_expiry_boundary_selected as base

TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CaddyPublicConfigurationTest.java'
FILES = [TEST, 'tools/quality/vm/050_s1/SelectedClassContractLauncher.java', 'tools/quality/vm/050_s1/NativeCoverageXml471.java']


def server():
    raw = base.server().replace('PG3044', 'PG3050').replace('ExpiryWorkerRequestTest', 'CaddyPublicConfigurationTest').replace('platform.CaddyPublicConfigurationTest', 'file.CaddyPublicConfigurationTest')
    start = raw.index("{'ereq3042001")
    end = raw.index('}.issubset(names)', start)
    raw = raw[:start] + "{'caddy455006Ipv4Ipv6AndFormattingRemainTlsOnly','caddy455007AnyUnexpectedDirectiveOrAddressFailsClosed','caddy455008DeploymentTemplateMatchesIndependentDirectiveSet'" + raw[end:]
    raw = raw.replace('dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry$PriorExpiry', 'dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration')
    # Existing template oracle resolves ../deployment relative to the batch module.
    raw = raw.replace('capture_output=True,timeout=timeout,env=env)', "capture_output=True,timeout=timeout,env=env,cwd=source/'src/schubert-nk-batch')")
    compile(raw, '<complete Caddy grammar and original template fixture>', 'exec')
    return raw


def main():
    raw = inspect.getsource(base.main).replace('pg3044-expiry-boundary-selected-v1', 'pg3050-caddy-grammar-selected-v1').replace('PG3044-candidate-v1', 'PG3050-candidate-v1')
    ns = {**base.__dict__, 'FILES': FILES, 'TEST': TEST, 'server': server}
    exec(compile(raw, '<fixed Caddy Test input>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
