"""Verify exactly one display-only fix against archived qualified bytes; never rerun preflight or PT."""
import ast
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify


def main():
    invocation = capture(Path(__file__))
    out = data.BASE/'PG10071-log-preflight-display-fix-v1'
    original = out/'qualified-original-tool.py'
    assert set(p.name for p in out.iterdir()) == {original.name}
    path = data.ROOT/'tools/quality/pg10064_log_sql_preflight.py'
    old, new = original.read_text(), path.read_text()
    manifest = data.read_checked(data.BASE/'PG10064-log-sql-preflight-v1/manifest.json',
        '6b4a2831d85fa55dea0436daf6b289b49f6de3c8f54f70b49f72f1df868fa2c5')
    assert data.sha(original.read_bytes()) == manifest['invocation']['entrypointSha256']
    before = 'tests=16,suites=3,mainClasses=2,'
    after = 'tests=len(cases),suites=len(CATALOG),mainClasses=len(physical_main),'
    assert old.count(before) == 1 and old.replace(before,after) == new
    tree = ast.parse(new)
    catalog = ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id == 'CATALOG' for t in n.targets)))
    assert len(catalog) == manifest['expectedSuites'] == 2
    assert sum(map(len,catalog.values())) == manifest['expectedTests'] == 16
    assert {k.rsplit('.',1)[-1]:v for k,v in manifest['caseCounts'].items()} == {k:len(v) for k,v in catalog.items()}
    verify(invocation)
    data.write(out/'manifest.json',dict(actualExit=0,source=manifest['source'],invocation=invocation,
        qualifiedPreflightSha256='6b4a2831d85fa55dea0436daf6b289b49f6de3c8f54f70b49f72f1df868fa2c5',
        qualifiedOriginalToolSha256=data.sha(original.read_bytes()),currentToolSha256=data.sha(path.read_bytes()),
        onlyPrintChanged=True,manifestAndAllGuardsUnchanged=True,originalDisplaySuites=3,actualSuites=2,
        expectedTests=16,preflightReexecuted=False,productTestsExecuted=0,newAccepted=0,formalUpdated=False))
    print(json.dumps(dict(actualExit=0,tests=16,suites=len(catalog),
        manifestSha256=data.sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
