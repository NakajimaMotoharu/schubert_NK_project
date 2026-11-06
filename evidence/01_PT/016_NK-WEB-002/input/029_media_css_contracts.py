"""Seven independent CSS resource contracts; separate parser/legacy-oracle metadata checks.
Only explicit local source/fixture inputs are read. No browser, application or backend is invoked.
"""
from pathlib import Path
import json,hashlib,sys,re,unittest,io,datetime,platform,subprocess,xml.etree.ElementTree as E
import tinycss2
R=Path.cwd();G=R/'evidence/01_PT/016_NK-WEB-002/input/030_media_css_golden.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def selector(s):return re.sub(r'\s*,\s*',',',' '.join(s.split()))
def condition(s):return re.sub(r':\s*',':',' '.join(s.split()))
def parse(css):
 if not isinstance(css,str):raise ValueError('CSS text required')
 result={}
 def visit(rules,context):
  for node in rules:
   if node.type=='at-rule':
    if node.lower_at_keyword!='media' or node.content is None:raise ValueError('unexpected at-rule')
    visit(tinycss2.parse_rule_list(node.content,skip_comments=True,skip_whitespace=True),context+('media:'+condition(tinycss2.serialize(node.prelude)),));continue
   if node.type!='qualified-rule':raise ValueError('CSS parse error')
   key=(context,selector(tinycss2.serialize(node.prelude)));props={}
   for item in tinycss2.parse_declaration_list(node.content,skip_comments=True,skip_whitespace=True):
    if item.type!='declaration' or item.important or item.lower_name in props:raise ValueError('invalid/duplicate/important declaration')
    props[item.lower_name]=tinycss2.serialize(item.value).strip()
   result.setdefault(key,[]).append(props)
 return visit(tinycss2.parse_stylesheet(css,skip_comments=True,skip_whitespace=True),()) or result
def one(rules,context,sel):
 values=rules.get((tuple(context),selector(sel)),[])
 if len(values)!=1:raise ValueError('exact one CSS rule required: '+sel)
 return values[0]
golden=json.loads(G.read_text());RULES=golden['rules'];MARKER=golden['marker'];before=R/golden['before']['snapshot'];CURRENT=Path(golden['current']['path'])
class ParserMetadata(unittest.TestCase):
 def test_fixed_tokens_nested_media_and_comments(self):
  p=parse('/*a*/ .x { color: red; } @media (max-width: 900px) { .y { width: 100%; } }')
  self.assertEqual({'color':'red'},one(p,[],'.x'));self.assertEqual({'width':'100%'},one(p,['media:(max-width:900px)'],'.y'))
 def test_quoted_semicolon_is_not_a_declaration_separator(self):self.assertEqual({'content':'"a;b"'},one(parse('.x{content:"a;b";}'),[],'.x'))
 def test_null_malformed_and_unexpected_at_rule_are_not_success(self):
  for value in [None,'.x{not-a-declaration}', '@import "unwanted.css";']:
   with self.assertRaises(ValueError):parse(value)
 def test_duplicate_selected_rules_cannot_hide_later_override(self):
  with self.assertRaises(ValueError):one(parse('.x{color:red}.x{color:blue}'),[],'.x')
 def test_manual_goldens_match_readonly_current_and_inherited_properties(self):
  self.assertEqual(golden['current']['sha256'],sha(CURRENT));p=parse(CURRENT.read_text())
  for row in RULES:
   if row['selector']=='.music-player .download, .song-player .download':actual=one(p,[],'.download')
   elif row['selector']=='.music-player audio, .song-player audio':actual={**one(p,[],'audio'),**one(p,[],row['selector'])}
   else:actual=one(p,row['context'],row['selector'])
   self.assertEqual(row['properties'],actual,row['selector'])
  self.assertEqual(16,len(RULES));self.assertEqual(62,sum(len(x['properties']) for x in RULES));self.assertEqual(golden['before']['sha256'],sha(before))
