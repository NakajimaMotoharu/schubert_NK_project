"""Exactly one new external attempt, original cutoff and 1800s, observer prerequisite."""
import ast
from pathlib import Path
from pg841_resume import bind
from pg842_resume_post import AFTER
R=Path(__file__).resolve().parent
def source():
 raw=(R/'pg808_external_once.py').read_text().replace('pg805-runtime-resume-v2','pg805-runtime-resume-v1').replace('pg805-resume-tools-v2','pg805-resume-tools-v1')
 raw=bind(raw).replace('pg808','pg844').replace('PG808','PG844').replace('pg807','pg843').replace('pg806-resume-post-v1','pg842-resume-post-v1').replace('a1cd83116444d30e0ca2cb974494f0edbe30a73cd233de308c7a68a1d2f79d63',AFTER)
 ast.parse(raw);return raw
if __name__=='__main__':exec(compile(source(),'<844 fresh durable same-original external once>','exec'),{'__file__':str(R/'pg844_external_once.py'),'__name__':'__main__'})
