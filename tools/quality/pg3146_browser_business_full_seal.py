"""Compose Root all24 -> explicitly qualified Browser all24 -> current full owned seal.

No new Root, replay, mutation or observed-as-expected shortcut. Both original
independent oracles run again on the fixed chain; current rows must equal its end.
"""
import ast
import inspect
import json
from pyflakes.api import check
import pg3134_browser_resume_full_seal as root_seal
from pg2025_fresh_resume_full_live_seal import constant
from pg1446_current_cold_stage import W
import pg3136_browser_rows_oracle as browser
import pg3160_partial_login_rows_oracle as partial

SLOT = 'pg3146-browser-business-full-seal-v1'


def browser_source():
    raw = inspect.getsource(browser)
    nodes = [node for node in ast.parse(raw).body if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef)) and not (isinstance(node, ast.ImportFrom) and node.module == 'pg543_retirement_contract') and not (isinstance(node, ast.FunctionDef) and node.name == 'main')]
    return 'TABLES=' + repr(set(browser.TABLES)) + '\n' + '\n'.join(ast.get_source_segment(raw, node) for node in nodes)


def partial_source():
    return 'import collections,datetime,json\nTABLES=' + repr(set(browser.TABLES)) + '\n' + '\n'.join(inspect.getsource(fn) for fn in [browser.require, browser.without, browser.indexed, browser.retained, partial.qualify])


def compose(raw, chain, root_hash, partial_chain=None):
    oracle = next(ast.literal_eval(node.value) for node in ast.parse(raw).body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'ORACLE' for target in node.targets))
    joined = 'import json,hashlib,pathlib,stat,os,datetime\nROOT_SHA=' + repr(root_hash) + '\nROOT_ORACLE=' + repr(oracle) + '\nBROWSER_ORACLE=' + repr(browser_source()) + '\nPARTIAL_ORACLE=' + repr(partial_source()) + '\nPARTIAL_CHAIN=' + repr(partial_chain) + '\nCHAIN=' + repr(chain) + r'''
def require(value):
    if not value:raise ValueError('Root/Browser all24 seal chain rejected')
def qualify(old,new,cutoff,done,upper):
    p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg3134-browser-resume-full-seal-v1/before.private.json')
    s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
    raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()==ROOT_SHA)
    root=json.loads(raw)
    require(root['source']=='a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'and root['manifestSha256']=='37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863')
    first=PARTIAL_CHAIN if PARTIAL_CHAIN is not None else CHAIN
    require(root['rows']==first['before'])
    context=CHAIN['context'];a=datetime.datetime.fromisoformat(context['upper'].replace('Z','+00:00'));b=datetime.datetime.fromisoformat(upper.replace('Z','+00:00'));require(a<=b)
    root_ns={};exec(compile(ROOT_ORACLE,'<independent Root prefix oracle>','exec'),root_ns)
    prefix=root_ns['qualify'](old,first['before'],cutoff,done,first['context']['lower'])
    if PARTIAL_CHAIN is not None:
        partial_ns={};exec(compile(PARTIAL_ORACLE,'<independent one-Login failure prefix>','exec'),partial_ns)
        pc=PARTIAL_CHAIN['context'];partial_result=partial_ns['qualify'](PARTIAL_CHAIN['before'],PARTIAL_CHAIN['after'],pc['owner'],pc['lower'],pc['upper'])
        require(partial_result['all24PartialQualified']and partial_result['oldBrowserActualExit']==1 and partial_result['failedCaseNormalized']is False)
        require(PARTIAL_CHAIN['after']==CHAIN['before']and pc['owner']==context['owner'])
        require(datetime.datetime.fromisoformat(pc['upper'].replace('Z','+00:00'))<=datetime.datetime.fromisoformat(context['lower'].replace('Z','+00:00')))
    browser_ns={};exec(compile(BROWSER_ORACLE,'<independent Browser all24 oracle>','exec'),browser_ns)
    suffix=browser_ns['qualify'](CHAIN['before'],CHAIN['after'],context['owner'],context['lower'],context['upper'])
    require(new==CHAIN['after'])
    return {**prefix,'browserAll24Qualified':suffix['all24Qualified'],'exactRootBrowserCurrentChain':True,'newQuestionCount':suffix['newQuestions'],'newAuthSessionCount':suffix['freshAuthSessions'],'answerProviderAcceptance':False,'wholeAccepted':False}
'''
    # Only the outer collector's output slot changes. The composed oracle must
    # continue reading its already-sealed Root prefix, not its not-yet-created output.
    raw = constant(raw.replace(root_seal.SLOT, SLOT), 'ORACLE', joined)
    if check(raw, '<complete composed Root Browser owned fullseal>'):
        raise ValueError('whole business seal namespace required')
    compile(raw, '<same current Root and Browser fullseal>', 'exec')
    return raw


def payload(binding):
    actual = json.loads((W / 'pg3164-browser-business-actual-v2/manifest.safe.json').read_bytes())
    if not (actual['actualExit'] == 0 and actual['sourceQualified'] and actual['all24IndependentPost'] and actual['sameFourOrdinaryOwnersBeforeAfter'] and actual['passedCases'] == 12):
        raise ValueError('actual complete finite Browser and independent all24 required')
    cases = W / 'pg3164-browser-business-actual-v2/cases'
    chain = {name: json.loads((cases / file).read_bytes()) for name, file in [('before', 'before-rows.private.json'), ('after', 'after-rows.private.json'), ('context', 'context.private.json')]}
    browser.qualify(chain['before'], chain['after'], chain['context']['owner'], chain['context']['lower'], chain['context']['upper'])
    original = json.loads((W / root_seal.SLOT / 'manifest.safe.json').read_bytes())
    prefix_dir = W / 'pg3162-failed-menu-partial-login-post-v1'
    proof = json.loads((prefix_dir / 'manifest.safe.json').read_bytes())
    if not (proof['actualExit'] == 0 and proof['sourceQualified'] and proof['result']['all24PartialQualified']):
        raise ValueError('actual failed-cohort prefix qualification required')
    prefix = {}
    for name in ['before', 'after', 'context']:
        path = prefix_dir / (name + '.private.json')
        import hashlib
        if hashlib.sha256(path.read_bytes()).hexdigest() != proof['privateHashes'][name]:
            raise ValueError('qualified failed-cohort prefix bytes drifted')
        prefix[name] = json.loads(path.read_bytes())
    partial.qualify(prefix['before'], prefix['after'], prefix['context']['owner'], prefix['context']['lower'], prefix['context']['upper'])
    return compose(root_seal.payload(binding), chain, original['privateBeforeSha256'], prefix)


def main():
    ns = {**root_seal.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(root_seal.main), '<composed Browser owned seal dispatcher>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
