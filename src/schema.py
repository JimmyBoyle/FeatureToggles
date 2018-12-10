"""Helpers for schema validation."""
import pathlib
import jsonref
import jsonschema

SCHEMA_CACHE = {}


def validate_update_feature_toggles_request(request):
    """Validate update_feature_toggles request."""
    return _validate(request, "update_feature_toggles_request.json")


def _validate(data, schema_filename):
    """Validate data against given JSON schema file."""
    schema = _load_json_schema(schema_filename)
    return jsonschema.validate(data, schema)


def _load_json_schema(filename):
    """Load schema file, correctly dereferencing relative file references."""
    if filename not in SCHEMA_CACHE:
        absolute_path = pathlib.Path(__file__).parent / 'schemas' / filename
        base_uri = pathlib.Path(absolute_path).parent.as_uri()
        
        with open(absolute_path) as schema_file:
            SCHEMA_CACHE[filename] = jsonref.loads(
                schema_file.read(),
                base_uri=base_uri + '/',
                jsonschema=True
            )

    return SCHEMA_CACHE[filename]
