"""Independent actual138 from exact new source/run; no prior pass transfer."""
import pg7846_api_query_duration_post_v2 as previous
import pg7858_api_query_duration_host_v3 as host
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7858-api-query-duration-host-v3'
    post.OUT=post.host.BASE/'PG7860-api-query-duration-post-v3'
    post.PRIVATE=post.host.W/'pg7860-api-query-duration-post-v3'
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
