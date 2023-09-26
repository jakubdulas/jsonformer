import pydantic

def get_annotations(obj):
    annotations = {}
    for o in obj.__mro__:
        if hasattr(o, "__annotations__"):
            annotations = {**annotations, **o.__annotations__}
    return annotations


def set_value(field, field_type):
    if field_type == "str":
        return {
            "type": "string",
        }
    elif field_type == "int" or field_type == "float":
        return  {
            "type": "number",
        }
    elif field_type == "bool":
        return {
            "type": "boolean",
        }
    elif field_type == "Literal":
        if len(field.__args__) == 0:
            raise Exception("You have to specify at least one possible value")
        return {
            "type": "enum",
            "values": list(field.__args__)
        }
    elif field_type == "list":
        if len(field.__args__) > 1:
            raise Exception("Only one-type list is allowed")
        if len(field.__args__) == 0:
            raise Exception("You have to specify list item type")
        
        list_field = field.__args__[0]
        list_field_type = list_field.__name__ if hasattr(list_field, "__name__") else str(list_field)

        new_block = {
            "type": "array",
            "items": {}
        }
        if type(list_field) == pydantic.main.ModelMetaclass:
            new_block["items"] = create_scheme(list_field, scheme={})
            return new_block
        return {
            "type": "array",
            "items": set_value(list_field, list_field_type)
        }
    return None
    

def create_scheme(obj, scheme={}):
    annotations = get_annotations(obj)
    for field_name, field in annotations.items():
        field_type = field.__name__ if hasattr(field, "__name__") else str(field)

        if type(field) == pydantic.main.ModelMetaclass:
            scheme[field_name] = {
                "type": "object",
                "properties": {}
            }
            create_scheme(field, scheme[field_name]["properties"])
            continue
        
        value = set_value(field, field_type)
        if value:
            scheme[field_name] = value
            continue
        else:
            raise Exception(f"Unsupported data type: {field_type}")

    return {"type": "object", "properties": scheme}
