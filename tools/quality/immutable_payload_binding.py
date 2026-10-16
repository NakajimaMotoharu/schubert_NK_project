"""Bind operator namespaces without rewriting already-composed oracle/snapshot literals."""
import ast

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
