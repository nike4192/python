import sqlite3
from sql_func import *
import valid

TABLE_NAME = 'catalog'
TABLE_COLUMNS = {  # IMPORTANT: keys of this dict is keys for **kwargs add_profile
    'first_name': {
        'type': str, 'length': 40, 'not_null': True
    },
    'last_name': {
        'type': str, 'length': 40
    },
    'phone': {
        'type': str, 'length': 20, 'unique': True,
        'valid': valid.phone
    },
    'city': {
        'type': str, 'length': 40
    },
    'email': {
        'type': str, 'length': 50, 'not_null': True, 'unique': True,
        'valid': valid.email
    }
}


class Profile:
    def __init__(self, catalog, data):
        self.__catalog = catalog
        for k in TABLE_COLUMNS:
            self[k] = data[k]

    def data(self):
        return dict((k, self[k]) for k in TABLE_COLUMNS)

    def print(self):
        values = [getattr(self, k) for k in TABLE_COLUMNS]
        print(spread(values, ' '))

    def update(self, **kwargs):
        self.__catalog.update_profile(self, **kwargs)

    def delete(self):
        self.__catalog.delete_profile(self)

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        self.__dict__.update({key: value})


class Catalog:
    column_names = list(TABLE_COLUMNS.keys())

    def __init__(self, db_name='catalog'):
        try:
            self.__conn = self.conn = conn = sqlite3.connect(f'{db_name}.db')

            table_name = TABLE_NAME
            columns = TABLE_COLUMNS

            spread_columns = \
                spread(  # sic esoteric
                    [(k, stringify_column_data(v))
                     for k, v in columns.items()], ',\n', ' ')

            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id integer PRIMARY KEY,
                    {spread_columns}
                )
            ''')
        except ValueError:
            pass

    def push_profile(self, tuple_data):
        kwargs = dict(zip(self.column_names, tuple_data))
        return self.add_profile(**kwargs)

    def add_profile(self, **kwargs):  # see TABLE_COLUMNS keys

        conn = self.__conn
        table_name = TABLE_NAME
        profile_data = {}

        # START CHECK RECORD
        for key, column_data in TABLE_COLUMNS.items():
            # 1
            if key not in kwargs:
                if column_data.get('not_null') and not column_data.get('primary_key'):
                    raise Exception(f'property {key} is required')
                continue

            valid_func = column_data.get('valid')
            # 2
            if callable(valid_func):
                if not valid_func(kwargs[key]):
                    raise Exception(f'{kwargs.get(key)} of {key} is not valid')
            # 3
            if column_data.get('unique'):
                if conn.execute(f'''
                    SELECT id FROM {table_name} WHERE {key} = '{kwargs[key]}'
                ''').fetchone() is not None:
                    raise Exception(f'{kwargs[key]} of {key} must be unique')

            profile_data[key] = kwargs[key]
        # END CHECK RECORD

        spread_keys = spread([f'`{k}`' for k in profile_data.keys()], ', ')
        spread_values = spread([f"'{v}'" for v in profile_data.values()], ', ')

        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                INSERT INTO {table_name} ({spread_keys})
                VALUES ({spread_values})
            ''')

            conn.commit()

            return Profile(self, kwargs)

        except ValueError:
            pass

    def get_profile(self, **kwargs):

        spread_column_names = spread(self.column_names, ', ')
        spread_pairs = spread(wrap_quotes(kwargs).items(), ' AND ', ' = ')

        cursor = self.__conn.execute(f'''
            SELECT {spread_column_names} FROM {TABLE_NAME}
            WHERE {spread_pairs}
        ''')

        return Profile(self, dict_factory(cursor, cursor.fetchone()))

    def update_profile(self, profile: Profile, **kwargs):

        spread_sets = spread(wrap_quotes(kwargs).items(), ', ', ' = ')
        spread_pairs = spread(wrap_quotes(profile.data()).items(), ' AND ', ' = ')

        try:
            self.__conn.execute(f'''
                UPDATE {TABLE_NAME} SET
                {spread_sets}
                WHERE {spread_pairs}
            ''')

            self.__conn.commit()

            for k in kwargs:
                profile[k] = kwargs[k]

            return profile

        except ValueError:
            pass

    def delete_profile(self, profile):

        spread_pairs = spread(wrap_quotes(profile.data()).items(), ' AND ', ' = ')

        try:
            cursor = self.__conn.execute(f'''
                DELETE FROM {TABLE_NAME}
                WHERE {spread_pairs}
            ''')

            self.__conn.commit()

            del profile

            return True

        except ValueError:
            pass

        return False

    def get_all_profiles(self, **kwargs):

        limit = kwargs.get('limit')

        kwargs = clean_kwargs([*self.column_names, 'id'], **kwargs)

        spread_column_names = spread(self.column_names, ', ')
        spread_pairs = spread(wrap_quotes(kwargs).items(), ' AND ', ' = ')

        try:
            cursor = self.__conn.execute(f'''
                SELECT {spread_column_names} FROM {TABLE_NAME}
                {('--', '')[bool(spread_pairs)]} WHERE {spread_pairs}
                {('--', '')[bool(limit)]} LIMIT {limit}''')

            return [Profile(self, dict(zip(self.column_names, v)))
                    for v in cursor.fetchall()]

        except ValueError:
            pass

    def clear_all(self):

        try:
            cursor = self.__conn.execute(f'''
                DELETE FROM {TABLE_NAME}
            ''')

            self.__conn.commit()

            return True

        except ValueError:
            pass

        return False