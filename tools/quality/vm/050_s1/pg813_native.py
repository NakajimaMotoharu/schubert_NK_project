"""Separate immutable staging, normal verify, once recover. No old runtime replay."""
import ast
from pathlib import Path
from pg813_sources import bind
R=Path(__file__).resolve().parent
def source():
 raw=bind((R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg779FailedRecovery').replace('pg778','pg779').replace('PG778','PG779'))
 raw=raw.replace('pg813-frozen-v1.safe.json','pg813-frozen-v2.safe.json').replace("action+'-v1'","action+'-v2'").replace('pg813-stage-v1.exit','pg813-stage-v2.exit').replace('pg813-verify-v1.exit','pg813-verify-v2.exit').replace('pg813-fixed-stage-v1','pg813-fixed-stage-v2');ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<813 single native transport>','exec'),{'__file__':str(R/'pg813_native.py'),'__name__':'__main__'})
