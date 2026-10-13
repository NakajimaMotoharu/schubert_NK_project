"""Current source real A01, unchanged Current driver and independent DIF001 oracle."""
import ast
from pg961_current_a01 import code as previous
from pg2446_question_current_observer import SOURCE,BOM,BOOT


def code():
    raw=previous()
    for a,b in [('PG961','PG2470'),('pg961','pg2470'),('pg956','pg2446'),
                ('pg957-ordinary-once-v1','pg2448-question-current-noargs-once-v1'),
                ('pg954-ordinary-before-v1.safe.json','pg2444-question-normal-publication-post-v1/manifest.safe.json'),
                ('40ef6e894573d2ffab1d1732124960f9c98d5f97',SOURCE),
                ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524',BOM),
                ('cc9ed874-7f4f-450e-a188-8de1e42c8441',BOOT),('PG932','PG2428')]:raw=raw.replace(a,b)
    marker="assert (W/'pg2448-question-current-noargs-once-v1.exit').read_bytes()==b'0\\n'"
    if raw.count(marker)!=1:raise ValueError('one actual current once receipt boundary required')
    raw=raw.replace(marker,"assert json.loads((W/'pg2448-question-current-noargs-once-v1/manifest.safe.json').read_bytes())['actualExit']==0")
    marker='assert time.monotonic_ns()//1000'
    if raw.count(marker)!=1:raise ValueError('one genuine active Root budget guard required')
    raw=raw.replace(marker,"assert m['MainPID']==issued['MainPID']=='194154'and m['InvocationID']=='9024d0364d07478d9237b6941d725208'\n"+marker)
    ast.parse(raw);return raw


if __name__=='__main__':
    ns={'__file__':__file__,'__name__':'question_current_a01'}
    exec(compile(code(),'<current real A01 driver entry>','exec'),ns);ns['main']()
