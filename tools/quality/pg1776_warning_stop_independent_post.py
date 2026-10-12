"""Separate terminal/resource/full-row post; retained failed manager is data.

Same-source current frozen helper byte only. Never issue stop/start again.
"""
import pg1707_new_source_stop_independent_post as prior
from pg1772_warning_owned_stop_sources import bind,SOURCE,TOOLS


def payload(seals):
    raw=bind(prior.payload(seals))
    raw=raw.replace('1707-new-source-terminal-post-v1','1776-warning-terminal-post-v1')
    compile(raw,'<separate warning-owned full terminal post>','exec');return raw


def source():
    return (prior.source().replace('1707-new-source-terminal-post-v1','1776-warning-terminal-post-v1')
            .replace('1705-stop-v1','1774-stop-v1').replace('1704-frozen-v1','1773-frozen-v1')
            .replace('1703','1772').replace('pg1772-new-source-owned-stop-tools-v1',TOOLS))


def main():
    ns={**prior.prior.prior.prior.previous.transport.__dict__,'SOURCE':SOURCE,'payload':payload}
    exec(compile(source(),'<actual warning terminal post transport>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
