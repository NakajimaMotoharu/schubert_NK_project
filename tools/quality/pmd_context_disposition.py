"""Finding dispositions retain raw warnings; unknown architecture is never an exemption."""
def standalone_thread_context(row,context):
    if row.get('rule')!='DoNotUseThreads':return None
    path=row.get('path');bound=context.get('sourceSha256',{}).get(path)
    if bound is None or bound!=row.get('sourceSha256'):raise ValueError('finding source unbound')
    if not(context.get('approvedDirectJavaProcess')is True and context.get('externalJavaEEManaged')is False and context.get('noManagedDeploymentDescriptors')is True and context.get('ruleExplicitlyJ2EE')is True):return None
    module=path.split('/')[1]
    if context.get('moduleRoles',{}).get(module)not in {'STANDALONE_JAVA_SERVICE','LIBRARY_ONLY_IN_STANDALONE_GRAPH'}:return None
    return {'disposition':'CONTEXT_NOT_APPLICABLE_J2EE_RULE','basis':'Primary vendor rule requires externally managed J2EE threads; approved SS311/342 specifies direct standalone Java processes and their shared libraries. Exact source/architecture evidence retained.','scope':'VENDOR_CONTEXT_ONLY_NOT_FUNCTIONAL_CORRECTNESS','qualityGatePass':False}
