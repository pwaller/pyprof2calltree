# We're going to use a custom timer, so we don't actually have to do anything
# in these functions.
def top():
    mid1()
    mid2()
    mid3(5)
    C1.samename()
    C2.samename()

def mid1():
    bot()
    for i in range(5):
        mid2()
    bot()

def mid2():
    bot()

def bot():
    pass

def mid3(x):
    if x > 0:
        mid4(x)

def mid4(x):
    mid3(x - 1)

class C1(object):
    @staticmethod
    def samename():
        pass

class C2(object):
    @staticmethod
    def samename():
        pass

expected_output_py2 = """event: ns : Nanoseconds
events: ns
summary: 59000
fl=<filename>
fn=top
3 6000
cfl=<filename>
cfn=mid1
calls=1 10
3 27000
cfl=<filename>
cfn=mid2
calls=1 16
3 3000
cfl=<filename>
cfn=mid3
calls=1 22
3 21000
cfl=<filename>
cfn=samename:30
calls=1 30
3 1000
cfl=<filename>
cfn=samename:35
calls=1 35
3 1000

fl=<filename>
fn=mid1
10 9000
cfl=<filename>
cfn=mid2
calls=5 16
10 15000
cfl=<filename>
cfn=bot
calls=2 19
10 2000
cfl=~
cfn=<range>
calls=1 0
10 1000

fl=<filename>
fn=mid2
16 12000
cfl=<filename>
cfn=bot
calls=6 19
16 6000

fl=<filename>
fn=bot
19 8000

fl=<filename>
fn=mid3
22 11000
cfl=<filename>
cfn=mid4
calls=5 26
22 19000

fl=<filename>
fn=mid4
26 10000
cfl=<filename>
cfn=mid3
calls=5 22
26 17000

fl=<filename>
fn=samename:30
30 1000

fl=<filename>
fn=samename:35
35 1000

fl=~
fn=<method 'disable' of '_lsprof.Profiler' objects>
0 1000

fl=~
fn=<range>
0 1000

""".replace('<filename>', __file__)

expected_output_py3 = """event: ns : Nanoseconds
events: ns
summary: 57000
fl=<filename>
fn=top
3 6000
cfl=<filename>
cfn=mid1
calls=1 10
3 25000
cfl=<filename>
cfn=mid2
calls=1 16
3 3000
cfl=<filename>
cfn=mid3
calls=1 22
3 21000
cfl=<filename>
cfn=samename:30
calls=1 30
3 1000
cfl=<filename>
cfn=samename:35
calls=1 35
3 1000

fl=<filename>
fn=mid1
10 8000
cfl=<filename>
cfn=mid2
calls=5 16
10 15000
cfl=<filename>
cfn=bot
calls=2 19
10 2000

fl=<filename>
fn=mid2
16 12000
cfl=<filename>
cfn=bot
calls=6 19
16 6000

fl=<filename>
fn=bot
19 8000

fl=<filename>
fn=mid3
22 11000
cfl=<filename>
cfn=mid4
calls=5 26
22 19000

fl=<filename>
fn=mid4
26 10000
cfl=<filename>
cfn=mid3
calls=5 22
26 17000

fl=<filename>
fn=samename:30
30 1000

fl=<filename>
fn=samename:35
35 1000

fl=~
fn=<method 'disable' of '_lsprof.Profiler' objects>
0 1000

""".replace('<filename>', __file__)
