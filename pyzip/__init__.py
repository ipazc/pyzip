#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

__author__ = 'Iván de Paz Centeno'


class PyZip(object):
    """
    In memory zipper dictionary
    """

    def __init__(self, initial_dict=None, compress=True):
        self.data = b""
        self.compression = {True: ZIP_DEFLATED, False: ZIP_STORED}[compress]
        self.stored_length = 0

        if initial_dict is not None:

            if type(initial_dict) is PyZip:
                self.data = initial_dict.to_bytes()
            elif type(initial_dict) is dict:
                for k, v in initial_dict.items():
                    self[k] = v
            else:
                raise Exception("Unknown dict type.")

            self.stored_length = len(self.keys())

    def __setitem__(self, key, value):
        if type(value) is int:
            value = str(value)

        try:
            del self[key]
        except Exception as ex:
            pass

        with BytesIO(self.data) as b:
            with ZipFile(b, mode="a", compression=self.compression) as z:
                z.writestr(str(key), value)

            b.seek(0)
            self.data = b.read()

        self.stored_length += 1

    def __contains__(self, item):
        return str(item) in self.keys()

    def __getitem__(self, item):
        key = str(item)

        if self.data is None:
            raise KeyError("{} not found.".format(key))

        found = True
        try:
            with BytesIO(self.data) as b, ZipFile(b) as z:
                result = z.read(key)

        except Exception as ex:
            found = False
            result = None

        if not found:
            raise KeyError("{} not found.".format(key))

        return result

    def __delitem__(self, key):
        if key not in self.keys():
            raise KeyError("{} not found.".format(key))

        copy = {k:v for k, v in self.items() if k != key}

        self.data = b""

        for k, v in copy.items():
            self[k] = v

    def __iter__(self):
        with BytesIO(self.data) as b, ZipFile(b) as z:
            for x in z.namelist():
                yield x

    def __len__(self):
        return self.stored_length

    def keys(self):
        with BytesIO(self.data) as b, ZipFile(b) as z:
            names = z.namelist()
        return names

    def __str__(self):
        return str(self.keys())

    def items(self):
        for x in self:
            yield x, self[x]

    def to_bytes(self):
        return self.data

    @classmethod
    def from_bytes(cls, bytes, compress=True):
        pyzip = cls()
        pyzip.data = bytes
        pyzip.stored_length = len(pyzip.keys())
        return pyzip

    def save(self, filename):
        if self.data is None:
            raise Exception("Dict is empty, can't be saved to file.")

        with open(filename, "wb") as f:
            f.write(self.data)

    @classmethod
    def from_file(cls, filename, compress=True):
        pyzip = cls()
        with open(filename, "rb") as f:
            pyzip.data = f.read()
        pyzip.stored_length = len(pyzip.keys())
        return pyzip

    def size(self):
        return len(self.data)
