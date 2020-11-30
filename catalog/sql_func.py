
def wrap_quotes(query_dict):
    return dict([(f"`{k}`", (f"'{v}'" if not str(v).isnumeric() else v))
                 for k, v in query_dict.items()])


def clean_kwargs(list_keys, **kwargs):
    return dict(filter(lambda k: k[0] in list_keys, kwargs.items()))


def dict_factory(cursor, row):
    return \
        dict((d[0], row[i])
             for i, d in enumerate(cursor.description))


def stringify_column_data(data):
    type_trans = {
        None: 'NULL', int: 'INTEGER', float: 'REAL', str: 'TEXT', bytes: 'BLOB'
    }

    def prop_trans_type(v, d):
        return type_trans[v] + (f'({d["length"]})' if 'length' in d else '')

    prop_trans = {
        'type': prop_trans_type,
        'primary_key': lambda v, d: ('', 'PRIMARY KEY')[v],
        'not_null': lambda v, d: ('', 'NOT NULL')[v],
        'unique': lambda v, d: ('', 'UNIQUE')[v]
    }

    pieces = list()

    for key, value in data.items():
        if key in prop_trans:
            pieces.append(prop_trans[key](value, data))

    return ' '.join(pieces)


def spread(iterable, *args) -> str:
    glue = str(args[0])
    iterable = [spread(v, *args[1::])
                if len(args) > 1 and hasattr(v, '__iter__') else str(v)
                for k, v in enumerate(iterable)]

    return glue.join(iterable)
