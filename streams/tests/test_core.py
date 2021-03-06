from datetime import timedelta
from operator import add
from time import time

import pytest

from distributed.utils_test import inc, double, gen_test
from distributed.utils import tmpfile
from tornado import gen
from tornado.queues import Queue
from tornado.ioloop import IOLoop

import streams as s

from ..core import Stream
from streams.sources import sink_to_file, Counter


def test_basic():
    source = Stream()
    b1 = source.map(inc)
    b2 = source.map(double)

    c = b1.scan(add)

    Lc = c.sink_to_list()
    Lb = b2.sink_to_list()

    for i in range(4):
        source.emit(i)

    assert Lc == [3, 6, 10]
    assert Lb == [0, 2, 4, 6]


def test_filter():
    source = Stream()
    L = source.filter(lambda x: x % 2 == 0).sink_to_list()

    for i in range(10):
        source.emit(i)

    assert L == [0, 2, 4, 6, 8]


def test_map():
    def add(x=0, y=0):
        return x + y

    source = Stream()
    L = source.map(add, y=10).sink_to_list()

    source.emit(1)

    assert L[0] == 11


def test_remove():
    source = Stream()
    L = source.remove(lambda x: x % 2 == 0).sink_to_list()

    for i in range(10):
        source.emit(i)

    assert L == [1, 3, 5, 7, 9]


def test_partition():
    source = Stream()
    L = source.partition(2).sink_to_list()

    for i in range(10):
        source.emit(i)

    assert L == [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]


def test_sliding_window():
    source = Stream()
    L = source.sliding_window(2).sink_to_list()

    for i in range(10):
        source.emit(i)

    assert L == [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5),
                 (5, 6), (6, 7), (7, 8), (8, 9)]


@gen_test()
def test_backpressure():
    q = Queue(maxsize=2)

    source = Stream()
    source.map(inc).scan(add, start=0).sink(q.put)

    @gen.coroutine
    def read_from_q():
        while True:
            yield q.get()
            yield gen.sleep(0.1)

    IOLoop.current().add_callback(read_from_q)

    start = time()
    for i in range(5):
        yield source.emit(i)
    end = time()

    assert end - start >= 0.2


@gen_test()
def test_timed_window():
    source = Stream()
    a = source.timed_window(0.01)

    L = a.sink_to_list()

    for i in range(10):
        yield source.emit(i)
        yield gen.sleep(0.004)

    yield gen.sleep(a.interval)
    assert L
    assert sum(L, []) == list(range(10))
    assert all(len(x) <= 3 for x in L)
    assert any(len(x) >= 2 for x in L)

    yield gen.sleep(0.1)
    assert not L[-1]


@gen_test()
def test_timed_window_backpressure():
    q = Queue(maxsize=1)

    source = Stream()
    source.timed_window(0.01).sink(q.put)

    @gen.coroutine
    def read_from_q():
        while True:
            yield q.get()
            yield gen.sleep(0.1)

    IOLoop.current().add_callback(read_from_q)

    start = time()
    for i in range(5):
        yield source.emit(i)
        yield gen.sleep(0.01)
    stop = time()

    assert stop - start > 0.2


def test_sink_to_file():
    with tmpfile() as fn:
        source = Stream()
        with sink_to_file(fn, source) as f:
            source.emit('a')
            source.emit('b')

        with open(fn) as f:
            data = f.read()

        assert data == 'a\nb\n'


@gen_test()
def test_counter():
    source = Counter(interval=0.01)
    L = source.sink_to_list()
    yield gen.sleep(0.1)

    assert L


@gen_test()
def test_rate_limit():
    source = Stream()
    L = source.rate_limit(0.05).sink_to_list()

    start = time()
    for i in range(5):
        yield source.emit(i)
    stop = time()
    assert stop - start > 0.2
    assert len(L) == 5


@gen_test()
def test_delay():
    source = Stream()
    L = source.delay(0.02).sink_to_list()

    for i in range(5):
        yield source.emit(i)

    assert not L

    yield gen.sleep(0.04)

    assert len(L) < 5

    yield gen.sleep(0.1)

    assert len(L) == 5


