"""Whole current resume/composite/parent18-bound stop graph; preserve nested raw oracles."""
import inspect
import pg3822_hygiene_owned_sources as previous
import pg3858_current_resume_acceptance as acceptance
import pg3870_current_resume_composite as composite
from immutable_payload_binding import bind_preserving_payloads

SOURCE=acceptance.SOURCE;BOM=acceptance.BOM;TOOLS='pg3876-current-resume-owned-tools-v1'


class Current:
    SOURCE=SOURCE;BOM=BOM;SEAL=composite.SLOT;TERM=acceptance.TERM
    terminal_payload=staticmethod(acceptance.terminal_payload)
    seal_payload=staticmethod(composite.payload)


current=Current


def role_text(raw):
    for a,b in [(previous.TOOLS,TOOLS),(previous.composite.SLOT,composite.SLOT),
                (previous.acceptance.TERM,acceptance.TERM),(previous.acceptance.LIVE,acceptance.LIVE),
                ('pg3818-hygiene-parent-projection-v1','pg3872-current-resume-parent-projection-v1'),
                ('pg3826-hygiene-owned-stage-v1','pg3880-current-resume-owned-stage-v1'),
                ('pg3828-hygiene-owned-post-v1','pg3882-current-resume-owned-post-v1'),
                ('PG3828-hygiene-owned-post-v1','PG3882-current-resume-owned-post-v1'),
                ('pg3822','pg3876'),('Pg3822','Pg3876'),('PG3822','PG3876'),
                ('pg3824','pg3878'),('pg3826','pg3880'),('pg3827','pg3881'),('pg3829','pg3883')]:raw=raw.replace(a,b)
    return raw


def final_bind(raw):return bind_preserving_payloads(raw,lambda text:role_text(previous.final_bind(text)))


def bind(raw):return bind_preserving_payloads(raw,lambda text:role_text(previous.bind(text)))


def candidate_bom():return BOM


def namespace():
    original=previous.previous.original
    values={**original.__dict__,'SOURCE':SOURCE,'BOM':BOM,'TOOLS':TOOLS,'bind':bind,'current':current}
    exec(compile(inspect.getsource(original.namespace),'<whole current resume owned graph>','exec'),values)
    return values['namespace']()


def context():return namespace()['context']()


def sources():return{final_bind(name):final_bind(raw)for name,raw in namespace()['sources']().items()}