class CssCompatibilityContracts(unittest.TestCase):
 def check_group(self,group):
  for row in RULES:
   if row['case']==group:
    try:actual=one(ACTUAL,row['context'],row['selector'])
    except ValueError as failure:self.fail(str(failure))
    self.assertEqual(row['properties'],actual,row['selector'])
 def test_001_video_page_keeps_current_1280_bound(self):self.check_group(1)
 def test_002_video_frame_keeps_current_clipping_and_colors(self):self.check_group(2)
 def test_003_video_player_keeps_current_16_9_and_height_policy(self):self.check_group(3)
 def test_004_music_rows_titles_and_spacing_keep_current_layout(self):self.check_group(4)
 def test_005_music_pair_players_placeholders_and_controls_keep_current(self):self.check_group(5)
 def test_006_mobile_music_and_pair_columns_keep_current_900_breakpoint(self):self.check_group(6)
 def test_007_existing_prefix_is_unchanged_and_suffix_has_only_target_rules(self):
  original=before.read_bytes();self.assertTrue(CSS_BYTES.startswith(original));tail=CSS_BYTES[len(original):].decode();self.assertEqual(1,tail.count(MARKER));parsed=parse(tail)
  self.assertEqual({(tuple(x['context']),selector(x['selector'])) for x in RULES},set(parsed));self.assertEqual(16,sum(len(v) for v in parsed.values()))
class Recorded(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.rows=[]
 def stopTest(self,test):
  status='PASS'
  if any(t==test for t,_ in self.failures):status='FAIL'
  if any(t==test for t,_ in self.errors):status='ERROR'
  if any(t==test for t,_ in self.skipped):status='SKIP'
  self.rows.append(dict(method=test._testMethodName,status=status));super().stopTest(test)
if __name__=='__main__':
 mode=sys.argv[1];assert mode in {'metadata','product'};bindings={};source=None;branch=None
 if mode=='product':
  source=sys.argv[3];assert re.fullmatch('[0-9a-f]{40}',source) and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==source;branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip();assert branch=='dev-foundation'
  for p in [Path(__file__),G,before]:
   name=str(p.resolve().relative_to(R));h=hashlib.sha256(subprocess.check_output(['git','show',source+':'+name])).hexdigest();assert h==sha(p);bindings[name]=h
  cssGit='src/schubert-nk-web/src/main/resources/static/css/schubert.css';assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+cssGit])).hexdigest()==sha(Path(sys.argv[2]))
 out=Path(sys.argv[-1]);assert not out.exists();out.mkdir(parents=True)
 if mode=='metadata':case=ParserMetadata;actualPath=None;CSS_BYTES=b'';ACTUAL={};expected=5
 else:actualPath=Path(sys.argv[2]);CSS_BYTES=actualPath.read_bytes();ACTUAL=parse(CSS_BYTES.decode('utf-8'));case=CssCompatibilityContracts;expected=7
 stream=io.StringIO();start=datetime.datetime.now(datetime.timezone.utc).isoformat();result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recorded).run(unittest.defaultTestLoader.loadTestsFromTestCase(case));end=datetime.datetime.now(datetime.timezone.utc).isoformat();assert result.testsRun==expected and len(result.rows)==expected
 log=out/'unit.stdout';log.write_text(stream.getvalue());suite=E.Element('testsuite',name=case.__name__,tests=str(expected),failures=str(len(result.failures)),errors=str(len(result.errors)),skipped=str(len(result.skipped)))
 for row in result.rows:
  node=E.SubElement(suite,'testcase',classname=case.__name__,name=row['method'])
  if row['status']!='PASS':E.SubElement(node,{'FAIL':'failure','ERROR':'error','SKIP':'skipped'}[row['status']])
 xml=out/'tests.xml';E.ElementTree(suite).write(xml,encoding='utf-8',xml_declaration=True)
 value=dict(source=source,branch=branch,inputBindings=bindings,actualExit=0 if result.wasSuccessful() else 1,startUTC=start,endUTC=end,mode=mode,tests=expected,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),aborted=0,cases=result.rows,producerSha256=sha(Path(__file__)),goldenSha256=sha(G),beforeSha256=sha(before),currentReadonlySha256=sha(CURRENT),actualCssPath=str(actualPath) if actualPath else None,actualCssSha256=sha(actualPath) if actualPath else None,python=sys.version,os=dict(system=platform.system(),release=platform.release(),architecture=platform.machine()),tinycss2Version=tinycss2.__version__,javaCoverage=None,javaCoverageReason='CSS resource has no Java counters; no Production Java/application/browser/backend execution',productTests=expected if mode=='product' else 0,metadataChecks=expected if mode=='metadata' else 0,toolchainManifestSha256=sha(R.parent/'toolchain/css-contract-parser-1.4.0/manifest.json'),files={'unit.stdout':sha(log),'tests.xml':sha(xml)})
 (out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:value[k] for k in ['actualExit','mode','tests','failures','errors','skipped']}));sys.exit(value['actualExit'])
