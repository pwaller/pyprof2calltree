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
5 6000
cfl=<filename>
cfn=mid1
calls=1 13
5 27000
cfl=<filename>
cfn=mid2
calls=1 20
5 3000
cfl=<filename>
cfn=mid3
calls=1 28
5 21000
cfl=<filename>
cfn=samename:38
calls=1 38
5 1000
cfl=<filename>
cfn=samename:44
calls=1 44
5 1000

fl=<filename>
fn=mid1
13 9000
cfl=<filename>
cfn=mid2
calls=5 20
13 15000
cfl=<filename>
cfn=bot
calls=2 24
13 2000
cfl=~
cfn=<range>
calls=1 0
13 1000

fl=<filename>
fn=mid2
20 12000
cfl=<filename>
cfn=bot
calls=6 24
20 6000

fl=<filename>
fn=bot
24 8000

fl=<filename>
fn=mid3
28 11000
cfl=<filename>
cfn=mid4
calls=5 33
28 19000

fl=<filename>
fn=mid4
33 10000
cfl=<filename>
cfn=mid3
calls=5 28
33 17000

fl=<filename>
fn=samename:38
38 1000

fl=<filename>
fn=samename:44
44 1000

fl=~
fn=<method 'disable' of '_lsprof.Profiler' objects>
0 1000

fl=~
fn=<range>
0 1000

""".replace('<filename>', top.__code__.co_filename)

expected_output_py3 = """event: ns : Nanoseconds
events: ns
summary: 57000
fl=<filename>
fn=top
5 6000
cfl=<filename>
cfn=mid1
calls=1 13
5 25000
cfl=<filename>
cfn=mid2
calls=1 20
5 3000
cfl=<filename>
cfn=mid3
calls=1 28
5 21000
cfl=<filename>
cfn=samename:38
calls=1 38
5 1000
cfl=<filename>
cfn=samename:44
calls=1 44
5 1000

fl=<filename>
fn=mid1
13 8000
cfl=<filename>
cfn=mid2
calls=5 20
13 15000
cfl=<filename>
cfn=bot
calls=2 24
13 2000

fl=<filename>
fn=mid2
20 12000
cfl=<filename>
cfn=bot
calls=6 24
20 6000

fl=<filename>
fn=bot
24 8000

fl=<filename>
fn=mid3
28 11000
cfl=<filename>
cfn=mid4
calls=5 33
28 19000

fl=<filename>
fn=mid4
33 10000
cfl=<filename>
cfn=mid3
calls=5 28
33 17000

fl=<filename>
fn=samename:38
38 1000

fl=<filename>
fn=samename:44
44 1000

fl=~
fn=<method 'disable' of '_lsprof.Profiler' objects>
0 1000

""".replace('<filename>', __file__)
