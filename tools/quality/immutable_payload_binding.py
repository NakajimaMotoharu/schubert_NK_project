"""Bind operator namespaces without rewriting already-composed oracle/snapshot literals."""
import ast
from collections import Counter

PROTECTED={'ORACLE','CHAIN','ROOT_ORACLE','BROWSER_ORACLE','PARTIAL_CHAIN','GUARD','RECEIPT'}


def bind_preserving_payloads(raw,binder):
    try:tree=ast.parse(raw)
    except SyntaxError:return binder(raw)  # Java declarations, not Python embedded data.
    segments=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in node.targets):
            segment=ast.get_source_segment(raw,node)
            if segment is None or raw.count(segment)!=1:raise ValueError('one exact immutable payload assignment required')
            segments.append(segment)
    value=raw;protected={}
    for index,segment in enumerate(sorted(segments,key=len,reverse=True)):
        if segment not in value:continue  # Entire nested assignment already protected by its outer value.
        marker='__PGPT_IMMUTABLE_PAYLOAD_'+str(index)+'__'
        if marker in value:raise ValueError('immutable payload marker collision')
        value=value.replace(segment,marker,1);protected[marker]=segment
    value=binder(value)
    for marker,segment in protected.items():
        if value.count(marker)!=1:raise ValueError('binder modified immutable payload boundary')
        value=value.replace(marker,segment,1)
    ast.parse(value);return value


def transform_bundle_preserving_payloads(sources,transform):
    """Protect literals across a multi-file generator, not just its initial rename.

    New helpers may be added and files renamed, but every pre-existing protected
    assignment must survive exactly once and remain an actual Python assignment.
    Java namespaces are transformed normally; database/oracle capsules in this
    graph reside only in the explicitly named Python assignments above.
    """
    if type(sources)is not dict or any(type(k)is not str or type(v)is not str for k,v in sources.items()):
        raise ValueError('textual immutable source bundle required')
    def segments(name,raw):
        if not name.endswith('.py'):return []
        try:tree=ast.parse(raw)
        except SyntaxError:raise ValueError('complete Python bundle syntax required')from None
        return [ast.get_source_segment(raw,node)for node in ast.walk(tree)
                if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id in PROTECTED for t in node.targets)]
    prefix='__pgpt_immutable_bundle_'
    while any(prefix in raw for raw in sources.values()):prefix+='x'
    def letters(number):
        value=''
        while True:
            number,digit=divmod(number,26);value=chr(97+digit)+value
            if number==0:return value
    masked={};capsules={};expected=[]
    for name,raw in sources.items():
        value=raw
        for segment in sorted(segments(name,raw),key=len,reverse=True):
            if segment is None:raise ValueError('exact protected assignment extent required')
            if segment not in value:continue
            marker=prefix+letters(len(capsules))+'__'
            value=value.replace(segment,marker,1);capsules[marker]=segment;expected.append(segment)
        masked[name]=value
    result=transform(masked)
    if type(result)is not dict or any(type(k)is not str or type(v)is not str for k,v in result.items()):
        raise ValueError('textual transformed source bundle required')
    result=dict(result)
    for marker,segment in capsules.items():
        if sum(raw.count(marker)for raw in result.values())!=1:raise ValueError('generator lost or duplicated protected payload')
        for name,raw in result.items():
            if marker in raw:result[name]=raw.replace(marker,segment,1);break
    actual=[part for name,raw in result.items()for part in segments(name,raw)]
    if Counter(actual)!=Counter(expected):raise ValueError('generator changed protected assignment semantics')
    return result
