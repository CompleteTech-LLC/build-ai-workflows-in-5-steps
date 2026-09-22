# Synthetic source intake

Input: a new, explicitly supplied local UTF-8 text file. No real customer files are
included. Count whitespace-separated tokens without language-dependent parsing.
A missing file or invalid UTF-8 fails rather than being silently substituted.
The target reference is echoed, not read. Source access needs operator approval.
