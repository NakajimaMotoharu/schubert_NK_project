"""Actual signed04bb ABI, all nested shared4916 classes and five phases."""
import pg4824_new_current_bootstrap_compile as previous
import pg4932_current_bootstrap_sources as role


def source():
    raw=previous.source()
    for old,new in [('pg4824-','pg4934-'),('Pg4820','Pg4932'),
                    ('pg4772-new-current-owned-tools-v1',role.owned.TOOLS),
                    ('pg4774-frozen-v1.safe.json','pg4918-frozen-v1.safe.json'),
                    ('pg4702-release-v1','pg4860-release-v1')]:raw=raw.replace(old,new)
    return raw


def main():
    ns={**vars(previous.previous),'role':role}
    exec(compile(source(),'<actual current nested Bootstrap ABI>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
