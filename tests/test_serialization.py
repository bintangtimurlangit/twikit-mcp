"""
Serialization robustness tests for the MCP layer.

twikit exposes tweet fields as properties that index a raw ``_legacy`` dict and
raise KeyError when X omits a field (issue #417). The serializers must degrade to
None rather than propagate the error.
"""
from twikit_mcp.serialization import tweet_to_dict, user_to_dict, paginated


class FakeUser:
    id = '123'
    screen_name = 'nasa'
    name = 'NASA'
    followers_count = 100

    @property
    def description(self):  # a property that blows up, like twikit's _legacy access
        raise KeyError('description')


class FakeTweet:
    id = '999'
    text = 'Hello world'
    user = FakeUser()

    @property
    def favorite_count(self):
        raise KeyError('favorite_count')  # field omitted by API

    @property
    def view_count(self):
        return 4200


def test_user_serialization_survives_keyerror_property():
    d = user_to_dict(FakeUser())
    assert d['screen_name'] == 'nasa'
    assert d['followers_count'] == 100
    assert d['description'] is None  # KeyError swallowed -> None


def test_tweet_serialization_survives_keyerror_property():
    d = tweet_to_dict(FakeTweet())
    assert d['id'] == '999'
    assert d['text'] == 'Hello world'
    assert d['favorite_count'] is None   # omitted field
    assert d['view_count'] == 4200
    assert d['user']['screen_name'] == 'nasa'


def test_paginated_wraps_result():
    class FakeResult(list):
        next_cursor = 'CURSOR123'

    result = FakeResult([FakeTweet(), FakeTweet()])
    out = paginated(tweet_to_dict, result)
    assert out['count'] == 2
    assert out['next_cursor'] == 'CURSOR123'
    assert len(out['items']) == 2


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            fn()
            print(f'ok  {name}')
    print('all passed')
