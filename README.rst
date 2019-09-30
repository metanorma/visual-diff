Visual HTML differ
==================

Uses headless Chrome to screenshot given pages
and generates an HTML GUI for visual comparison.

Setup
-----

* Obtain the ``chromedriver`` binary [1]_ and make sure it’s in your $PATH.

* Install matching Chrome version.

  (If not sure, let the tool run and it’ll fail with a ``chromedriver`` error
  instructing you which version you need.)

* Obtain this tool::

      git clone git@github.com:metanorma/visual-diff.git visual-diff
      cd visual-diff

* Create a Python 2 virtual environment [2]_ with libraries needed::

      virtualenv diff-env
      source diff-env/bin/activate 
      pip install -r requirements.txt

.. [1] https://chromedriver.chromium.org
.. [2] https://virtualenv.pypa.io/en/latest/

Usage
-----

1. With Python environment activated, run::

       python html_diff.py <path/to/old/document.html> <path/to/new/document.html> <path/to/diff/results/dir>

2. Open ``<path/to/diff/results/dir>/<document-name>.html``
   in your favorite browser to see a visual diff.

3. Switch between old, new and diff layers, and adjust opacity as needed.


Why
---

Many Metanorma flavors offer deliverables formatted in compliance
with corresponding organizations’ requirements.

During development (especially larger refactors),
a visual diff helps avoid undesired accidental changes in styling
that might break compliance.


Roadmap
-------

* Simplify testing responsive layouts [1]_
* Simplify running on CI pipelines for Metanorma flavor repos

.. [1] https://github.com/metanorma/visual-diff/issues/1
