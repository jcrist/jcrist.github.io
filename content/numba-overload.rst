Extending Numba with ``overload``
#################################

:date: 2020-04-06 10:00
:slug: numba-overload
:author: Jim Crist
:summary: A quick post on adding new functions to Numba

Numba_ is an amazing project. It's able to just-in-time (JIT) compile a fairly
large subset of numerical Python code to fast machine code, with the user only
having to apply a decorator_ to their function. It looks like this:

.. code-block:: python

    import random
    import numba as nb

    @nb.njit   # <- magic Numba decorator
    def monte_carlo_pi(nsamples):
        """Estimate the value of Pi using the monte-carlo method"""
        acc = 0
        for i in range(nsamples):
            x = random.random()
            y = random.random()
            if (x ** 2 + y ** 2) < 1.0:
                acc += 1
        return 4.0 * acc / nsamples

The above is an example routine for estimating Pi using the monte-carlo_
method. Without the ``nb.njit`` decorator ``monte_carlo_pi`` would successfully
run (everything is valid Python), but with the decorator itruns significantly
faster (roughly 30x in my quick benchmark).

Numba does this by analyzing the decorated function's bytecode_ to build an
`intermediate representation`_ (IR) of the its structure. Type inference is
then applied, followed by a series of IR transformations. Finally the IR is
used to generate LLVM IR, which is then compiled to machine code.  Part of this
transformation process involves swapping out calls to Python functions (like
``random.random`` above) with faster compiled versions that Numba knows about.

Numba natively supports a decent subset of Python and NumPy (see `here
<http://numba.pydata.org/numba-doc/latest/reference/pysupported.html>`__ and
`here
<http://numba.pydata.org/numba-doc/latest/reference/numpysupported.html>`__ for
a full reference). But sometimes you'll run into situations where Numba doesn't
know about the function you're referencing. In this case you'll get an error:

.. code-block:: python

    >>> import numpy as np
    >>> import numba as nb

    >>> @nb.njit
    ... def clipped_sum(x):
    ...     return np.clip(x, 0, 1).sum()

    >>> clipped_sum(np.arange(10))
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/opt/miniconda3/envs/numba/lib/python3.8/site-packages/numba/dispatcher.py", line 401, in _compile_for_args
        error_rewrite(e, 'typing')
    File "/opt/miniconda3/envs/numba/lib/python3.8/site-packages/numba/dispatcher.py", line 344, in error_rewrite
        reraise(type(e), e, None)
    File "/opt/miniconda3/envs/numba/lib/python3.8/site-packages/numba/six.py", line 668, in reraise
        raise value.with_traceback(tb)
    TypingError: Failed in nopython mode pipeline (step: nopython frontend)
    Use of unsupported NumPy function 'numpy.clip' or unsupported use of the function.

    File "<ipython-input-8-3524b5de079c>", line 3:
    def clipped_sum(x):
        return np.clip(x, 0, 1).sum()
        ^

    [1] During: typing of get attribute at <ipython-input-8-3524b5de079c> (3)

    File "<ipython-input-8-3524b5de079c>", line 3:
    def clipped_sum(x):
        return np.clip(x, 0, 1).sum()
        ^

Numba (at least version ``0.48.0``) doesn't know how to handle the ``np.clip``
call. We'll need to use Numba's `extension API
<http://numba.pydata.org/numba-doc/latest/extending/index.html>`__ to add
support for ``np.clip``.

Implementing new functions with ``overload``
--------------------------------------------

To add support for a new function to Numba, we can make use of the
`numba.extending.overload
<http://numba.pydata.org/numba-doc/latest/extending/overloading-guide.html>`__
decorator. The decorated function is called at compile time with the *types* of
the arguments, and should return an *implementation* for those given types.
This implementation will then be jit compiled and used in place of the
overloaded function.

Lets work a simplified example first, before handling ``np.clip``. Say we
wanted to add Numba support for the following function:

.. code-block:: python

    def myfunc(x):
        if isinstance(x, int):
            return x + 1
        elif isinstance(x, float):
            return x * 2
        else:
            raise TypeError("x must be an int or a float")

The above checks if ``x`` is an ``int``, and if so increments it. If it's a
``float`` it doubles it. Otherwise it raises a ``TypeError``.

