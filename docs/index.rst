ipsw SDK for Python
===================

A Python library for the ipsw API. It lets you do anything the ``ipsw`` command does, but from within Python apps – download, parse, explore IPSWs, etc.

For more information about the API, `see its documentation <https://blacktop.github.io/ipsw/`_.

Installation
------------

The latest stable version `is available on PyPI <https://pypi.python.org/pypi/ipsw/>`_. Either add ``ipsw`` to your ``requirements.txt`` file or install with pip::

    pip install ipsw

Getting started
---------------

To talk to a ipsw daemon, you first need to instantiate a client. You can use :py:func:`~ipsw.client.from_env` to connect using the default socket or the configuration in your environment:

.. code-block:: python

  import ipsw
  client = ipsw.from_env()

You can now run containers:

.. code-block:: python

  >>> client.ipsw_info("iPhone15,2_16.4_20E246_Restore.ipsw")
  'INFO\n'


That's just a taste of what you can do with the ipsw SDK for Python. For more, :doc:`take a look at the reference <client>`.

.. toctree::
  :hidden:
  :maxdepth: 2

  client
  api
