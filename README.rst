==============
pyzip 0.0.1
==============
PyZip is a package for handling zip-in-memory content as a dictionary. 

.. code:: python

    >>> from pyzip import PyZip
    >>> 
    >>> pyzip = PyZip()
    >>> pyzip['key1'] = b"content_bytes"
    >>> pyzip['key2'] = file_bytes
    >>>
    >>> pyzip.to_file("/path/to/file.zip")
    >>> zip_bytes = pyzip.to_bytes() # Alternatively, to bytes

It is run on top of the module `zipfile`, however, in addition to its functionality, PyZip accepts to edit and remove
elements of a zip.

Installation
============
Currently it is only supported Python 3.4.1 onwards:

.. code:: bash
    
    sudo pip3 install pyzip

Basic Usage
===============
PyZip can easily store content into a zip on the fly. The usage is the same as a normal dictionary: 

* Add content to in-memory zip:

.. code:: python

    >>> from pyzip import PyZip
    >>> 
    >>> pyzip = PyZip()
    >>> pyzip['key1'] = b"content_bytes"


* Get specific content from in-memory zip:

.. code:: python

    >>> print(pyzip['key1'])
    b"content_bytes"
    

* Edit content of in-memory zip:

.. code:: python

    >>> pyzip['key1'] = b"replaced_content_bytes"


* Remove content of in-memory zip:

.. code:: python

    >>> del pyzip['key1']


* Get zip bytes:

.. code:: python

    >>> zip_bytes = pyzip.to_bytes()


* Load from bytes:

.. code:: python

    >>> pyzip = PyZip.from_bytes(zip_bytes)
    

* Save to zip file:

.. code:: python

    >>> pyzip.save("path/to/file.zip")
    

* Load from zip file:

.. code:: python

    >>> pyzip = PyZip.from_file("path/to/file.zip")
    
* Convert existing dictionary into PyZip:

.. code:: python

    >>> pyzip = PyZip({'file1': b'example', 'file2': b'example2'})
    
    
    
Use case
===============
Compressing a folder into a zip:


.. code:: python

    >>> from pyzip import PyZip
    >>> import os
    >>>
    >>> path_to_compress = "route/to/files"
    >>>
    >>> pyzip = PyZip()
    >>>
    >>> for file in os.listdir(path_to_compress):
    >>>     with open(path_to_compress, "rb") as f:
    >>>        pyzip[file] = f.read()
    >>>
    >>> pyzip.save("compressed_folder.zip")

Uncompressing a folder from a zip:

.. code:: python

    >>> from pyzip import PyZip
    >>> import os
    >>>
    >>> destination = "route/for/uncompress"
    >>>
    >>> pyzip = PyZip.from_file("compressed_folder.zip)
    >>>
    >>> for filename, content in pyzip.items():
    >>>     with open(os.path.join(destination, filename), "wb") as f:
    >>>        f.write(content)
    >>>
