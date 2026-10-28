"""Test source-only authority oracle projection; no class, fixture or application invocation."""
from collections import Counter
import difflib
import json
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
import pg13340_authority_oracle_config as cfg
from f03_literal_batch_sources import tokens
from public_java_digest_provenance import LEX
from pg11370_source_constructor_owner_audit import functions
from f03_state_oracle_sources import indices

CALL_TEXT = '"ROLE_" + p.role().wireValue()'
CALL = tokens(CALL_TEXT)

def single(values,pattern):
    found = indices(values,pattern);assert len(found) == 1, "one exact structural token block required"
    return found[0]

def before(path):
    raw = subprocess.check_output(['git','show',cfg.BASE_SOURCE+':'+path],cwd=data.ROOT);assert data.sha(raw) == cfg.SPECS[path]['sha256'];return raw.decode()

def declarations():return ''.join('  private static final String '+name+' = '+json.dumps(value)+';\n' for name,value in cfg.FIELDS.values())

def helper():
    return '  // SS314 closed Test input identity, never the Production output mapper.\n  private static String '+cfg.HELPER+'(SessionPrincipal principal) {\n    return switch (principal.role()) {\n'+''.join('      case '+role+' -> '+name+';\n' for role,(name,_) in cfg.FIELDS.items())+'    };\n  }\n'

def project(values,spec,previous):
    result = list(values);method = tokens(helper());start = single(result,method);del result[start:start+len(method)]
    for name,value in cfg.FIELDS.values():
        decl = tokens('private static final String '+name+' = '+json.dumps(value)+';');at = single(result,decl);del result[at:at+len(decl)]
        result = [json.dumps(value) if v == name else v for v in result]
    call = tokens(cfg.HELPER+'(p)');sites = indices(result,call);assert len(sites) == spec['count']
    for i in reversed(sites):result[i:i+len(call)] = CALL
    assert result == tokens(previous)
    return dict(allNonOracleTokensRecovered=True,callerReplacements=len(sites),newPrivateHelperMethods=1,newPrivateConstantFields=2)

def callers(text):
    positioned = [(m.group(),m.start()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))];values = [v[0] for v in positioned];methods = functions(positioned);result = []
    for i in indices(values,CALL):
        found = [(b-a,name) for a,b,name in methods if a <= i <= b];assert found
        result.append(dict(method=min(found)[1],line=text.count('\n',0,positioned[i][1])+1))
    return result

def planned(path):
    spec = cfg.SPECS[path];text = before(path);values = tokens(text)
    assert cfg.HELPER not in values and all(name not in values for name,_ in cfg.FIELDS.values())
    assert len(indices(values,CALL)) == text.count(CALL_TEXT) == spec['count'] and Counter(r['method'] for r in callers(text)) == Counter(spec['methods'])
    updated = text.replace(CALL_TEXT,cfg.HELPER+'(p)');literals = {json.dumps(value):name for name,value in cfg.FIELDS.values()}
    updated = LEX.sub(lambda m:literals.get(m.group(),m.group()),updated)
    marker = re.search(r'^class '+re.escape(Path(path).stem)+r' \{\n',updated,re.M);assert marker
    updated = updated[:marker.end()]+declarations()+helper()+updated[marker.end():]
    project(tokens(updated),spec,text);return updated

def negatives(text,spec,previous):
    values = tokens(text);pattern = tokens(helper());start = single(values,pattern);variants = []
    for role,(name,value) in cfg.FIELDS.items():
        case = tokens('case '+role+' -> '+name+';');at = single(pattern,case);other = next(n for n,_ in cfg.FIELDS.values() if n != name)
        bad = list(values);bad[start+at+case.index(name)] = other;variants.append(('wrong-role-'+role,bad))
        decl = tokens('private static final String '+name+' = '+json.dumps(value)+';');at = single(values,decl)
        bad = list(values);bad[at+decl.index(json.dumps(value))] = '"ROLE_UNAPPROVED"';variants.append(('wrong-fixed-literal-'+role,bad))
    role,(name,_) = next(iter(cfg.FIELDS.items()));case = tokens('case '+role+' -> '+name+';');at = single(pattern,case)
    bad = list(values);del bad[start+at:start+at+len(case)];variants.append(('missing-case',bad))
    bad = list(values);bad[start+at:start+at] = case;variants.append(('duplicate-case',bad))
    bad = list(values);bad[start:start+len(pattern)] = tokens('private static String '+cfg.HELPER+'(SessionPrincipal principal) { return "ROLE_" + principal.role().wireValue(); }');variants.append(('production-encoder',bad))
    call = tokens(cfg.HELPER+'(p)');at = indices(values,call)[0];bad = list(values);bad[at+call.index('p')] = 'otherPrincipal';variants.append(('wrong-input',bad))
    bad = list(values);bad[bad.index('assertEquals')] = 'assertNotEquals';variants.append(('assertion-binding',bad))
    at = indices(values,['@','Test'])[0];bad = list(values);del bad[at:at+2];variants.append(('annotation',bad));variants.append(('class-end',values[:-1]));labels = []
    for label,bad in variants:
        assert bad != values
        try:project(bad,spec,previous)
        except AssertionError:labels.append(label)
        else:raise AssertionError('dependent/non-preserving authority oracle source accepted')
    return labels

def ss_domain():
    raw = (data.ROOT/cfg.SS[0]).read_bytes();assert data.sha(raw) == cfg.SS[1] and raw == subprocess.check_output(['git','show','origin/main:'+cfg.SS[0]],cwd=data.ROOT)
    assert 'ROLE_USER/ROLE_ADMINのどちらか1個だけ' in raw.decode()
    return [dict(inputRole=role,expectedAuthority=value,actualKind='STATIC_SOURCE_BINDING_NOT_RUNTIME') for role,(_,value) in cfg.FIELDS.items()]

def emit():
    patch = '*** Begin Patch\n'
    for path,spec in cfg.SPECS.items():
        old = (data.ROOT/path).read_text();assert data.sha(old.encode()) == spec['sha256'];new = planned(path)
        patch += '*** Update File: '+str(data.ROOT/path)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=2))[2:])+'\n'
    return patch+'*** End Patch\n'
