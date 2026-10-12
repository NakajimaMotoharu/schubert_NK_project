"""Independent qualifier for exact formatted API5 new run, not1714 pass reuse."""
import inspect
import pg1715_api_configuration_selected_qualification as prior


def server():
    return prior.server().replace('PG1715','PG1717').replace('1714','1716')


def main():
    raw=inspect.getsource(prior.main)
    for old,new in [('pg1715-api-configuration-selected-qualified-v1','pg1717-formatted-api-selected-qualified-v1'),
                    ('pg1714-api-configuration-negative-selected-v1','pg1716-formatted-api-configuration-selected-v1'),
                    ('pg1715-qualification','pg1717-qualification'),('PG1715-selected-qualification','PG1717-selected-qualification'),
                    ("{'1714':host['manifestSha256']}","{'1716':host['manifestSha256']}")]:
        if old not in raw:raise ValueError('formatted actual result join boundary absent')
        raw=raw.replace(old,new)
    ns={**prior.__dict__,'server':server}
    exec(compile(raw,'<formatted source read-only five qualifier>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
