"""Same-source genuine90/current20 independent CRC/four counters and all raw static."""
import pg8062_http_duration_safe_post as post
import pg8100_http_duration_nullable_host as original
if __name__=='__main__':
    post.original=original
    post.SLOT=post.host.W/'pg8102-http-duration-nullable-post-v1'
    post.OUT=post.host.BASE/'PG8102-http-duration-nullable-post-v1'
    post.main()
