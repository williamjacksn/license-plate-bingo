import datetime
import fort
import uuid

STATE_NAME_TO_ABBR = {
    'Alabama':       'AL', 'Alaska':      'AK', 'Arizona':        'AZ', 'Arkansas':      'AR', 'California':     'CA',
    'Colorado':      'CO', 'Connecticut': 'CT', 'Delaware':       'DE', 'Florida':       'FL', 'Georgia':        'GA',
    'Hawaii':        'HI', 'Idaho':       'ID', 'Illinois':       'IL', 'Indiana':       'IN', 'Iowa':           'IA',
    'Kansas':        'KS', 'Kentucky':    'KY', 'Louisiana':      'LA', 'Maine':         'ME', 'Maryland':       'MD',
    'Massachusetts': 'MA', 'Michigan':    'MI', 'Minnesota':      'MN', 'Mississippi':   'MS', 'Missouri':       'MO',
    'Montana':       'MT', 'Nebraska':    'NE', 'Nevada':         'NV', 'New Hampshire': 'NH', 'New Jersey':     'NJ',
    'New Mexico':    'NM', 'New York':    'NY', 'North Carolina': 'NC', 'North Dakota':  'ND', 'Ohio':           'OH',
    'Oklahoma':      'OK', 'Oregon':      'OR', 'Pennsylvania':   'PA', 'Rhode Island':  'RI', 'South Carolina': 'SC',
    'South Dakota':  'SD', 'Tennessee':   'TN', 'Texas':          'TX', 'Utah':          'UT', 'Vermont':        'VT',
    'Virginia':      'VA', 'Washington':  'WA', 'West Virginia':  'WV', 'Wisconsin':     'WI', 'Wyoming':        'WY',
}
STATE_ABBR_TO_NAME = {v: k for k, v in STATE_NAME_TO_ABBR.items()}

class Database(fort.SQLiteDatabase):
    _version: int = None

    def games_get(self, game_id: uuid.UUID):
        sql = '''
            select found, game_id, started_at from games where game_id = :game_id
        '''
        params = {
            'game_id': game_id,
        }
        record = self.q_one(sql, params)
        if record is None:
            return None
        all_state_names = set(STATE_NAME_TO_ABBR.keys())
        found = set(record['found'].split(','))
        found.discard('')
        self.log.debug(f'{found=}')
        looking = all_state_names - found
        self.log.debug(f'{looking=}')
        return {
            'found': found,
            'game_id': game_id,
            'looking': looking,
            'started_at': record['started_at'].replace(tzinfo=datetime.timezone.utc),
        }

    def games_insert(self) -> uuid.UUID:
        sql = '''
            insert into games (found, game_id, started_at)
            values ('', :game_id, :started_at)
        '''
        game_id = uuid.uuid4()
        params = {
            'game_id': game_id,
            'started_at': datetime.datetime.utcnow(),
        }
        self.u(sql, params)
        return game_id

    def games_update(self, game_id: uuid.UUID, found: set):
        sql = '''
            update games
            set found = :found
            where game_id = :game_id
        '''
        params = {
            'found': ','.join(sorted(found)),
            'game_id': game_id,
        }
        self.u(sql, params)

    def db_migrate(self):
        self.log.info(f'Database schema version is {self.version}')
        if self.version < 1:
            self.log.info('Migrating database to schema version 1')
            self.u('''
                create table schema_versions (
                    schema_version integer primary key,
                    migration_timestamp timestamp
                )
            ''')
            self.version = 1
        if self.version < 2:
            self.log.info('Migrating database to schema version 2')
            self.u('''
                create table states (
                    state_name text,
                    state_abbreviation text
                )
            ''')
            sql = '''
                insert into states (state_name, state_abbreviation)
                values (:state_name, :state_abbreviation)
            '''
            params = [
                {'state_name': k, 'state_abbreviation': v}
                for k, v in STATE_NAME_TO_ABBR.items()
            ]
            self.b(sql, params)
            self.version = 2
        if self.version < 3:
            self.log.info('Migrating database to schema version 3')
            self.u('''
                create table games (
                    game_id uuid primary key,
                    started_at timestamp,
                    found text
                )
            ''')
            self.version = 3

    def _table_exists(self, table_name: str) -> bool:
        sql = '''
            select name from sqlite_master where type = 'table' and name = :table_name
        '''
        params = {
            'table_name': table_name,
        }
        if self.q_val(sql, params) is None:
            return False
        return True

    @property
    def version(self) -> int:
        if self._version is None:
            self._version = 0
            if self._table_exists('schema_versions'):
                sql = '''
                    select max(schema_version) current_version from schema_versions
                '''
                current_version = self.q_val(sql)
                if current_version is not None:
                    self._version = int(current_version)
        return self._version

    @version.setter
    def version(self, value: int):
        self._version = value
        sql = '''
            insert into schema_versions (schema_version, migration_timestamp)
            values (:schema_version, :migration_timestamp)
        '''
        params = {
            'migration_timestamp': datetime.datetime.utcnow(),
            'schema_version': value,
        }
        self.u(sql, params)
