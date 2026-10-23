"""Independent actual138/17 after wrapper import correction, no test/compile replay."""
import pg7832_api_query_duration_post as previous
import pg7858_api_query_duration_host_v3 as host
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7858-api-query-duration-host-v3'
    post.OUT=post.host.BASE/'PG7864-api-query-duration-post-v4'
    post.PRIVATE=post.host.W/'pg7864-api-query-duration-post-v4'
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
