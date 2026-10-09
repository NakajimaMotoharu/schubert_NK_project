"""Current state/full32 typed-empty under all ten Load/Ref, never before Ref scope."""
import ast
from pathlib import Path
from pg901_bootstrap_post_v2 import payload as previous
import pg901_bootstrap_post as dispatch
R=Path(__file__).resolve().parent
def payload(proof,seals):
 raw=previous(proof,seals)
 start=raw.index('current_bootstrap=show(bootstrap,STATE_FIELDS)');end=raw.index('\n\nbus=dbus.SystemBus',start)
 block=raw[start:end];raw=raw[:start]+raw[end:]
 marker=' for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)';assert raw.count(marker)==1
 raw=raw.replace(marker,marker+'\n'+''.join(' '+l+'\n'for l in block.splitlines()))
 raw=raw.replace('pg901-bootstrap-post-v2','pg901-bootstrap-post-v3').replace('PG901-bootstrap-post-v2','PG901-bootstrap-post-v3')
 assert raw.index(marker)<raw.index('current_bootstrap=show')<raw.index(' def snapshot():')
 ast.parse(raw);return raw
if __name__=='__main__':
 source=(R/'pg901_bootstrap_post.py').read_text();env={'__file__':str(R/'pg901_bootstrap_post_v3.py'),'__name__':'post_v3'}
 exec(compile(source,'<901 shared readonly dispatcher>','exec'),env);env['payload']=payload
 main_source=source[source.index('def main():'):source.index("if __name__=='__main__':")].replace('pg901-bootstrap-post-v1','pg901-bootstrap-post-v3')
 exec(compile(main_source,'<901 separate post v3>','exec'),env);env['main']()
