# Pure python implementation of [Quite OK Image Format](https://qoiformat.org/)

Even though the [Python bindings for QOI](https://github.com/kodonnell/qoi) are WAY faster, I implemented the QOI in pure python 3.10 with switch-statements and optional PIL.Image compatibility (or byte-streams)

This module exposes the encode() and decode() methods that take byte-streams as iterables or iterators.

The tests use the images from the qoi_test_images folder.
