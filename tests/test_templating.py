import jinja2
import pytest

from prometheus_communicator.templating import validate_template


class TestValidateTemplate:
    def test_success(self):
        template = jinja2.Template("{{ commonAnnotations.summary }}")
        validate_template(template)

    def test_error(self):
        template = jinja2.Template("{{ commonAnnotations.summary.nested }}")
        with pytest.raises(ValueError, match="Invalid template"):
            validate_template(template)
