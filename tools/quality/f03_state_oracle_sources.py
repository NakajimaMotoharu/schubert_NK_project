"""Existing Test source transformation/projection only; fixed UI vectors, never Java target execution."""
from collections import Counter
import difflib
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from f03_literal_batch_sources import tokens
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
import pg13324_state_oracle_config as cfg

CALL = tokens('state.wireValue()')

def indices(values,pattern):return [i for i in range(len(values)-len(pattern)+1) if values[i:i+len(pattern)] == pattern]

def before(path):
    raw = subprocess.check_output(['git','show',cfg.BASE_SOURCE+':'+path],cwd=data.ROOT)
    assert data.sha(raw) == cfg.SPECS[path]['sha256']
    return raw.decode()

def helper(spec):
    return '  // Test-only exhaustive UI236 oracle; never use the Production output encoder.\n  private static String '+spec['helper']+'('+spec['enum']+' state) {\n    return switch (state) {\n'+''.join('      case '+value+' -> '+name+';\n' for value,name in spec['fields'].items())+'    };\n  }\n'

def bindings(values,spec):
    for value,name in spec['fields'].items():assert len(indices(values,tokens('private static final String '+name+' = '+json.dumps(value)+';'))) == 1

def project(values,spec,previous):
    result = list(values);bindings(result,spec);pattern = tokens(helper(spec));found = indices(result,pattern);assert len(found) == 1
    start = found[0];del result[start:start+len(pattern)]
    call = tokens(spec['helper']+'(state)');sites = indices(result,call);assert len(sites) == spec['count']
    for i in reversed(sites):result[i:i+len(call)] = CALL
    assert result == tokens(previous)
    return dict(allNonOracleTokensRecovered=True,callerReplacements=len(sites),privateHelperMethodsAdded=1,fixedLiteralFieldsUnchanged=len(spec['fields']))

def callers(text):
    positioned = [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    values = [t[0] for t in positioned];methods = functions(positioned);result = []
    for i in indices(values,CALL):
        enclosing = [(end-start,name) for start,end,name in methods if start <= i <= end];assert enclosing
        result.append(dict(method=min(enclosing)[1],line=text.count('\n',0,positioned[i][1])+1))
    return result

def planned(path):
    spec = cfg.SPECS[path];text = before(path);values = tokens(text);bindings(values,spec)
    assert spec['helper'] not in values and len(indices(values,CALL)) == spec['count']
    assert Counter(r['method'] for r in callers(text)) == Counter(spec['methods'])
    assert text.count('state.wireValue()') == spec['count']
    updated = text.replace('state.wireValue()',spec['helper']+'(state)')
    marker = re.search(r'^class '+re.escape(Path(path).stem)+r' \{\n',updated,re.M);assert marker
    updated = updated[:marker.end()]+helper(spec)+updated[marker.end():]
    project(tokens(updated),spec,text);return updated

def negatives(text,spec,previous):
    values = tokens(text);pattern = tokens(helper(spec));start, = indices(values,pattern);variants = []
    for value,name in spec['fields'].items():
        case = tokens('case '+value+' -> '+name+';');at, = indices(pattern,case);wrong = next(v for v in spec['fields'].values() if v != name)
        bad = list(values);bad[start+at+case.index(name)] = wrong;variants.append(('wrong-wire-'+value,bad))
        decl = tokens('private static final String '+name+' = '+json.dumps(value)+';');at, = indices(values,decl)
        bad = list(values);bad[at+decl.index(json.dumps(value))] = '"UNAPPROVED_STATE"';variants.append(('wrong-fixed-literal-'+value,bad))
    first_value,first_name = next(iter(spec['fields'].items()));case = tokens('case '+first_value+' -> '+first_name+';');at, = indices(pattern,case)
    bad = list(values);del bad[start+at:start+at+len(case)];variants.append(('missing-case',bad))
    bad = list(values);bad[start+at:start+at] = case;variants.append(('duplicate-case',bad))
    bad = list(values);bad[start:start+len(pattern)] = tokens('private static String '+spec['helper']+'('+spec['enum']+' state) { return state.wireValue(); }');variants.append(('production-encoder',bad))
    call = tokens(spec['helper']+'(state)');site = indices(values,call)[0];bad = list(values);bad[site+call.index('state')] = 'otherState';variants.append(('wrong-input',bad))
    bad = list(values);bad[bad.index('assertEquals')] = 'assertNotEquals';variants.append(('assertion-binding',bad))
    test_at = indices(values,['@','Test'])[0];bad = list(values);del bad[test_at:test_at+2];variants.append(('annotation',bad))
    variants.append(('class-end',values[:-1]));labels = []
    for label,bad in variants:
        assert bad != values
        try:project(bad,spec,previous)
        except AssertionError:labels.append(label)
        else:raise AssertionError('non-independent or non-preserving oracle source accepted')
    return labels

def ui_domain():
    raw = (data.ROOT/cfg.UI[0]).read_bytes();assert data.sha(raw) == cfg.UI[1]
    assert raw == subprocess.check_output(['git','show','origin/main:'+cfg.UI[0]],cwd=data.ROOT)
    text = raw.decode();domains = []
    for kind,label,offset in [('AnswerState','回答状態',615),('NotificationState','内部状態',51)]:
        match = re.search(r'^\|\s*'+label+r'\s*\|\s*'+str(offset)+r'\s*\|\s*12\s*\|\s*X\s*\|\s*M\s*\|\s*([^|]+)\|',text,re.M);assert match
        actual = match[1].strip().split('/');spec = next(v for v in cfg.SPECS.values() if v['enum'] == kind);assert actual == list(spec['fields'])
        domains.extend(dict(enum=kind,inputIdentity=value,expectedLiteral=value,uiOffset=offset,uiLength=12,actualKind='STATIC_SOURCE_BINDING_NOT_RUNTIME') for value in actual)
    assert len(domains) == 8;return domains

def emit():
    patch = '*** Begin Patch\n'
    for path,spec in cfg.SPECS.items():
        text = (data.ROOT/path).read_text();assert data.sha(text.encode()) == spec['sha256'];new = planned(path)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(text.splitlines(),new.splitlines(),n=2))[2:])+'\n'
    return patch+'*** End Patch\n'
