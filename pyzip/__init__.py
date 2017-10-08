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

    def __init__(self, initial_dict=None, compress=True, reuse_dict=True):
        self.compression = {True: ZIP_DEFLATED, False: ZIP_STORED}[compress]

        if initial_dict is None:
            initial_dict = {}

        if reuse_dict:
            self.zip_content = initial_dict
        else:
            self.zip_content = dict(initial_dict)

        self.cached_content = b""
        self.modified = len(self.zip_content) > 0

    @staticmethod
    def __flatten_dict(dictionary):
        keys = []
        values = []

        for k, v in dictionary.items():

            flat_root = k

            if isinstance(v, dict):
                flattened_keys, flattened_values = PyZip.__flatten_dict(v)

                keys += ["{}/{}".format(flat_root, flat) for flat in flattened_keys]
                values += flattened_values
            else:
                keys += ["{}".format(k)]
                values += [v]

        return keys, values

    @staticmethod
    def _flatten_dict(dictionary):
        keys, values = PyZip.__flatten_dict(dictionary)
        return {k: v for k, v in zip(keys, values)}

    @staticmethod
    def _inflate_dict(dictionary):
        result_dict = {}

        for k, v in dictionary.items():
            if "/" in k:
                keys = k.split("/")

                it_dict = result_dict
                for key in keys[:-1]:
                    if key not in it_dict:
                        it_dict[key] = {}
                    it_dict = it_dict[key]

                it_dict[keys[-1]] = v

            else:
                result_dict[k] = v

        return result_dict

    def __cache_content(self, store_hashes):
        hashes = {}

        with BytesIO() as b:
            with ZipFile(b, mode="a", compression=self.compression) as z:
                flattened_content = self._flatten_dict(self.zip_content)

                for key, content in flattened_content.items():

                    if store_hashes:
                        value_hash = hashlib.sha256(content).hexdigest()
                        hashes[str(key)] = value_hash.encode()

                    z.writestr(str(key), content)

                if store_hashes:
                    hashes_bytes = PyZip(hashes).to_bytes(store_hashes=False)
                    z.writestr('__SHA256__HASHES__.zip', hashes_bytes)

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
        self.modified = True

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

    def size(self, store_hashes=True):
        """
        Retrieves the size in bytes of this ZIP content.
        :return: Size of the zip content in bytes
        """
        if self.modified:
            self.__cache_content(store_hashes)

        return len(self.cached_content)

    def from_bytes(self, bytes, inflate=True):

        zip_content = self.zip_content
        zip_content.clear()

        hashes = None
        invalid_hashes = []

        with BytesIO(bytes) as b, ZipFile(b) as z:

            if "__SHA256__HASHES__.zip" in z.namelist():
                hashes = PyZip().from_bytes(z.read("__SHA256__HASHES__.zip"), inflate=False)

            for key in z.namelist():
                if key == "__SHA256__HASHES__.zip":
                    continue

                if key[-1] == "/":
                    continue

                content = z.read(key)

                # Let's check content hash
                if hashes is not None:
                    hash_value = hashlib.sha256(content).hexdigest().encode()
                    if hash_value != hashes[key]:
                        invalid_hashes.append(key)
                        continue

                zip_content[key] = content

        if len(invalid_hashes) > 0:
            raise InvalidKeysHashes(invalid_hashes)

        if inflate:
            self.zip_content = self._inflate_dict(zip_content)

        self.cached_content = bytes
        self.modified = False

        return self

    def to_bytes(self, store_hashes=True):
        if self.modified:
            self.__cache_content(store_hashes)
        return self.cached_content

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(self.to_bytes())

    def from_file(self, filename, compress=True, inflate=True):
        with open(filename, "rb") as f:
            content = f.read()

        return self.from_bytes(content, inflate=inflate)
