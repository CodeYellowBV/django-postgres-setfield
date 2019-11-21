django-postgres-setfield
========================

.. image:: https://travis-ci.org/CodeYellowBV/django-postgres-setfield.svg?branch=master
   :target: https://travis-ci.org/CodeYellowBV/django-postgres-setfield

A Django field for storing `standard Python set <https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset>`_
objects.  It uses Postgres arrays as a backing store.

Usage
-----

Using the field is straightforward, and similar to how you'd use a
`Django ArrayField <https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/>`_.
You can add the field to your model like so:

.. code:: python

    from django.db import models
    from setfield import SetField

    class Person(models.Model):
      LANGUAGES = (('NL', 'Dutch'), ('EN', 'English'), ('RU', 'Russian'))
      speaks_languages=SetField(models.TextField(choices=LANGUAGES), default=list, blank=True)

Then later, you can use it:

.. code:: python

    piet = Person(languages={'NL'})
    piet.save()

    john = Person(languages={'RU', 'EN'})
    john.save()


Lookups
-------

All the standard `Django ArrayField`_ lookups are supported.


Caveats
-------

* Unlike ArrayFields, SetFields cannot be nested (because sets cannot
  be nested in Python).
* When upgrading an existing ArrayField to a SetField, make sure the
  entries are sorted using the default sort order of Python for the
  corresponding object type, if you want to use the ``__exact``
  lookup.  Otherwise you'll get inconsistent results.
