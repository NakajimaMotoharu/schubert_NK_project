"""Bounded literal-only Test PG. Original token values are the oracle; no target is executed."""
from collections import Counter
import difflib
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

def tokens(text):
    return [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]

def out(cfg,number):
    return data.BASE/('PG'+str(number)+'-'+cfg.PREFIX+'-v1')

def prior_normal(cfg):
    value = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1])
    assert value['source'] == cfg.BASE_SOURCE and value['actualExit'] == value['testsExecuted'] == 0
    return value

def original_value(cfg):
    path = out(cfg,cfg.ORIGINAL_NUMBER)
    manifest = json.loads((path/'manifest.json').read_bytes())
    return data.read_checked(path/'originals.json',manifest['originalsSha256'])

def select(text,rows,expected):
    source_tokens = tokens(text);result = []
    for row in rows:
        if row['attributes']['rule'] != 'AvoidDuplicateLiterals':continue
        match = re.fullmatch(r'The String literal "(.*)" appears (\d+) times in this file; the first occurrence is on line \d+',row['message'])
        if not match or not re.fullmatch(r'[A-Za-z0-9_:./ -]{3,120}',match[1]):continue
        literal = json.dumps(match[1])
        if source_tokens.count(literal) != int(match[2]):continue
        stem = re.sub('[^A-Z0-9]+','_',match[1].upper()).strip('_')[:40]
        assert stem
        name = 'FIXTURE_'+stem+'_'+data.sha(literal.encode())[:8].upper()
        assert name not in source_tokens and source_tokens.count(literal) >= 4
        result.append(dict(id=row['id'],value=match[1],literal=literal,name=name,references=source_tokens.count(literal)))
    assert len(result) == expected and len({r['name'] for r in result}) == expected
    return result

def inverse(old,new,mapping):
    before,after = tokens(old),tokens(new);by_name = {r['name']:r for r in mapping};expanded = [];declarations = Counter();refs = Counter();i = 0
    while i < len(after):
        if after[i:i+4] == ['private','static','final','String'] and i+4 < len(after) and after[i+4] in by_name:
            name = after[i+4];literal = by_name[name]['literal']
            assert after[i:i+8] == ['private','static','final','String',name,'=',literal,';']
            declarations[name] += 1;i += 8;continue
        token = after[i]
        if token in by_name:refs[token] += 1;token = by_name[token]['literal']
        expanded.append(token);i += 1
    assert declarations == Counter({r['name']:1 for r in mapping})
    assert refs == Counter({r['name']:r['references'] for r in mapping})
    assert expanded == before
    return dict(originalTokens=len(before),privateConstants=len(mapping),references=dict(refs),wholeSourceTokensRecovered=True)

def negative(old,new,mapping):
    variants = []
    for row in mapping:
        # Whitespace-independent declaration token value mutation, not a fixture execution.
        matches = list(re.finditer(r'\b'+re.escape(row['name'])+r'\s*=\s*'+re.escape(row['literal'])+r'\s*;',new));assert len(matches) == 1
        m = matches[0];block = m.group();bad = block.replace(row['literal'],json.dumps(row['value']+'-WRONG'),1)
        variants.append(new[:m.start()]+bad+new[m.end():])
    variants += [new.replace('assertEquals','assertNotEquals',1),new.replace('@Test','',1),new.rstrip()[:-1]]
    for value in variants:
        assert value != new
        try:inverse(old,value,mapping)
        except AssertionError:pass
        else:raise AssertionError('non-equivalent literal/source mutation accepted')
    return len(variants)

def originals(cfg):
    invocation = capture(__file__);target = out(cfg,cfg.ORIGINAL_NUMBER);assert not target.exists()
    normal = prior_normal(cfg);raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes();findings = json.loads(raw)
    ids,refs,_ = cfg.PREVIOUS_STATE();sources = []
    for path,(sha,expected,owner) in cfg.PATHS.items():
        assert path.startswith('src/') and '/src/test/java/' in path and path.endswith('Test.java')
        file = data.ROOT/path;assert not file.is_symlink();text = file.read_text();assert data.sha(text.encode()) == sha == normal['begin']['inputHashes'][path]
        rows = [r for r in findings if r['path'] == path];assert {r['inputSha256'] for r in rows} == {sha}
        mapping = select(text,[r for r in rows if r['id'] in ids-refs],expected)
        assert not any(x in text for x in ['getDeclaredField','Class.forName','setAccessible'])
        sources.append(dict(path=path,sha256=sha,text=text,findings=rows,mapping=mapping,canonicalOwner=owner))
    assert sum(len(r['mapping']) for r in sources) == cfg.EXPECTED_CORRECTIONS
    verify(invocation);target.mkdir();data.write(target/'originals.json',dict(source=cfg.BASE_SOURCE,originalFindingsSha256=data.sha(raw),sources=sources))
    data.write(target/'manifest.json',dict(actualExit=0,source=cfg.BASE_SOURCE,invocation=invocation,originalsSha256=data.sha((target/'originals.json').read_bytes()),
        sourcePaths=list(cfg.PATHS),selectedLiteralDiagnostics=cfg.EXPECTED_CORRECTIONS,productTestsExecuted=0,newAccepted=0,externalActions=0))
    print(data.sha((target/'manifest.json').read_bytes()))

def emit(cfg):
    value = original_value(cfg);patch = '*** Begin Patch\n'
    for row in value['sources']:
        old = row['text'];assert data.sha((data.ROOT/row['path']).read_bytes()) == row['sha256']
        literals = {r['literal']:r['name'] for r in row['mapping']}
        new = LEX.sub(lambda m:literals.get(m.group(),m.group()),old)
        name = row['path'].rpartition('/')[2][:-5]
        marker = re.search(r'^(?:final )?class '+re.escape(name)+r' \{\n',new,re.M);assert marker
        declarations = ''.join('  private static final String '+r['name']+' = '+r['literal']+';\n' for r in row['mapping'])
        new = new[:marker.end()]+declarations+new[marker.end():]
        inverse(old,new,row['mapping'])
        patch += '*** Update File: '+str(data.ROOT/row['path'])+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=2))[2:])+'\n'
    return patch+'*** End Patch\n'
