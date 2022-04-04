.. Neuromake documentation master file, created by
   sphinx-quickstart on Fri Mar 25 13:44:23 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Neuromake
=====================================

Neuromake aims to help users easily create custom BIDS Apps using `snakemake <https://snakemake.readthedocs.io/en/stable/>`. 

While snakemake typically expects wildcard variables to be defined statically, we instead define format strings containining all relevant wildcards. This means that, regardless which optional bids keywords are used within your BIDS dataset, a neuromake snakefile will do what you need it to.


.. toctree::
   :maxdepth: 2

   usage/installation
   usage/quickstart
   


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
