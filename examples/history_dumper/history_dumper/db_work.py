# -*- coding: utf-8 -*-

import psycopg2
from psycopg2 import sql
import logging
import json

logger = logging.getLogger("LOG")

class DBWork:
    
    def __init__(self, database, user, host, port, password):
        self.database = database
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.latest_msg_id_table = "latest_msg_id"
        self.conn = None
        self.cur = None
        self.connect()
        #self.drop_table(self.latest_msg_id_table)

    def __enter__(self):
        pass
        
    def __exit__(self, type, value, traceback):
        pass
    
    def connect(self):
        self.conn = psycopg2.connect(database=self.database, user=self.user,
                                     host=self.host,
                                     password=self.password, port = self.port)
        self.cur = self.conn.cursor()
    
    def is_table_exists(self, table_name):
        if self.conn.closed != 0:
            self.connect()
        self.cur.execute("SELECT exists(SELECT * FROM information_schema.tables " + \
                         "WHERE table_name=%s)", (table_name,))
        return self.cur.fetchone()[0]

    def create_last_msg_table(self):
        if self.is_table_exists(self.latest_msg_id_table):
            return
        command = (
        """
        CREATE TABLE """ + self.latest_msg_id_table + 
        """ 
           (
            uid INTEGER PRIMARY KEY,
            msg_id INTEGER)
        """)
        if self.conn.closed != 0:
            self.connect()
        self.cur.execute(command)
        self.conn.commit()

    def update_latest_msg_id(self, uid, msg_id):
        if self.get_latest_msg_id(uid) != None:
            try:
                if self.conn.closed != 0:
                    self.connect()
                self.cur.execute(sql.SQL(
                                "UPDATE {} SET msg_id = %s WHERE uid = %s").format(
                                sql.Identifier(self.latest_msg_id_table)), 
                                [msg_id, uid])
                self.conn.commit()
                return True
            except Exception as e:
                self.conn.rollback()
                logger.critical("Exception: %s", str(e))
                return False
        else:
            try:
                if self.conn.closed != 0:
                    self.connect()
                self.cur.execute(sql.SQL(
                                "INSERT INTO {} (uid, msg_id) VALUES \
                                (%s, %s)")
                                .format(sql.Identifier(self.latest_msg_id_table)), 
                                [uid, msg_id])
                self.conn.commit()
                return True
            except Exception as e:
                self.conn.rollback()
                logger.critical("Exception: %s", str(e))
                return False

    def get_latest_msg_id(self, uid):
        try:
            if self.conn.closed != 0:
                self.connect()
            self.cur.execute(sql.SQL("SELECT msg_id FROM {} WHERE uid = %s").format(
                             sql.Identifier(self.latest_msg_id_table)), [uid])
            result = self.cur.fetchall()
            if result != []:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.critical("Exception: %s", e)
            return None

    def drop_table(self, table_name):
        if self.conn.closed != 0:
            self.connect()
        self.cur.execute('DROP TABLE "' + table_name + '";')
        self.conn.commit()

    def close_connection(self):
        self.cur.close()
        self.conn.close()