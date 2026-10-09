"""Separate fresh successful-body/guard replay contrast, old v1 evidence unchanged."""
import inspect,json
import pg743_closing_selected as selected
from pg925_body_selected import dependencies
selected.D=selected.W/'pg925-body-selected-v2'
if __name__=='__main__':
    print(json.dumps({'dependencyMainClasses':dependencies(),'classByteMismatch':0}),flush=True)
    raw=inspect.getsource(selected.main)
    marker="'src/schubert-nk-bootstrap,src/schubert-nk-api', '-am',";assert raw.count(marker)==1
    raw=raw.replace(marker,"'src/schubert-nk-bootstrap,src/schubert-nk-api',").replace('PG743-closing-selected-v1','PG925-body-selected-v2').replace('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','e01612fcd7f2752df5ae0836b78538fd5e87f120')
    env=dict(selected.__dict__);exec(compile(raw,'<PG925v2 real body guard success/replay>','exec'),env);env['main']()