@gen_test()
def test_buffer():
    source = Stream()
    L = source.map(inc).buffer(10).map(inc).rate_limit(0.05).sink_to_list()

    start = time()
    for i in range(10):
        yield source.emit(i)
    stop = time()

    assert stop - start < 0.01
    assert not L

    start = time()
    for i in range(5):
        yield source.emit(i)
    stop = time()

    assert L
    assert stop - start > 0.04


def test_zip():
    a = Stream()
    b = Stream()
    c = s.zip(a, b)

    L = c.sink_to_list()

    a.emit(1)
    b.emit('a')
    a.emit(2)
    b.emit('b')

    assert L == [(1, 'a'), (2, 'b')]
    d = Stream()
    # test zip from the object itself
    # zip 3 streams together
    e = a.zip(b, d)
    L2 = e.sink_to_list()

    a.emit(1)
    b.emit(2)
    d.emit(3)
    assert L2 == [(1, 2, 3)]


def test_combine_latest():
    a = Stream()
    b = Stream()
    c = a.combine_latest(b)
    d = a.combine_latest(b, emit_on=[a, b])

    L = c.sink_to_list()
    L2 = d.sink_to_list()

    a.emit(1)
    a.emit(2)
    b.emit('a')
    a.emit(3)
    b.emit('b')

    assert L == [(2, 'a'), (3, 'a'), (3, 'b')]
    assert L2 == [(2, 'a'), (3, 'a'), (3, 'b')]


def test_combine_latest_emit_on():
    a = Stream()
    b = Stream()
    c = a.combine_latest(b, emit_on=a)

    L = c.sink_to_list()

    a.emit(1)
    b.emit('a')
    a.emit(2)
    a.emit(3)
    b.emit('b')
    a.emit(4)

    assert L == [(2, 'a'), (3, 'a'), (4, 'b')]


@gen_test()
def test_zip_timeout():
    a = Stream()
    b = Stream()
    c = s.zip(a, b, maxsize=2)

    L = c.sink_to_list()

    a.emit(1)
    a.emit(2)

    future = a.emit(3)
    with pytest.raises(gen.TimeoutError):
        yield gen.with_timeout(timedelta(seconds=0.01), future)

    b.emit('a')
    yield future

    assert L == [(1, 'a')]


def test_frequencies():
    source = Stream()
    L = source.frequencies().sink_to_list()

    source.emit('a')
    source.emit('b')
    source.emit('a')

    assert L[-1] == {'a': 2, 'b': 1}


def test_concat():
    source = Stream()
    L = source.concat().sink_to_list()

    source.emit([1, 2, 3])
    source.emit([4, 5])
    source.emit([6, 7, 8])

    assert L == [1, 2, 3, 4, 5, 6, 7, 8]


def test_unique():
    source = Stream()
    L = source.unique().sink_to_list()

    source.emit(1)
    source.emit(2)
    source.emit(1)

    assert L == [1, 2]


def test_unique_key():
    source = Stream()
    L = source.unique(key=lambda x: x % 2, history=1).sink_to_list()

    source.emit(1)
    source.emit(2)
    source.emit(4)
    source.emit(6)
    source.emit(3)

    assert L == [1, 2, 3]


def test_unique_history():
    source = Stream()
    s = source.unique(history=2)
    L = s.sink_to_list()

    source.emit(1)
    source.emit(2)
    source.emit(1)
    source.emit(2)
    source.emit(1)
    source.emit(2)

    assert L == [1, 2]

    source.emit(3)
    source.emit(2)

    assert L == [1, 2, 3]

    source.emit(1)

    assert L == [1, 2, 3, 1]


def test_union():
    a = Stream()
    b = Stream()
    c = Stream()

    L = a.union(b, c).sink_to_list()

    a.emit(1)
    assert L == [1]
    b.emit(2)
    assert L == [1, 2]
    a.emit(3)
    assert L == [1, 2, 3]
    c.emit(4)
    assert L == [1, 2, 3, 4]


def test_collect():
    source1 = Stream()
    source2 = Stream()
    collector = source1.collect()
    L = collector.sink_to_list()
    source2.sink(collector.flush)

    source1.emit(1)
    source1.emit(2)
    assert L == []

    source2.emit('anything')  # flushes collector
    assert L == [(1, 2)]

    source2.emit('anything')
    assert L == [(1, 2), ()]

    source1.emit(3)
    assert L == [(1, 2), ()]

    source2.emit('anything')
    assert L == [(1, 2), (), (3,)]
