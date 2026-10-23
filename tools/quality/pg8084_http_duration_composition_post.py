"""Same original90/current20 post on composition source; static missing classes are not ignored."""
import pg8062_http_duration_safe_post as post
import pg8082_http_duration_composition_host as original
if __name__=='__main__':
    post.original=original
    post.SLOT=post.host.W/'pg8084-http-duration-composition-post-v1'
    post.OUT=post.host.BASE/'PG8084-http-duration-composition-post-v1'
    post.main()
