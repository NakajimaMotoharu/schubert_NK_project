"""Current40ef only, actual eeae completed parent and fresh978-v2 existingADMIN profile."""
import ast
from pathlib import Path
from pg894_sources_v3 import files as previous
SOURCE='40ef6e894573d2ffab1d1732124960f9c98d5f97'
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def files(baseline_sha):
    original=previous(baseline_sha);result={}
    replacements=(('Pg894','Pg983'),('PG894','PG983'),('pg894','pg983'),('PG862','PG932'),('pg862','pg932'),('e01612fcd7f2752df5ae0836b78538fd5e87f120',SOURCE),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),('93cb976e-c36c-47a3-b9e2-0ad28d2996de','eeae04ea-713c-4f2d-888d-358fb4bed274'),('2026-10-09T19:07:23.894279Z','2026-10-09T23:31:22.087768Z'),('0dfe0b7f-0e36-4b81-9086-500d896d1187','091663ce-1cf4-47e7-8311-218ebb0c8653'),('2026-10-09T19:31:23.759513Z','2026-10-09T23:56:48.112404Z'),('75f48ce36cd740e98a801eede7fdbb7f','0bb4d6f3b9e74cdc91c553748a4cd018'),('187002958845','202927375873'),('pg895-bootstrap-before-v1','pg978-bootstrap-before-v2'),('pg887','pg963'),('==584','==594'))
    for name,raw in original.items():
        for a,b in replacements:name=name.replace(a,b);raw=raw.replace(a,b)
        if name=='pg963_parent_receipt.py':raw=(W/'pg963-native-tools-v1/pg963_parent_receipt.py').read_text()
        if name.endswith('.py'):ast.parse(raw)
        result[name]=raw
    assert 'pg963_parent_receipt.py' in result
    return result
