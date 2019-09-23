Visual differ for Metanorma flavor HTML deliverables
====================================================

The tool will use headless Chrome to screenshot given pages
and compare resulting PNG images for differences.

Setup
-----

* ``git clone <this-repo> visual-diff && cd visual-diff``
* Obtain ``chromedriver`` binary and make sure it’s in your $PATH
* Install corresponding Chrome version
* Create Python 2 environment with libraries needed::

      virtualenv diff-env
      source diff-env/bin/activate 
      pip install requirements.txt

Usage
-----

With Python environment activated, run::

    python html_diff.py <path/to/old/html/file> <path/to/new/html/file> <out_dir>

...then open ``<out_dir>/<html_document_filenamename>.html``
to see the visual diff.

Switch between old, new and diff layers, and adjust opacity as needed.