These type checks happen at *runtime*. When writing our Numba implementation,
the types are known at *compile time*.  This means that we can elide the type
checks at runtime by handling the type-based dispatching (and erroring) at
compile time.

The corresponding Numba implementation for this function is:

.. code-block:: python

    from numba import types
    from numba.errors import TypingError
    from numba.extending import overload

    @overload(myfunc)
    def implement_myfunc(x):
        # This is a code generator for ``myfunc``.
        # Here x is the compile-time *type*

        if isinstance(x, types.Integer):
            def impl(x):
                # This is an *implementation* of ``myfunc`` (in this case the
                # implementation for integer values of x).
                # Here x is the runtime *value*
                return x + 1

        elif isinstance(x, types.Float):
            def impl(x):
                return x * 2

        else:
            # If an invalid type is passed to ``implement_myfunc``, a
            # ``numba.types.TypingError`` should be raised. This helps inform
            # the user what went wrong.
            raise TypingError("x must be an int or a float")

        return impl

At a high level ``implement_myfunc`` and ``myfunc`` look quite similar. Both
branch on the type of ``x``, with branches for integers, floats, and errors.
But while ``myfunc`` returns values, ``implement_myfunc`` returns a callable
that will be JIT compiled by numba and used to implement ``myfunc`` for the
provided type.

Note that Numba types are distinct from their Python counterparts (but there's
usually a one-to-one mapping between them). These types can be found in
``numba.types`` (`documentation
<http://numba.pydata.org/numba-doc/latest/reference/types.html>`__). If you
don't know what the corresponding Numba type is for something, you can use
``numba.typeof``.

.. code-block:: python

    >>> from numba import typeof
    >>> typeof(1)
    int64
    >>> typeof((1, 5.0))
    Tuple(int64, float64)

Also, instead of a ``TypeError``, when an invalid type (or combination of
types) is provided, the decorated function (e.g. ``implement_myfunc``) a should
raise a ``numba.errors.TypingError``. This will be reported back to the user.

Adding an overload for ``np.clip``
----------------------------------

Now lets apply the same process to ``np.clip``, reimplementing the function in
a way that Numba's JIT can reason about.  To make sure the NumPy and Numba
versions are compatible, we first check the `docstring
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.clip.html>`__:

.. code-block:: python

    """
    Clip (limit) the values in an array.

    Given an interval, values outside the interval are clipped to
    the interval edges.  For example, if an interval of ``[0, 1]``
    is specified, values smaller than 0 become 0, and values larger
    than 1 become 1.

    Equivalent to but faster than ``np.maximum(a_min, np.minimum(a, a_max))``.
    No check is performed to ensure ``a_min < a_max``.

    Parameters
    ----------
    a : array_like
        Array containing elements to clip.
    a_min : scalar or array_like or None
        Minimum value. If None, clipping is not performed on lower
        interval edge. Not more than one of `a_min` and `a_max` may be
        None.
    a_max : scalar or array_like or None
        Maximum value. If None, clipping is not performed on upper
        interval edge. Not more than one of `a_min` and `a_max` may be
        None. If `a_min` or `a_max` are array_like, then the three
        arrays will be broadcasted to match their shapes.
    ...
    """

We don't need to support all of ``np.clip``'s possible arguments yet, just the
ones we need. To simplify things, we'll support:

- Scalar values for ``a_min``/``a_max`` (``int``, ``float``, or ``None``).
- Either scalar or 1D-array values for ``a``.

After a bit of work, I ended up with the following implementation:

