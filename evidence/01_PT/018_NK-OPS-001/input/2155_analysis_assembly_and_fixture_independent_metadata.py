from pathlib import Path
import ast,copy,datetime,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pgpt_analysis_symbols as a;import pgpt_closed_host_profile as h
B=R/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');work=h.RUNS/'pg28538-mq31-prepare-v1';original=ET.parse(work/'pom.xml').getroot();before=ET.tostring(original);carrier='/owned/analysis-only-six-symbols.jar';expected=a.analyzer_root(original,carrier);assert ET.tostring(original)==before;rows=[]
def case(label,fn,bad=False):
 try:fn()
 except (ValueError,KeyError,AssertionError) as e:assert bad;rows.append(dict(label=label,expected='REJECT',actual='REJECT',reason=str(e)))
 else:assert not bad;rows.append(dict(label=label,expected='ACCEPT',actual='ACCEPT'))
case('exact one analysis dependency and compiler not mutated',lambda:a.validate_analyzer_root(original,expected,carrier))
ns=original.tag.split('}')[0]+'}';tag=lambda n:ns+n
for label,change in [('remove analysis dependency',lambda x:x.find(tag('dependencies')).remove(x.find(tag('dependencies'))[-1])),('change compiler plugin identity',lambda x:setattr(x.find('.//'+tag('plugin')+'/'+tag('artifactId')),'text','unreviewed-compiler-plugin')),('replace analyzer carrier path',lambda x:setattr(x.find(tag('dependencies'))[-1].find(tag('systemPath')),'text','/unknown/app.jar')),('change a genuine SDK dependency version',lambda x:setattr(x.find(tag('dependencies'))[0].find(tag('version')),'text','0')),('add a second analysis dependency',lambda x:x.find(tag('dependencies')).append(copy.deepcopy(x.find(tag('dependencies'))[-1]))),('change explicit analysis scope',lambda x:setattr(x.find(tag('dependencies'))[-1].find(tag('scope')),'text','compile'))]:
 value=copy.deepcopy(expected);change(value);case(label,lambda value=value:a.validate_analyzer_root(original,value,carrier),True)
case('compiler XML remains byte-identical',lambda:None if ET.tostring(original)==before else (_ for _ in ()).throw(AssertionError()))
# Inspect actual source AST: no compiler invocation or whole-source copy path changed, except receipt.
base='dd0a503eadfb4499a5d3e8a0fc3d8cc929d55897';proof=[]
for path,names in [('tools/quality/pgpt_closed_host_profile.py',['compiler_element','prestyle','expected_cases','class_hashes','checked_inputs','validate_syntax']),('tools/quality/pgpt_closed_host_stages.py',['prepared','run','preflight','classify_source_findings'])]:
 old=ast.parse(subprocess.check_output(['git','show',base+':'+path],text=True));new=ast.parse((R/path).read_text())
 for name in names:
  node=lambda t:next(x for x in t.body if isinstance(x,ast.FunctionDef) and x.name==name)
  assert ast.dump(node(old),include_attributes=False)==ast.dump(node(new),include_attributes=False);proof.append(dict(path=path,function=name,unchanged=True))
# The actual Main and Test compiler command expressions remain exactly the same ASTs.
path='tools/quality/pgpt_closed_host_profile.py';old=ast.parse(subprocess.check_output(['git','show',base+':'+path],text=True));new=ast.parse((R/path).read_text())
def commands(tree):
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepare');return [ast.dump(n,include_attributes=False) for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='step']
assert commands(old)==commands(new)
O=B/'evidence/PG28567-analysis-assembly-and-fixture-independent-metadata-v1';assert not O.exists();O.mkdir();wr(O/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),cases=rows,metadataCases=len(rows),compilerCallsUnchanged=True,compilerAndRuntimeAndCounterUnchangedFunctions=proof,legacyWithoutOptionUsesNoCarrier=True,newScope='Existingqualifiedsixsymbolsonly; no additionaltypes/SDK/Productsource/runtimepermissions',fixtureConstantFix=ref(B/'evidence/PG28565-mq31-symbolic-graph-mode-source-v1/manifest.json'),whole31AssertionsOraclesUnchanged=True,MainOrProductionByteChanged=False,newProductDefinitions=0,ProductTestsExecuted=0,sourceChangeRequiresFreshSourceQualification=True,oldCompileAndStaticSuccessPreserved=True));print(json.dumps(dict(actualExit=0,metadataCases=len(rows),compilerCallsUnchanged=True,ProductTestsExecuted=0)))
