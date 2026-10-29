"""Exact reviewed pure JDBC fixture text preflight; not a permission/safety or runtime override."""
NAMES={'AsyncJobMetricCollectorTest','AsyncJobMetricRecorderTest','AsyncJobCountRepositoryTest'}
FORBIDDEN=('DriverManager','DataSource','InitialContext','org.postgresql','getConnection(','jdbc:','Class.forName(','ProcessBuilder','Runtime.getRuntime(','EmbeddedActiveMQ','ActiveMQConnectionFactory','preserveFatal(','ServiceProcessResources','Files.','Path.of(')
REQUIRED=('Proxy.newProxyInstance(','Connection.class','PreparedStatement.class','ResultSet.class','borrowed connection must not be mutated or closed','SELECT state, COUNT(*) AS job_count FROM schubert.async_jobs GROUP BY state')

def eligible(texts):
    if not isinstance(texts,dict) or set(texts)!=NAMES or any(not isinstance(v,str) for v in texts.values()):
        return False
    if any(term in text for text in texts.values() for term in FORBIDDEN):
        return False
    return all(term in texts['AsyncJobCountRepositoryTest'] for term in REQUIRED)
