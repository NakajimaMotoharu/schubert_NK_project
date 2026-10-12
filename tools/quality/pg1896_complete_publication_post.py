"""Separate full canonical/sole Unit/new signature post with actual new frozen graph."""
import ast
import inspect
import json
import pg1882_warning_publication_post as prior
from pg1891_complete_publication_sources import bind

SLOT='pg1896-complete-publication-full-post-v1'


def payload():
    raw=bind(prior.payload()).replace(prior.SLOT,SLOT)
    fixed=json.loads((prior.W/'pg1893-frozen-v1.safe.json').read_bytes())
    if fixed['actualExit']!=0 or fixed['sourceQualified']is not True:raise ValueError('actual new full export ABI required')
    tree=ast.parse(raw);pins=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PUBLICATION_FILES'for t in n.targets)]
    if len(pins)!=1:raise ValueError('one exact actual new publication closure required')
    raw=raw.replace(ast.get_source_segment(raw,pins[0]),'PUBLICATION_FILES='+repr(fixed['fileHashes']),1)
    compile(raw,'<new full export publication post>','exec')
    if prior.check(raw,'<actual complete independent post>'):raise ValueError('full post static gate required')
    return raw


def main():
    code=inspect.getsource(prior.main).replace('pg1880-activate','pg1894-activate')
    ns={**prior.__dict__,'SLOT':SLOT,'payload':payload}
    exec(compile(code,'<new actual post direct transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
