# coding=utf-8

# Copyright (C) 2013-2015 David R. MacIver (david@drmaciver.com)

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import, \
    unicode_literals

import math
import time
from random import Random

import pytest
from hypothesis import Settings, find, given, assume
from hypothesis.errors import Timeout, NoSuchExample, \
    DefinitelyNoSuchExample
from hypothesis.specifiers import streaming, dictionary, sampled_from


@given(Random, settings=Settings(max_examples=10, min_satisfying_examples=1))
def test_only_raises_if_actually_considered_all(r):
    examples = set()
    settings = Settings(min_satisfying_examples=0, max_examples=100)

    def consider_and_append(x):
        examples.add(x)
        return False
    s = sampled_from(range(100))
    with pytest.raises(NoSuchExample) as e:
        find(s, consider_and_append, settings=settings)

    assume(len(examples) < 100)
    assert not isinstance(e.value, DefinitelyNoSuchExample)


def test_can_find_an_int():
    assert find(int, lambda x: True) == 0
    assert find(int, lambda x: x >= 13) == 13


def test_can_find_list():
    x = find([int], lambda x: sum(x) >= 10)
    assert sum(x) == 10


def test_can_find_nan():
    find(float, math.isnan)


def test_can_find_nans():
    x = find([float], lambda x: math.isnan(sum(x)))
    if len(x) == 1:
        assert math.isnan(x[0])
    else:
        assert 2 <= len(x) <= 3


def test_find_streaming_int():
    n = 100
    r = find(streaming(int), lambda x: all(t >= 1 for t in x[:n]))
    assert list(r[:n]) == [1] * n


def test_raises_when_no_example():
    settings = Settings(
        max_examples=20,
        min_satisfying_examples=0,
    )
    with pytest.raises(NoSuchExample):
        find(int, lambda x: False, settings=settings)


def test_raises_more_specifically_when_exhausted():
    with pytest.raises(DefinitelyNoSuchExample):
        find(bool, lambda x: False)


def test_condition_is_name():
    settings = Settings(
        max_examples=20,
        min_satisfying_examples=0,
    )
    with pytest.raises(DefinitelyNoSuchExample) as e:
        find(bool, lambda x: False, settings=settings)
    assert 'lambda x:' in e.value.args[0]

    with pytest.raises(NoSuchExample) as e:
        find(int, lambda x: '☃' in str(x), settings=settings)
    assert 'lambda x:' in e.value.args[0]

    def bad(x):
        return False

    with pytest.raises(NoSuchExample) as e:
        find(int, bad, settings=settings)
    assert 'bad' in e.value.args[0]


def test_find_dictionary():
    assert len(find(
        dictionary(int, int),
        lambda xs: any(kv[0] > kv[1] for kv in xs.items()))) == 1


def test_times_out():
    with pytest.raises(Timeout) as e:
        find(
            int,
            lambda x: time.sleep(0.05) or False,
            settings=Settings(timeout=0.01))

    e.value.args[0]
