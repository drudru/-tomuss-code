
def run(t):
    t.goto_url("http://%s:8888/=super.user/9999/Test/UE-INF9999L" % t.server)
    t.check_image('table')
