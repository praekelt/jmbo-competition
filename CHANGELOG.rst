Changelog
=========

next
----
#. Add missing object footer to detail page.

0.1.7
-----
#. Cache templates.

0.1.6
-----
#. Apply changelist filters to competition entry export.

0.1.5
-----
#. Speed up competition entry export.

0.1.4
-----
#. Handle case where competition is edited after entries have been received.
#. Export now handles unicode correctly.

0.1.3
-----
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

