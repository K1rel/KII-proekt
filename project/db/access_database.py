from typing import Dict, List, Union
import psycopg2
from psycopg2 import sql
from psycopg2 import pool
from project.db.config_database import ConfigDatabase

class AccessDataBase(ConfigDatabase):

    def __init__(self) -> None:
        self.logger.debug('Init Class AccessDataBase')
        
        # Set up connection pool
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,  # min and max connections
            dbname=self.postgres_access['database'],
            user=self.postgres_access['user'],
            password=self.postgres_access['password'],
            host=self.postgres_access['host'],
            port=self.postgres_access['port']
        )
        
        # Initialize table
        self._initialize_table()
        self.logger.debug('CLASS AccessDataBase INITED')
        
    def _initialize_table(self):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL('''CREATE TABLE IF NOT EXISTS {table_name}(
                                    message_id SERIAL PRIMARY KEY NOT NULL,
                                    message_title VARCHAR(30) NOT NULL UNIQUE,
                                    author_name VARCHAR(30) NOT NULL,
                                    message_text VARCHAR(200) NOT NULL,
                                    creation_date DATE NOT NULL)''').format(
                                        table_name=sql.Identifier(self.table_name)
                                    )
                cursor.execute(query)
                conn.commit()
        except Exception as e:
            self.logger.error(f'Error initializing table: {e}')
        finally:
            self.pool.putconn(conn)
        
    def get_messages(self, indice: int=0):
        self.logger.debug('GETTING DATA')
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("SELECT * FROM {table_name} ORDER BY creation_date DESC;").format(
                    table_name=sql.Identifier(self.table_name)
                )
                cursor.execute(query)
                datas = cursor.fetchall()
                self.logger.debug('QUERY EXECUTED')
        except Exception as e:
            self.logger.error(f'Error fetching messages: {e}')
            datas = []
        finally:
            self.pool.putconn(conn)
        
        self.logger.debug('RETURNING DATA')
        if indice:
            end = indice * 3 - 1
            start = end - 2
            return datas[start:end + 1]
        else:
            return datas
    
    def get_message_by_condition(self, target_query: List[Union[int, str]]=[]):
        self.logger.debug('GETTING DATA')
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("SELECT * FROM {table_name} WHERE {column} = %s;").format(
                    table_name=sql.Identifier(self.table_name),
                    column=sql.Identifier(target_query[0])
                )
                cursor.execute(query, (target_query[1],))
                data = cursor.fetchone()
                self.logger.debug('QUERY EXECUTED')
        except Exception as e:
            self.logger.error(f'Error fetching message by condition: {e}')
            data = None
        finally:
            self.pool.putconn(conn)
        
        self.logger.debug('RETURNING DATA')
        return data
    
    def insert_message(self, message_rows: Dict[str, str]):
        self.logger.debug(f'INSERT INTO {self.table_name} VALUES({message_rows})')
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("INSERT INTO {table_name} (message_title, author_name, message_text, creation_date) VALUES (%s, %s, %s, %s);").format(
                    table_name=sql.Identifier(self.table_name)
                )
                insert_tuple = (
                    message_rows['message_title'],
                    message_rows['author_name'],
                    message_rows['message_text'],
                    message_rows['creation_date']
                )
                cursor.execute(query, insert_tuple)
                conn.commit()
                self.logger.debug('SUCCESS')
        except Exception as e:
            self.logger.error(f'Error inserting message: {e}')
        finally:
            self.pool.putconn(conn)
    
    def update_message(self, message_id: int, args: List[Union[str, str]]):
        self.logger.debug('UPDATE DATA')
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("UPDATE {table_name} SET {column} = %s WHERE message_id = %s;").format(
                    table_name=sql.Identifier(self.table_name),
                    column=sql.Identifier(args[0])
                )
                cursor.execute(query, (args[1], message_id))
                conn.commit()
                self.logger.debug('QUERY EXECUTED')
        except Exception as e:
            self.logger.error(f'Error updating message: {e}')
        finally:
            self.pool.putconn(conn)
    
    def remove_message(self, message_id: int):
        self.logger.debug('REMOVING DATA')
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("DELETE FROM {table_name} WHERE message_id = %s;").format(
                    table_name=sql.Identifier(self.table_name)
                )
                cursor.execute(query, (message_id,))
                conn.commit()
                self.logger.debug('DELETE EXECUTED')
        except Exception as e:
            self.logger.error(f'Error removing message: {e}')
        finally:
            self.pool.putconn(conn)
    
    def get_message_length(self):
        self.logger.debug('GETTING DATA')
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                query = sql.SQL("SELECT COUNT(*) FROM {table_name};").format(
                    table_name=sql.Identifier(self.table_name)
                )
                cursor.execute(query)
                data = cursor.fetchone()[0]
                self.logger.debug('QUERY EXECUTED')
        except Exception as e:
            self.logger.error(f'Error getting message length: {e}')
            data = 0
        finally:
            self.pool.putconn(conn)
        
        self.logger.debug('RETURNING DATA')
        return data
