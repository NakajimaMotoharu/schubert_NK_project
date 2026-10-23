"""Independent corrected138/17 exact XML/CRC/four counters/static; old failed run never transferred."""
import pg7832_api_query_duration_post as previous
import pg7844_api_query_duration_host as host
def configure():
    post=previous.configure()
    post.SLOT=host.SLOT;post.RUN='PG7844-api-query-duration-host-v2'
    post.OUT=post.host.BASE/'PG7846-api-query-duration-post-v2'
    post.PRIVATE=post.host.W/'pg7846-api-query-duration-post-v2'
    return post
if __name__=='__main__':
    host.dependency.verify_inputs()
    configure().main()
