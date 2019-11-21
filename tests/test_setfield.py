from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import models

from setfield import SetField
from .testapp.models import SetTest

class SetFieldTest(TestCase):
    def setUp(self):
        SetTest.objects.all().delete()


    def assertStrictEqual(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(type(a), type(b))


    def test_basic_set_value_survives_db_roundtrip(self):
        input_text_value = {'RED', 'GREEN'}
        input_int_value = {1, 2, 3}
        obj = SetTest(text_value=input_text_value, int_value=input_int_value)
        obj.save()

        obj.refresh_from_db()
        self.assertStrictEqual(input_text_value, obj.text_value)
        self.assertStrictEqual(input_int_value, obj.int_value)


    def test_empty_set_survives_db_roundtrip(self):
        obj = SetTest(text_value=set(), int_value=set())
        obj.save()

        obj.refresh_from_db()
        self.assertStrictEqual(set(), obj.text_value)
        self.assertStrictEqual(set(), obj.int_value)


    def test_empty_list_as_default_survives_db_roundtrip_as_set(self):
        obj = SetTest()
        self.assertStrictEqual(set(), obj.int_value)
        obj.save()

        obj.refresh_from_db()
        self.assertIsNone(obj.text_value)
        self.assertStrictEqual(set(), obj.int_value)


    def test_basic_frozenset_value_survives_db_roundtrip_as_set(self):
        input_text_value = frozenset(['RED', 'GREEN'])
        input_int_value = frozenset([1, 2, 3])
        obj = SetTest(text_value=input_text_value, int_value=input_int_value)
        obj.save()

        obj.refresh_from_db()
        self.assertStrictEqual({'RED', 'GREEN'}, obj.text_value)
        self.assertStrictEqual({1, 2, 3}, obj.int_value)


    def test_empty_frozenset_survives_db_roundtrip_as_set(self):
        obj = SetTest(text_value=frozenset(), int_value=frozenset())
        obj.save()

        obj.refresh_from_db()
        self.assertStrictEqual(set(), obj.text_value)
        self.assertStrictEqual(set(), obj.int_value)


    def test_none_value_also_survives_db_roundtrip(self):
        obj = SetTest(text_value=None, int_value={1})
        obj.save()

        obj.refresh_from_db()
        self.assertIsNone(obj.text_value)


    def test_none_value_survives_full_clean(self):
        obj = SetTest(text_value=None, int_value={1})
        obj.full_clean()
        self.assertIsNone(obj.text_value)


    # Specific check, because to_python doesn't get called by save()
    # or full_clean() when the value is None (but other things might)
    def test_none_value_survives_to_python(self):
        self.assertIsNone(SetField(models.TextField()).to_python(None))
        self.assertIsNone(SetField(models.IntegerField()).to_python(None))


    def test_list_value_is_normalized_on_full_clean(self):
        input_text_value = ['RED', 'GREEN', 'RED']
        input_int_value = [1, 1, 2, 1, 3]
        obj = SetTest(text_value=input_text_value, int_value=input_int_value)
        obj.full_clean()

        self.assertNotEqual(input_text_value, obj.text_value)
        self.assertStrictEqual({'RED', 'GREEN'}, obj.text_value)
        self.assertStrictEqual({1, 2, 3}, obj.int_value)

        # Quick sanity check to ensure the input isn't mutated.
        self.assertStrictEqual(['RED', 'GREEN', 'RED'], input_text_value)
        self.assertStrictEqual([1, 1, 2, 1, 3], input_int_value)


    def test_empty_list_value_is_normalized_on_full_clean_if_blankable(self):
        obj = SetTest(text_value=[], int_value=[1])
        obj.full_clean()

        self.assertStrictEqual(set(), obj.text_value)
        self.assertStrictEqual({1}, obj.int_value)


    def test_empty_list_value_raises_blank_error_if_not_blankable(self):
        obj = SetTest(text_value=[], int_value=[])

        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()
        self.assertEqual(set(['int_value']), set(cm.exception.error_dict.keys()))
        self.assertEqual('blank', cm.exception.error_dict['int_value'][0].code)


    def test_empty_set_value_raises_blank_error_if_not_blankable(self):
        obj = SetTest(text_value=[], int_value=set())

        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()
        self.assertEqual(set(['int_value']), set(cm.exception.error_dict.keys()))
        self.assertEqual('blank', cm.exception.error_dict['int_value'][0].code)


    def test_string_input_from_json(self):
        obj = SetTest(text_value='["GREEN", "RED"]', int_value='[1, 2, 3]')
        obj.full_clean()

        self.assertStrictEqual(obj.text_value, {'RED', 'GREEN'})
        self.assertStrictEqual(obj.int_value, {1, 2, 3})


    def test_invalid_objects_raise_validation_errors(self):
        obj = SetTest(int_value={1})

        obj.text_value = True
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()
        self.assertEqual(set(['text_value']), set(cm.exception.error_dict.keys()))
        self.assertEqual('not_iterable', cm.exception.error_dict['text_value'][0].code)

        obj.text_value = 1
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()
        self.assertEqual(set(['text_value']), set(cm.exception.error_dict.keys()))
        self.assertEqual('not_iterable', cm.exception.error_dict['text_value'][0].code)

        obj.text_value = {'RED'}
        obj.full_clean()


    def test_filtering_works(self):
        obj1 = SetTest(text_value={'RED', 'GREEN'}, int_value=set())
        obj1.save()

        obj2 = SetTest(text_value={'BLUE'}, int_value=set())
        obj2.save()

        q = SetTest.objects.filter(text_value__contains={'RED'})
        self.assertEqual(1, q.count())
        self.assertEqual(obj1, q.get())

        q = SetTest.objects.filter(text_value__contains={'RED', 'GREEN', 'BLUE'})
        self.assertEqual(0, q.count())

        q = SetTest.objects.filter(text_value__contained_by={'RED', 'GREEN', 'BLUE'})
        self.assertEqual(2, q.count())

        # Strangely enough, this filter was the only one to raise an
        # error of "can't adapt type", while the ones above worked.
        q = SetTest.objects.filter(text_value__overlap={'RED'})
        self.assertEqual(1, q.count())
        self.assertEqual(obj1, q.get())

        q = SetTest.objects.filter(text_value={'RED'})
        self.assertEqual(0, q.count())

        # NOTE: This is dependent on sort order!
        q = SetTest.objects.filter(text_value={'RED', 'GREEN'})
        self.assertEqual(1, q.count())
        self.assertEqual(obj1, q.get())


    def test_set_deduplication_is_done_by_save(self):
        obj = SetTest(text_value=['RED', 'GREEN', 'RED', 'GREEN', 'RED', 'GREEN'], int_value=[1, 2, 1, 2, 3])
        obj.save()

        # Check to ensure we didn't mutate the original object (full_clean will do that)
        self.assertStrictEqual(['RED', 'GREEN', 'RED', 'GREEN', 'RED', 'GREEN'], obj.text_value)
        self.assertStrictEqual([1, 2, 1, 2, 3], obj.int_value)

        q = SetTest.objects.filter(text_value__len=6)
        self.assertEqual(0, q.count())

        q = SetTest.objects.filter(text_value__len=2)
        self.assertEqual(1, q.count())


    def test_set_deduplication_is_done_by_full_clean(self):
        obj = SetTest(
            text_value=['RED', 'GREEN', 'RED', 'GREEN', 'RED', 'GREEN'],
            int_value=[1, 2, 1, 2, 3],
        )
        obj.full_clean()

        self.assertStrictEqual({'RED', 'GREEN'}, obj.text_value)
        self.assertStrictEqual({1, 2, 3}, obj.int_value)