.. code-block:: python

    import numpy as np
    from numba import types
    from numba.errors import TypingError
    from numba.extending import overload

    @overload(np.clip)
    def impl_clip(a, a_min, a_max):
        # Check that `a_min` and `a_max` are scalars, and at most one of them is None.
        if not isinstance(a_min, (types.Integer, types.Float, types.NoneType)):
            raise TypingError("a_min must be a_min scalar int/float")
        if not isinstance(a_max, (types.Integer, types.Float, types.NoneType)):
            raise TypingError("a_max must be a_min scalar int/float")
        if isinstance(a_min, types.NoneType) and isinstance(a_max, types.NoneType):
            raise TypingError("a_min and a_max can't both be None")

        if isinstance(a, (types.Integer, types.Float)):
            # `a` is a scalar with a valid type
            if isinstance(a_min, types.NoneType):
                # `a_min` is None
                def impl(a, a_min, a_max):
                    return min(a, a_max)
            elif isinstance(a_max, types.NoneType):
                # `a_max` is None
                def impl(a, a_min, a_max):
                    return max(a, a_min)
            else:
                # neither `a_min` or `a_max` are None
                def impl(a, a_min, a_max):
                    return min(max(a, a_min), a_max)
        elif (
            isinstance(a, types.Array) and
            a.ndim == 1 and
            isinstance(a.dtype, (types.Integer, types.Float))
        ):
            # `a` is a 1D array of the proper type
            def impl(a, a_min, a_max):
                # Allocate an output array using standard numpy functions
                out = np.empty_like(a)
                # Iterate over `a`, calling `np.clip` on every element
                for i in range(a.size):
                    # This will dispatch to the proper scalar implementation (as
                    # defined above) at *compile time*. There should have no
                    # overhead at runtime.
                    out[i] = np.clip(a[i], a_min, a_max)
                return out
        else:
            raise TypingError("`a` must be an int/float or a 1D array of ints/floats")

        # The call to `np.clip` has arguments with valid types, return our
        # numba-compatible implementation
        return impl

With our implementation registered, we should now be able to use ``np.clip``
with Numba. Verifying:

.. code-block:: python

    >>> import numpy as np
    >>> import numba as nb

    >>> @nb.njit
    ... def test_clip(x, a_min, a_max):
    ...     return np.clip(x, a_min, a_max)

    >>> x = np.arange(10)

    >>> test_clip(x, 2, 5)
    array([2, 2, 2, 3, 4, 5, 5, 5, 5, 5])

    >>> test_clip(x, None, 5)
    array([0, 1, 2, 3, 4, 5, 5, 5, 5, 5])

    >>> test_clip(5.0, 0, 3)
    3.0


Registering Numba Extensions with Entry Points
----------------------------------------------

Our above example using ``np.clip`` worked because our overloaded definition
was already registered with Numba. As long as our ``overload`` decorated
functions have been loadAs long as our ``overload`` decorated functions have
been loaded before Numba tries to compile something that relies on them,
everything should *just work*. However, sometimes you may need (or want) to
store the overloaded definitions in a package that would not normally be
imported by users. For example, the `numba-scipy
<https://github.com/numba/numba-scipy>`__ package adds Numba support for the
SciPy library, but is a separate package from ``scipy``.

To avoid forcing users to ``import numba_scipy`` to enable the extension, Numba
relies on `entry points
<https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins>`__
to automatically discover any installed extensions.

To register a module as a Numba extension, you need to:

- Define an ``init`` function to setup your extension (in our case this is just
  importing any modules with ``overload`` definitions):

  .. code-block:: python

    # numba_overload_example/__init__.py
    def init():
        # Import the overloads module, registering any functions or types
        from . import overloads

- Register this ``init`` function as an entry point under the
  ``numba_extensions`` group.

  .. code-block:: python

    # setup.py
    setup(
        ...,
        entry_points={
            "numba_extensions": [
                "init = numba_overload_example:init",
            ]
        },
        ...
    )

For more information on registering Numba extensions using entry points, see
the `documentation
<http://numba.pydata.org/numba-doc/latest/extending/entrypoints.html>`__.

Wrapping Up
-----------

Unmodified, Numba is able to compile a decent subset of Python and NumPy. If
you're writing code that looks similar to how it'd be done in a "low-level"
language like C (e.g. loops, arithmetic, arrays of scalars, ...) you may never
need to use the extension API. But when needed, using ``overload`` to add
support for new functions can be quite useful.

The full code for our example extension module can be found here:
numba-overload-example_.


.. _Numba: https://numba.pydata.org
.. _decorator: https://docs.python.org/3/glossary.html#term-decorator
.. _monte-carlo: https://en.wikipedia.org/wiki/Monte_Carlo_method
.. _bytecode: https://docs.python.org/3/glossary.html#term-bytecode
.. _intermediate representation: http://numba.pydata.org/numba-doc/latest/glossary.html#term-numba-ir
.. _numba-overload-example: https://github.com/jcrist/numba-overload-example
