"""Pure metadata guards for single/multiple source schema; no Product/Test import or source read."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,subprocess
R=Path(__file__).resolve().parents[4];OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22614-projection-source-schema-guards-v1'
def main():
 assert not OUT.exists();p=R/'evidence/01_PT/018_NK-OPS-001/input/232_ordinary85_classification_source_seal.py';spec=importlib.util.spec_from_file_location('owned_seal_metadata',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);a='src/sample/src/test/java/OneTest.java';b='src/sample/src/test/java/TwoTest.java';one=dict(inputHashes={a:'0'*64});two=dict(inputHashes={a:'0'*64,b:'0'*64});assert m.source_for({},one)==a and m.source_for(dict(sourcePath=a),one)==a;rejected=[]
 for label,row,parent in [('ambiguousMissing',{},two),('unknownExplicit',dict(sourcePath=b),one),('missingParent',{},dict(inputHashes={}))]:
  try:m.source_for(row,parent)
  except AssertionError:rejected.append(label)
 assert len(rejected)==3;OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productTestsExecuted=0,positiveCases=2,rejectedMetadataCases=rejected,expectedSourceLiteral=a,source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command=['python3','-B',str(Path(__file__).relative_to(R))],environment=dict(python=__import__('sys').version),subject=dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()));(OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rejected=3,accepted=2,productTests=0)))
if __name__=='__main__':main()
