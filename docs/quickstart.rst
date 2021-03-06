=================
Quick start guide
=================

This document should talk you through everything you need to get started with
Hypothesis.

----------
An example
----------

Suppose we've written a `run length encoding
<http://en.wikipedia.org/wiki/Run-length_encoding>`_ system and we want to test
it out.

We have the following code which I took straight from the
`Rosetta Code <http://rosettacode.org/wiki/Run-length_encoding>`_ wiki (OK, I
removed some commented out code and fixed the formatting, but there are no
functional modifications):


.. code:: python

  def encode(input_string):
      count = 1
      prev = ''
      lst = []
      for character in input_string:
          if character != prev:
              if prev:
                  entry = (prev, count)
                  lst.append(entry)
              count = 1
              prev = character
          else:
              count += 1
      else:
          entry = (character, count)
          lst.append(entry)
      return lst


  def decode(lst):
      q = ''
      for character, count in lst:
          q += character * count
      return q


We want to write a test for this that will check some invariant of these
functions.

The invariant one tends to try when you've got this sort of encoding /
decoding is that if you encode something and then decode it then you get the same
value back.

Lets see how you'd do that with Hypothesis:


.. code:: python

  @given(str)
  def test_decode_inverts_encode(s):
      assert decode(encode(s)) == s

(For this example we'll just let pytest discover and run the test. We'll cover other
ways you could have run it later).

The @given decorator takes our test function and turns it into a parametrized one.
When it is called, Hypothesis will run the test function over a wide range of matching
data.

Anyway, this test immediately finds a bug in the code:

.. code::

  Falsifying example: test_decode_inverts_encode(s='')

  UnboundLocalError: local variable 'character' referenced before assignment

Hypothesis correctly points out that this code is simply wrong if called on
an empty string.

If we fix that by just adding the following code to the beginning of the function
then Hypothesis tells us the code is correct (by doing nothing as you'd expect
a passing test to).

.. code:: python

  
    if not input_string:
        return []


Suppose we had a more interesting bug and forgot to reset the count each time.

Hypothesis quickly informs us of the following example:

.. code::

  Falsifying example: test_decode_inverts_encode(s='001')

Note that the example provided is really quite simple. Hypothesis doesn't just
find *any* counter-example to your tests, it knows how to simplify the examples
it finds to produce small easy to understand examples. In this case, two identical
values are enough to set the count to a number different from one, followed by another
distinct value which should have reset the count but in this case didn't.

Some side notes:
  
* The examples Hypothesis provides are valid Python code you can run. When called with the arguments explicitly provided the test functions Hypothesis uses are just calls to the underlying test function.
* Because of the use of str this behaves differently in python 2 and python 3. In python 2 the example would have been something like '\\x02\\x02\\x00' because str is a binary type. Hypothesis works equally well in both python 2 and python 3, but if you want consistent behaviour across the two you need something like `six <https://pypi.python.org/pypi/six>`_'s text_type. 

----------
Installing
----------

Hypothesis is `available on pypi as "hypothesis"
<https://pypi.python.org/pypi/hypothesis>`_. You can install it with:

.. code:: bash

  pip install hypothesis

or 

.. code:: bash 

  easy_install hypothesis

If you want to install directly from the source code (e.g. because you want to
make changes and install the changed version) you can do this with:

.. code:: bash

  python setup.py install

You should probably run the tests first to make sure nothing is broken. You can
do this with:

.. code:: bash

  python setup.py test 

Note that if they're not already installed this will try to install the test
dependencies.

You may wish to do all of this in a `virtualenv <https://virtualenv.pypa.io/en/latest/>`_. For example:

.. code:: bash

  virtualenv venv
  source venv/bin/activate
  pip install hypothesis

Will create an isolated environment for you to try hypothesis out in without
affecting your system installed packages.

-------------
Running tests
-------------

In our example above we just let pytest discover and run our tests, but we could
also have run it explicitly ourselves:

.. code:: python

  if __name__ == '__main__':
      test_decode_inverts_encode()

We could also have done this as a unittest TestCase:


.. code:: python

  import unittest


  class TestEncoding(unittest.TestCase):
      @given(str)
      def test_decode_inverts_encode(self, s):
          self.assertEqual(decode(encode(s)), s)

  if __name__ == '__main__':
      unittest.main()

A detail: This works because Hypothesis ignores any arguments it hasn't been told
to provide (positional arguments start from the right), so the self argument to the
test is simply ignored and works as normal. This also means that Hypothesis will play
nicely with other ways of parametrizing tests.

-------------
Writing tests
-------------

A test in Hypothesis consists of two parts: A function that looks like a normal
test in your test framework of choice but with some additional arguments, and
a @given decorator that specifies how to provide those arguments.

Here are some other examples of how you could use that:


.. code:: python

    from hypothesis import given

    @given(int, int)
    def test_ints_are_commutative(x, y):
        assert x + y == y + x

    @given(x=int, y=int)
    def test_ints_cancel(x, y):
        assert (x + y) - y == x

    @given([int])
    def test_reversing_twice_gives_same_list(xs):
        assert xs == list(reversed(reversed(xs)))

    @given((int, int))
    def test_look_tuples_work_too(t):
        assert len(t) == 2
        assert isinstance(t[0], int)
        assert isinstance(t[1], int)

Note that you can pass arguments to @given either as positional or as keywords.

The arguments to @given are intended to be "things that describe data". There are more
details in :doc:`the advanced section <details>` but the following should be enough to get
you started:

1. For "primitive" types like int, float, bool, str, unicode, bytes, etc. the type is enough to generate data of that type
2. A tuple of things you can generate generates a tuple of that length, with each element coming from the corresponding one in the description (so e.g. (int, bool) will give you a tuple of length two with the first element being an int and the second a bool)
3. A list of descriptions generates lists of arbitrary length whose elements match one of those descriptions

--------------
Where to start
--------------

You should now know enough of the basics to write some tests for your code using Hypothesis.
The best way to learn is by doing, so go have a try.

If you're stuck for ideas for how to use this sort of test for your code, here are some good
starting points:

1. Try just calling functions with appropriate random data and see if they crash. You may be surprised how often this works. e.g. note that the first bug we found in the encoding example didn't even get as far as our assertion: It crashed because it couldn't handle the data we gave it, not because it did the wrong thing.
2. Look for duplication in your tests. Are there any cases where you're testing the same thing with multiple different examples? Can you generalise that to a single test using Hypothesis?
3. `This piece is designed for an F# implementation <http://fsharpforfunandprofit.com/posts/property-based-testing-2/>`_, but is still very good advice which you may find helps give you good ideas for using Hypothesis.

If you have any trouble getting started, don't feel shy about :doc:`asking for help <community>`.
