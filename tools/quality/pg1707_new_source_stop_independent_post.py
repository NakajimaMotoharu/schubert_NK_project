"""Separate whole terminal post; never stop/replay/authority."""
import pg1613_current_ordinary_stop_independent_post as prior
from pg1703_new_source_owned_stop_sources import bind,SOURCE,TOOLS


def payload(seals):
    raw=bind(prior.payload(seals)).replace('1613-current-ordinary-terminal-post-v1','1707-new-source-terminal-post-v1')
    compile(raw,'<new Source independent terminal full post>','exec')
    return raw


def source():
    return (prior.source().replace('1613-current-ordinary-terminal-post-v1','1707-new-source-terminal-post-v1')
            .replace('1611-stop-v1','1705-stop-v1').replace('1610-frozen-v1','1704-frozen-v1')
            .replace('1609','1703').replace('pg1703-current-ordinary-owned-stop-tools-v1',TOOLS))


def main():
    ns={**prior.prior.prior.previous.transport.__dict__,'SOURCE':SOURCE,'payload':payload}
    exec(compile(source(),'<new Source readonly complete terminal transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
