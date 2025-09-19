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

The adapters expect the following environment variables to be populated before
startup:

``BM_PARTS_TOKEN``
    Static token string used to authenticate against the BM Parts API.

``INTERCARS_CLIENT_ID`` / ``INTERCARS_CLIENT_SECRET``
    OAuth client credentials for the InterCars integration.

``ASG_TOKEN``
    Default ASG API token used for bootstrap flows.

``OMEGA_API_URL`` and ``OMEGA_API_KEY``
    Base URL and API key for Omega requests.

``UNIQTRADE_API_KEY``
    Credential required by the UniqTrade client.


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

