"""New immutable result slot after BUG1220; same completed PG2228, no Maven replay."""
import inspect
import pg2229_root_host_integration_full_qualification as qualification


def main():
    raw=inspect.getsource(qualification.main).replace('pg2229-root-host-integration-full-qualified-v1','pg2236-root-host-integration-full-qualified-v1')
    namespace={**qualification.__dict__}
    exec(compile(raw,'<corrected test-only full integration qualifier>','exec'),namespace)
    return namespace['main']()


if __name__=='__main__':raise SystemExit(main())
