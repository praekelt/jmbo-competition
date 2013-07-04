Changelog
=========

next
----
#. Do not display canonical image if content contains an image.

0.1.2.1
-------
#. Fixes CSV export crash when an attribute is None. Uses empty string when value is None.

0.1.2
-----
#. Redirect back to competition after login.
#. CSV export of competition winners.

0.1.1
-----
#. Add an URL rule that yields prettier urls.

0.1
---
#. Add migrations. If you have an existing installation then you must do `./bin/django migrate competition 0001 --fake`.
#. Clean up templates.

0.0.5
-----
#. Better packaging.

