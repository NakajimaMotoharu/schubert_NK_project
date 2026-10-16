"""Current composite/parent18-bound ordinary stop graph; never rewrite embedded data."""
import inspect
import pg3600_current_browser_owned_sources as previous
import pg3808_hygiene_acceptance as acceptance
import pg3816_hygiene_browser_composite as composite
from immutable_payload_binding import bind_preserving_payloads

SOURCE=acceptance.SOURCE;BOM=acceptance.BOM;TOOLS='pg3822-hygiene-owned-stop-tools-v1'


class Current:
    SOURCE=SOURCE;BOM=BOM;SEAL=composite.SLOT;TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.terminal_payload)
    seal_payload=staticmethod(composite.payload)


current=Current


def role_text(raw):
    for a,b in [(previous.TOOLS,TOOLS),(previous.SOURCE,SOURCE),(previous.BOM,BOM),('PG3420','PG3748'),('pg3420','pg3748'),(previous.composite.SLOT,composite.SLOT),(previous.acceptance.TERM,acceptance.TERM),(previous.acceptance.LIVE,acceptance.LIVE),('pg3594-current-browser-parent-projection-v1','pg3818-hygiene-parent-projection-v1'),('pg3604-current-browser-owned-stage-v1','pg3826-hygiene-owned-stage-v1'),('pg3606-current-browser-owned-post-v1','pg3828-hygiene-owned-post-v1'),('PG3606-current-browser-owned-post-v1','PG3828-hygiene-owned-post-v1'),('pg3600','pg3822'),('Pg3600','Pg3822'),('PG3600','PG3822'),('pg3602','pg3824'),('pg3604','pg3826'),('pg3605','pg3827'),('pg3607','pg3829')]:raw=raw.replace(a,b)
    return raw


def final_bind(raw):return bind_preserving_payloads(raw,lambda value:role_text(previous.final_bind(value)))


def bind(raw):return bind_preserving_payloads(raw,lambda value:role_text(previous.bind(value)))


def candidate_bom():return BOM


def namespace():
    values={**previous.original.__dict__,'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'bind':bind,'current':current}
    exec(compile(inspect.getsource(previous.original.namespace),'<current7fff whole owned composer>','exec'),values)
    return values['namespace']()


def context():return namespace()['context']()


def sources():return{final_bind(n):final_bind(raw)for n,raw in namespace()['sources']().items()}
