#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#MIT License
#
#Copyright (c) 2017 Iván de Paz Centeno
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import hashlib
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

__author__ = 'Iván de Paz Centeno'


class InvalidKeysHashes(Exception):
    def __init__(self, keys, message=""):
        self.keys = keys

        if message == "":
            message = "Invalid hashes for keys: {}".format(keys)

        Exception.__init__(self, message)

    def get_keys(self):
        return self.keys


class PyZip(object):
    """
    In memory zipper dictionary
    """

    def __init__(self, initial_dict=None, compress=True):
        self.compression = {True: ZIP_DEFLATED, False: ZIP_STORED}[compress]

        if initial_dict is None:
            initial_dict = {}

        self.zip_content = dict(initial_dict)
        self.cached_content = b""
        self.modified = len(self.zip_content) > 0

    def __cache_content(self, store_hashes):
        hashes = {}

        with BytesIO() as b:
            with ZipFile(b, mode="a", compression=self.compression) as z:
                for key, v in self.items():
                    if type(v) is dict:
                        k = "[-__PYZIP__-]{}".format(key)
                        content = PyZip(v).to_bytes()
                    else:
                        k = key
                        content = v

                    if store_hashes:
                        value_hash = hashlib.sha256(content).hexdigest()
                        hashes[str(key)] = value_hash.encode()

                    z.writestr(str(k), content)

                if store_hashes:
                    hashes_bytes = PyZip(hashes).to_bytes(store_hashes=False)
                    z.writestr('[-__PYZIP__HASHES__-]', hashes_bytes)

            b.seek(0)
            self.cached_content = b.read()
            self.modified = False

    def __len__(self):
        return len(self.zip_content)

    def __getitem__(self, item):
        return self.zip_content[str(item)]

    def __setitem__(self, key, value):
        self.zip_content[str(key)] = value
        self.modified = True

    def __delitem__(self, key):
        del self.zip_content[key]

    def __str__(self):
        return str(self.keys())

    def __repr__(self):
        return "<< PyZip: {} >>".format(str(self))

    def __contains__(self, item):
        return str(item) in self.keys()

    def keys(self):
        return list(self.zip_content.keys())

    def values(self):
        return list(self.zip_content.values())

    def __iter__(self):
        for x in self.zip_content:
            yield x

    def items(self):
        for k, v in self.zip_content.items():
            yield k, v

    def size(self):
        """
        Retrieves the size in bytes of this ZIP content.
        :return: Size of the zip content in bytes
        """
        if self.modified:
            self.__cache_content()

        return len(self.cached_content)

    @classmethod
    def from_bytes(cls, bytes, compress=True):

        zip_content = {}
        hashes = None
        hash_value = None
        invalid_hashes = []

        with BytesIO(bytes) as b, ZipFile(b) as z:

            if "[-__PYZIP__HASHES__-]" in z.namelist():
                hashes = PyZip.from_bytes(z.read("[-__PYZIP__HASHES__-]"))

            for key in z.namelist():
                if key == "[-__PYZIP__HASHES__-]":
                    continue

                if key.startswith("[-__PYZIP__-]"):
                    k = key.strip("[-__PYZIP__-]")
                    content = z.read(key)
                    if hashes is not None:
                        hash_value = hashlib.sha256(content).hexdigest()

                    v = PyZip.from_bytes(content)
                else:
                    k = key
                    v = z.read(key)

                    if hashes is not None:
                        hash_value = hashlib.sha256(v).hexdigest()

                if hashes is not None:
                    v_hash = hashes[k]
                    if v_hash != hash_value.encode():
                        invalid_hashes.append(k)

                zip_content[k] = v

        if len(invalid_hashes) > 0:
            raise InvalidKeysHashes(invalid_hashes)

        pyzip = cls(zip_content)
        pyzip.cached_content = bytes
        pyzip.modified = False
        return pyzip

    def to_bytes(self, store_hashes=True):
        if self.modified:
            self.__cache_content(store_hashes)
        return self.cached_content

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(self.to_bytes())

    @classmethod
    def from_file(cls, filename, compress=True):
        with open(filename, "rb") as f:
            content = f.read()

        return PyZip.from_bytes(content)
