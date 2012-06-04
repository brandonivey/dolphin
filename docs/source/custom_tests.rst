Custom Tests
============

Dolphin can also support custom tests. They are simply functions by the form of::

    def test_func(key, **kwargs):
        return True or False

kwargs will contain the backend which can be used to get the request object if necessary
(though depending on how the test is called, it may be passed as a keyword argument).
