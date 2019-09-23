Visual HTML differ
==================

The tool will use headless Chrome to screenshot given pages
and compare resulting PNG images for differences.

Setup
-----

* Obtain the ``chromedriver`` [1]_ binary and make sure it’s in your $PATH.

* Install matching Chrome version.

  (If not sure, let the tool run and it’ll fail with a ``chromedriver`` error
  instructing you which version you need.)

* Obtain this tool::

      git clone <this-repo> visual-diff
      cd visual-diff

* Create a Python 2 environment with libraries needed::

      virtualenv diff-env
      source diff-env/bin/activate 
      pip install requirements.txt

.. [1] https://chromedriver.chromium.org

Usage
-----

1. With Python environment activated, run::

       python html_diff.py <path/to/old/html/document> <path/to/new/html/document> <out_dir>

2. Open ``<out_dir>/<html_document_filename>.html``
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

* Simplify running on CI pipelines for Metanorma flavor repos
