import time

def run(t):
    t.goto_url("http://%s:8888/=super.user/" % t.server)
    time.sleep(3)
    t.check_image('home')

    time.sleep(1)
    t.xnee.key('2')
    t.check_image('home_search_ue', message="Key stroke in UE search")

    t.xnee.key('Tab') # On the 'find' button
    t.xnee.key('Tab') # On the search input field
    t.xnee.key('G')
    t.check_image('home_search_student',message='Key stroke in student search')

    t.goto_url("http://%s:8888/=ue1.master/" % t.server)
    t.check_image('home_user', timeout=10) # timeout for epiphany bug ?

    t.goto_url("http://%s:8888/=super.user/9999/Test/average" % t.server)
    t.check_image('home_average')

    t.goto_url("http://%s:8888/=super.user/9999/Test/test_types" % t.server)
    t.check_image('home_types')

    # t.goto_url("http://%s:8888/=super.user/9999/Dossiers/javascript_regtest_ue" % t.server)
    # t.check_image('home_javascript', wait=40)
