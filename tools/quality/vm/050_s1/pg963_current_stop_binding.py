"""Current40ef/neweeae genuine proof only; generation, never an actual stop."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parent
SOURCE='40ef6e894573d2ffab1d1732124960f9c98d5f97'
def module_source():
    raw=(R/'pg877_stop_binding.py').read_text()
    values=(('Pg877','Pg963'),('PG877','PG963'),('pg877','pg963'),('PG875','PG960'),('pg875','pg960'),('PG862','PG932'),('pg862','pg932'),('e01612fcd7f2752df5ae0836b78538fd5e87f120','40ef6e894573d2ffab1d1732124960f9c98d5f97'),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),('19022204-8a9e-418d-ba2a-9967ff923dc2','eeae04ea-713c-4f2d-888d-358fb4bed274'),('2026-10-09T18:28:14.612111Z','2026-10-09T23:31:22.087768Z'),('cf07d74f-14c7-4223-9eb9-82eb6f0fbd0d','091663ce-1cf4-47e7-8311-218ebb0c8653'),('09167719cb0445fea8da5a6fdbaa3b0f','0bb4d6f3b9e74cdc91c553748a4cd018'),('183192933299','201380374989'),('184992933299','203180374989'),('189291','213904'),('3592151','3844442'),('pg870-ordinary-before-v1','pg954-ordinary-before-v1'))
    for a,b in values:assert a in raw,a;raw=raw.replace(a,b)
    # This original thirty-minute window may cross UTC midnight; never extend monotonic budget.
    marker=' ast.parse(raw)\n return raw';assert raw.count(marker)==1
    raw=raw.replace(marker," raw=raw.replace(\"r'2026-10-09T[0-9:]{8}\",\"r'2026-10-(?:09|10)T[0-9:]{8}\")\n"+marker)
    ast.parse(raw);return raw
def namespace():
    env={'__file__':str(R/'pg963_current_stop_binding.py'),'__name__':'current40ef_ownedstop'};exec(compile(module_source(),'<963 whole new-source stop>','exec'),env);return env
def bindings(proof):return namespace()['bindings'](proof)
def generate(proof):return namespace()['generate'](proof)
