from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class SetField(ArrayField):
    """Stores set objects.
    
    Uses Array on PostgreSQL.
    """
    description = _("SetField")
    default_error_messages = {
        'not_iterable': _('Set field only accepts iterables'),
        **ArrayField.default_error_messages
    }

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return value
        else:
            try:
                return set(value)
            except TypeError:
                return value


    def get_db_prep_value(self, value, connection, prepared=False):
        # Normalise to list and pass on to ArrayField.  Avoid first
        # going through "set" constructor if it's already a set, for
        # performance reasons.
        if hasattr(value, '__iter__') and not isinstance(value, (set, frozenset)):
            return super().get_db_prep_value(list(set(value)), connection, prepared=prepared)
        elif isinstance(value, (set, frozenset)):
            return super().get_db_prep_value(list(value), connection, prepared=prepared)
        else:
            return super().get_db_prep_value(value, connection, prepared=prepared)


    def __init__(self, base_field, size=None, **kwargs):
        super().__init__(base_field, size=None, **kwargs)
        # Overwrite hack set by parent.  For performance reasons, we
        # avoid converting to a list first and then to a set.
        if not hasattr(self.base_field, 'from_db_value'):
            self.from_db_value = self._simple_from_db_value
        else:
            self.from_db_value = self._from_db_value


    def _simple_from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return set(value)


    # Override parent, so we don't create a list first
    def _from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return {
            self.base_field.from_db_value(item, expression, connection)
            for item in value
        }


    # This is actually an improvement over ArrayField, which doesn't
    # validate that it receives a list as input, and will just crash
    # hard instead...
    def validate(self, value, model_instance):
        if hasattr(value, '__iter__'):
            super().validate(value, model_instance)
        else:
            raise ValidationError(self.error_messages['not_iterable'], code='not_iterable')
