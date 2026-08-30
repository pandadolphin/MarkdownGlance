# Third-party notices

## markdown2 2.3.9

Vendored from [python-markdown2](https://github.com/trentm/python-markdown2)
with three local changes: the command-line mainline is removed — a Sublime Text
package never runs it, and it pulled in `optparse`, a `Markdown.pl` comparison
through `subprocess.Popen` and a `sys.path` insert — two regex literals are
raw strings so that recent Python versions do not warn about invalid escape
sequences, and `SECRET_SALT` is three random bytes rather than
`bytes(randint(0, 1000000))`, which is a zero-filled buffer of random *length*
prepended to every `_hash_text` call. The library API is untouched.

Copyright (c) 2012 Trent Mick.
Copyright (c) 2007-2008 ActiveState Corp.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
