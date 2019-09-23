Visual differ for Metanorma flavor HTML deliverables
====================================================

The tool will use headless Chrome to screenshot given pages
and compare resulting PNG images for differences.

Setup
-----

* `chromedriver` binary in $PATH
* Corresponding Chrome version
* Python 2 environment with libraries::

      virtualenv diff-env
      source diff-env/bin/activate 
      pip install requirements.txt

Usage
-----

    python html_diff.py <path/to/old/file> <path/to/new/file> <out_dir>

...then open `<OUT_DIR>/<html_document_filenamename>.html`
to see the visual diff.

Switch between old, new and diff layers, and adjust opacity.
