import datetime
import fort

class Database(fort.SQLiteDatabase):
    _version: int = None

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

    def _table_exists(self, table_name: str) -> bool:
        sql = '''
            select name from sqlite_schema where type = 'table' and name = :table_name
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
