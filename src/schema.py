"""Helpers for schema validation."""

import os.path as path
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
    print('jimmy', schema)
    return jsonschema.validate(data, schema)


def _load_json_schema(filename):
    """Load schema file, correctly dereferencing relative file references."""
    if filename not in SCHEMA_CACHE:
        relative_path = path.join('schemas', filename)
        absolute_path = path.join(path.dirname(__file__), relative_path)

        base_path = path.dirname(absolute_path)
        base_uri = 'file://{}/'.format(base_path)
        base_uri = pathlib.Path(base_path).as_uri() + '/'
        
        #base_uri = 'file://C:/Users/boylejim/Documents/GitHub/FeatureToggles/src/schemas/'
        with open(absolute_path) as schema_file:
            print(absolute_path)
            print(base_uri)
            SCHEMA_CACHE[filename] = jsonref.loads(
                schema_file.read(),
                base_uri=base_uri,
                jsonschema=True
            )

    return SCHEMA_CACHE[filename]
