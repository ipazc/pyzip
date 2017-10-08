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

from io import BytesIO
from random import random
import unittest
from zipfile import ZipFile
from pyzip import PyZip, InvalidKeysHashes


__author__ = 'Iván de Paz Centeno'


class TestPyZip(unittest.TestCase):
    """
    Unitary tests for the PyZip class.
    """
    def setUp(self):
        self.vocabulary = "abcdefghijklmnñopqrstuvwxyz1234567890"

    def test_zip_content(self):
        """
        PyZip can compress or pack the content on the fly.
        """
        pyzip = PyZip()

        # 1. We generate a big file (~ 10 KB)
        file_content = b""
        for x in range(10000):
            file_content += self.vocabulary[int(random()*len(self.vocabulary))].encode()

        pyzip["key1"] = file_content

        # In a compressed pyzip it should consume less memory.
        self.assertLess(len(pyzip.to_bytes()), len(file_content))

        pyzip = PyZip(compress=False)

        pyzip["key1"] = file_content

        # However, in an uncompressed pyzip it should consume more memory because of the zip headers.
        self.assertGreater(len(pyzip.to_bytes()), len(file_content))

    def test_unzip_content(self):
        """
        PyZip can uncompress or unpack the content on the fly.
        """
        pyzip = PyZip()

        # 1. We generate a big file (~ 10 KB)
        file_content = b""
        for x in range(10000):
            file_content += self.vocabulary[int(random()*len(self.vocabulary))].encode()

        pyzip["key1"] = file_content

        self.assertEqual(pyzip["key1"], file_content)

        pyzip = PyZip(compress=False)

        pyzip["key1"] = file_content

        self.assertEqual(pyzip["key1"], file_content)

    def test_save_load_to_file(self):
        """
        PyZip can save to a and load from a zip file.
        """
        pyzip = PyZip()

        # 1. We generate a big file (~ 10 KB)
        file_content = b""
        for x in range(10000):
            file_content += self.vocabulary[int(random()*len(self.vocabulary))].encode()

        pyzip["key1"] = file_content

        pyzip.save("test.zip")
        with open("test.zip", "rb") as f: bytes = f.read()

        self.assertEqual(pyzip.to_bytes(), bytes)

        pyzip2 = PyZip().from_file("test.zip")
        self.assertEqual(pyzip.to_bytes(), pyzip2.to_bytes())
        self.assertEqual(pyzip2["key1"], file_content)

    def test_pyzip_iteration(self):
        """
        PyZip can be iterated.
        """
        pyzip = PyZip()
        pyzip["1"] = b"hola"
        pyzip["2"] = b"hola2"
        pyzip["3"] = b"hola3"
        pyzip["4"] = b"hola4"

        for key, content in pyzip.items():
            self.assertEqual(pyzip[key], content)

    def test_pyzip_keys(self):
        """
        PyZip keys are retrieved successfully.
        """
        pyzip = PyZip()
        pyzip["1"] = b"hola"
        pyzip["2"] = b"hola2"
        pyzip["3"] = b"hola3"
        pyzip["4"] = b"hola4"

        self.assertTrue(all([x in pyzip.keys() for x in ["1", "2", "3", "4"]]))

    def test_pyzip_keys_to_str(self):
        """
        PyZip int keys are converted to strings.
        """
        pyzip = PyZip()
        pyzip[1] = b"hola"
        pyzip[2] = b"hola2"
        pyzip[3] = b"hola3"
        pyzip[4] = b"hola4"

        self.assertTrue(all([x in pyzip.keys() for x in ["1", "2", "3", "4"]]))

    def test_pyzip_from_dict(self):
        """
        PyZip can be created from a dict.
        """
        dictionary = {
            "1": b"hola",
            "2": b"hola2",
            "3": b"hola3",
            "4": b"hola4"
        }

        pyzip = PyZip(dictionary)

        for k, v in pyzip.items():
            self.assertEqual(dictionary[k], v)

    def test_pyzip_from_itself(self):
        """
        PyZip can be created from itself.
        """
        pyzip = PyZip()
        pyzip[1] = b"hola"
        pyzip[2] = b"hola2"
        pyzip[3] = b"hola3"
        pyzip[4] = b"hola4"

        pyzip2 = PyZip(pyzip)

        for k, v in pyzip.items():
            self.assertEqual(pyzip2[k], v)

    def test_pyzip_contains(self):
        """
        PyZip can be questioned for containing elemnets.
        """
        pyzip = PyZip()
        pyzip[1] = b"hola"
        pyzip[2] = b"hola2"
        pyzip[3] = b"hola3"
        pyzip[4] = b"hola4"

        self.assertIn("1", pyzip)
        self.assertNotIn("0", pyzip)

    def test_pyzip_str(self):
        """
        PyZip is converted to str successfully.
        """
        pyzip = PyZip()
        pyzip[1] = b"hola"
        pyzip[2] = b"hola2"
        pyzip[3] = b"hola3"
        pyzip[4] = b"hola4"

        self.assertTrue(all([x in str(pyzip) for x in pyzip.keys()]))

    def test_pyzip_wrong_key_exception(self):
        """
        PyZip should not accept wrong keys by raising KeyError exceptions
        :return:
        """
        pyzip = PyZip()
        with self.assertRaises(KeyError) as ex:
            v = pyzip["ass"]

    def test_pyzip_delete_key(self):
        """
        PyZip accepts a delete of a key.
        :return:
        """
        pyzip = PyZip()
        pyzip["a"] = b"a1"
        pyzip["b"] = b"a2"
        pyzip["c"] = b"a3"

        del pyzip["b"]

        with self.assertRaises(KeyError) as ex:
            v = pyzip["b"]

        self.assertIn("a", pyzip)
        self.assertIn("c", pyzip)
        self.assertEqual(pyzip["a"], b"a1")
        self.assertEqual(pyzip["c"], b"a3")

    def test_pyzip_edit_key(self):
        """
        PyZip accepts an edition of a key.
        :return:
        """
        pyzip = PyZip()
        pyzip["a"] = b"a1"
        pyzip["b"] = b"a2"
        pyzip["c"] = b"a3"

        self.assertEqual(pyzip["b"], b"a2")
        self.assertEqual(pyzip["a"], b"a1")
        self.assertEqual(pyzip["c"], b"a3")

        pyzip["b"] = b"a4"

        self.assertEqual(pyzip["b"], b"a4")
        self.assertEqual(pyzip["a"], b"a1")
        self.assertEqual(pyzip["c"], b"a3")

    def test_pyzip_to_dict(self):
        """
        PyZip can be converted to a dict.
        :return:
        """
        pyzip = PyZip()
        pyzip["a"] = b"a1"
        pyzip["b"] = b"a2"
        pyzip["c"] = b"a3"

        d = dict(pyzip)

        self.assertEqual(d["b"], b"a2")
        self.assertEqual(d["a"], b"a1")
        self.assertEqual(d["c"], b"a3")

    def test_pyzip_deep_dicts(self):
        """
        PyZip can compress dicts containing dicts.
        :return:
        """
        pyzip = PyZip()
        pyzip["a"] = b"a1"
        pyzip["b"] = b"a2"
        pyzip["c"] = {"c1": b"c1"}

        compression = pyzip.to_bytes()
        new_pyzip = PyZip().from_bytes(compression)
        self.assertTrue(all([x in new_pyzip for x in "abc"]))
        self.assertEqual(new_pyzip["c"]["c1"], b"c1")

    def test_pyzip_integrity(self):
        """
        PyZip stores hashes of elements and checks for integrity.
        :return:
        """
        pyzip = PyZip()
        pyzip["a"] = b"a1"
        pyzip["b"] = b"a2"
        pyzip["c"] = {"c1": b"c1"}

        compression = pyzip.to_bytes()

        storage = {}
        with BytesIO(compression) as b, ZipFile(b) as z:
            storage = {x: z.read(x) for x in z.namelist()}

        storage["a"] = b"ba0"  # small modification to trigger the integrity check

        with BytesIO() as b:
            with ZipFile(b, mode="a") as z:
                for key, v in storage.items():
                    z.writestr(key, v)
            b.seek(0)
            content = b.read()

        with self.assertRaises(InvalidKeysHashes) as ex:
            new_pyzip = PyZip().from_bytes(content)


if __name__ == '__main__':
    unittest.main()