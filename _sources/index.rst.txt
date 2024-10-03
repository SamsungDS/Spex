.. _sec-welcome:

Welcome to NVMe-Spex's documentation!
=====================================

.. toctree::
   :maxdepth: 1
   :hidden:

   what_is_spex.rst
   setup/index.rst
   user_guide/stages.rst
   user_guide/using_spex.rst
   user_guide/dev.rst


Welcome to the documentation for **Spex**, a tool for extracting information
on data-structures in the NVMe specification documents.

To read more about what **Spex** does, see :ref:`sec-what-is-spex`.
For help on setting up **Spex** on your system, see :ref:`sec-setup`.


For direct usage of nvme-spex it is possible to run it from docker. For setup of
docker on windows we refer to guides from `Docker Desktop
<https://docs.docker.com/desktop/install/windows-install/>`_.

.. code-block:: shell

      docker run --rm -v ~/Documents/specs/:/specs ghcr.io/samsungds/nvme-spex-webserver:latest run -s --output=/specs/output /specs/nvme_base.docx 

The output of the run will be available at ~/Documents/specs/output in this example.

It is also possible to lint the docx specification by using the web application.
To start the web application can be started with the following command:

.. code-block:: shell

       docker pull ghcr.io/samsungds/nvme-spex-webserver:latest
       docker run --rm -p 8000:8000 ghcr.io/samsungds/nvme-spex-webserver:latest webserver

When the docker container is successfully running the web application can be
accessed in the browser at `http://localhost:8000 <http://localhost:8000>`_.


The web application will show the following user interface:

.. image:: images/web_ss_1.png
  :width: 100%
  :alt: Alternative text

Upload the specification .docx or .html file and press the submit button.

.. image:: images/web_ss_2.png
  :width: 100%
  :alt: Alternative text

After processing is done the web-application will show
the following report:

.. image:: images/web_ss_3.png
  :width: 100%
  :alt: Alternative text
