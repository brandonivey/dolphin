Custom Tests
============

Dolphin can also support custom tests. Custom tests are conditions placed on flags that
are checked in addition to the existing conditions, i.e. checking if a username matches a
string. They are simply functions by the form of::

    def test_func(key, **kwargs):
        return True or False

kwargs will contain the backend which can be used to get the request object if necessary
(though depending on how the test is called, it may be passed as a keyword argument).
