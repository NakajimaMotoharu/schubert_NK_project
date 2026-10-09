"""Separate immutable staging, normal verify, once recover. No old runtime replay."""
import ast
from pathlib import Path
from pg813_sources import bind
R=Path(__file__).resolve().parent
def source():
 raw=bind((R/'pg778_native.py').read_text().replace('Pg778FailedRecovery','Pg779FailedRecovery').replace('pg778','pg779').replace('PG778','PG779'))
 raw=raw.replace('pg813-failed758-tools-v1','pg813-failed949-tools-v1');ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<813 single native transport>','exec'),{'__file__':str(R/'pg813_native.py'),'__name__':'__main__'})
