"""Exact before-manifest name/hash binding before candidate body, no candidate execution."""
from pathlib import Path
import ast,re,datetime,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check_before(source,suffix):
 assert isinstance(suffix,str) and re.fullmatch(r'PG[0-9]+-[a-z0-9-]+-before-v1/manifest\.json',suffix)
 values=[n.value for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Constant) and isinstance(n.value,str)];refs=[v for v in values if re.search(r'(?:^|/)PG[0-9]+-[a-z0-9-]+-before-v1/manifest\.json$',v)];assert len(refs)==1 and refs[0].endswith(suffix);return dict(beforeLiteral=refs[0],fullSuffix=suffix,candidateExecuted=False)

def main():
 current=B/'input/1020_web_range_generated_configured_prepare.py';oldfile=B/'evidence/PG25690-generated-before-ref-before-v1/prepare.failed.py.txt';old=oldfile.read_text();cur=current.read_text();a='PG25676-web-range-parser-owner-before-v1/manifest.json';n='PG25676-range-generated-direct-before-v1/manifest.json';assert old.count(a)==1 and cur.replace(n,a)==old and ast.dump(ast.parse(cur.replace(n,a)))==ast.dump(ast.parse(old));checks=[]
 def reject(label,s,suffix=n):
  try:check_before(s,suffix)
  except (AssertionError,SyntaxError):checks.append(label);return
  raise AssertionError(label)
 reject('actual old correct-number/wrong-description',old)
 reject('wrong-number',cur.replace('PG25676-range-generated','PG25675-range-generated'))
 reject('missing-before',"a='no before binding'")
 reject('duplicate-before',cur+"\nx='"+n+"'\n")
 reject('wrong-version',cur.replace('direct-before-v1','direct-before-v2'))
 reject('boolean-expected-suffix',cur,True)
 reject('absolute-expected',cur,'/private/'+n)
 reject('invalid-source','broken=((')
 rows=[]
 for path,ref in [(current,B/'evidence/PG25676-range-generated-direct-before-v1/manifest.json'),(B/'input/1015_web_range_parser_configured_prepare.py',B/'evidence/PG25652-web-range-parser-owner-before-v1/manifest.json')]:
  suffix=ref.parent.name+'/manifest.json';contract=check_before(path.read_text(),suffix);v=json.loads(ref.read_bytes());assert v['actualExit']==0 and len(v['sources'])==1 and v['sources'][0]['path']=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/HttpByteRangeParserTest.java';rows.append(dict(path=str(path.relative_to(R)),sha256=sha(path),beforeManifest=dict(path=str(ref.relative_to(R)),sha256=sha(ref)),contract=contract,applicableFix=path==current))
 O=B/'evidence/PG25692-generated-before-ref-independent-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),oldToolSha256=sha(oldfile),fixedToolSha256=sha(current),onlyOneBeforeLiteralChanged=True,otherAstAndOraclesUnchanged=True,negativeChecks=len(checks),negativeLabels=checks,currentExplicitTargets=2,rows=rows,futurePreflightTargetPending=True,candidatesExecuted=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,bug='BUG-2611',ykt='YKT-2301',toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,negativeChecks=len(checks),targets=2,manifestSha256=sha(O/'manifest.json'))))

if __name__=='__main__':main()
