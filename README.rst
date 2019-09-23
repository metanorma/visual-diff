Visual differ for Metanorma flavor HTML deliverables
====================================================

The tool will use headless Chrome to screenshot given pages
and compare resulting PNG images for differences.

Setup
-----

* Obtain the ``chromedriver`` [1]_ binary and make sure it’s in your $PATH

* Install matching Chrome version
  (otherwise, the tool will fail with a ``chromedriver`` error telling you which version you need)

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

       python html_diff.py <path/to/old/html/file> <path/to/new/html/file> <out_dir>

2. Open ``<out_dir>/<html_document_filenamename>.html``
   in your favorite browser to see a visual diff.

3. Switch between old, new and diff layers, and adjust opacity as needed.
