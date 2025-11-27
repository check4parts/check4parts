Development Notes
=================

Local Environment
-----------------

The backend targets Python 3.11. Install dependencies and run the service with:

.. code-block:: bash

   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload

Environment Variables
---------------------

Supplier adapters require credentials during startup or when handling requests.
Populate the following variables in your ``.env`` file:

``BM_PARTS_TOKEN``
    Static token string used to authenticate against the BM Parts API. Used as
    the default credential for clients that do not provide their own token.

``ASG_TOKEN``
    Default ASG bearer token. Requests can override this by supplying
    ``login``/``password`` or a different ``token`` via ``supplier_options``.

``OMEGA_KEY``
    API key for Omega. Stored as the default ``key`` in unified calls.

``UNIQTRADE_EMAIL`` / ``UNIQTRADE_PASSWORD`` / ``UNIQTRADE_FINGERPRINT``
    Required credential trio for UniqTrade requests. Stored as defaults and can
    be overridden per client.

``INTERCARS_CLIENT_ID`` / ``INTERCARS_CLIENT_SECRET``
    OAuth client credentials for the InterCars integration.


Running Tests
-------------

The repository contains a ``pytest`` suite under ``backend/tests``. Execute the
tests with:

.. code-block:: bash

   cd backend
   pytest


Building Documentation
----------------------

Build the documentation locally after installing ``sphinx`` and
``sphinx-autobuild`` (optional) via ``pip``:

.. code-block:: bash

   pip install sphinx
   sphinx-build -b html docs docs/_build/html

The generated HTML is available in ``docs/_build/html/index.html``.

