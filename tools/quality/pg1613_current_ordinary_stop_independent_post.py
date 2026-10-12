"""Independent whole current ordinary post, not a stop/deployment authority."""
import pg1583_current_stop_independent_post as prior
from pg1609_current_ordinary_owned_stop_sources import bind,SOURCE,TOOLS

def payload(seals):
    raw=bind(prior.payload(seals)).replace('1583-current-terminal-post-v1','1613-current-ordinary-terminal-post-v1')
    compile(raw,'<ordinary stop all-field independent post>','exec');return raw

def source():
    return prior.source().replace('1583-current-terminal-post-v1','1613-current-ordinary-terminal-post-v1').replace('1581-stop-v1','1611-stop-v1').replace('1580-frozen-v1','1610-frozen-v1').replace('1579','1609').replace('pg1609-current-owned-stop-tools-v1',TOOLS)

def main():
    env={**prior.prior.previous.transport.__dict__,'SOURCE':SOURCE,'payload':payload}
    exec(compile(source(),'<ordinary stop all-field independent transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
