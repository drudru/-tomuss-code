
def run(t):
    t.goto_url("http://%s:8888/=super.user/" % t.server)
    t.check_image('home')
    
    t.xnee.key('2')
    t.wait_change('Key stroke in UE search', 'fast')
    t.check_image('home_search_ue')

    t.xnee.key('Tab') # On the 'find' button
    t.xnee.key('Tab') # On the search input field
    t.xnee.key('G')
    t.wait_change('Key stroke in student search', 'fast')
    t.check_image('home_search_student')

    t.goto_url("http://%s:8888/=ue1.master/" % t.server)
    t.check_image('home_user')

    t.goto_url("http://%s:8888/=super.user/2008/Test/average" % t.server,
               speed='veryslow')
    t.check_image('home_average')

    t.goto_url("http://%s:8888/=super.user/2008/Test/test_types" % t.server,
               speed='veryslow')
    t.check_image('home_types')

