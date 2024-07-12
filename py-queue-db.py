import asyncio
from aiohttp import web
import sqlite3
import json
from datetime import datetime

class KafkaLikeDB:
    def __init__(self, db_name='kafka_like.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offsets (
                topic TEXT,
                consumer_group TEXT,
                offset INTEGER,
                PRIMARY KEY (topic, consumer_group)
            )
        ''')
        self.conn.commit()

    def publish_message(self, topic, message):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO messages (topic, message) VALUES (?, ?)', (topic, message))
        self.conn.commit()
        return cursor.lastrowid

    def get_messages(self, topic, offset, limit):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, message FROM messages WHERE topic = ? AND id > ? ORDER BY id LIMIT ?', (topic, offset, limit))
        return cursor.fetchall()

    def get_offset(self, topic, consumer_group):
        cursor = self.conn.cursor()
        cursor.execute('SELECT offset FROM offsets WHERE topic = ? AND consumer_group = ?', (topic, consumer_group))
        result = cursor.fetchone()
        return result[0] if result else 0

    def set_offset(self, topic, consumer_group, offset):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO offsets (topic, consumer_group, offset) VALUES (?, ?, ?)', (topic, consumer_group, offset))
        self.conn.commit()

class KafkaLikeServer:
    def __init__(self):
        self.db = KafkaLikeDB()
        self.app = web.Application()
        self.app.router.add_post('/publish', self.publish)
        self.app.router.add_get('/poll', self.poll)
        self.app.router.add_post('/commit', self.commit)

    async def publish(self, request):
        data = await request.json()
        topic = data['topic']
        message = data['message']
        message_id = self.db.publish_message(topic, json.dumps(message))
        return web.json_response({'status': 'ok', 'message_id': message_id})

    async def poll(self, request):
        topic = request.query.get('topic')
        consumer_group = request.query.get('consumer_group')
        timeout = int(request.query.get('timeout', 0))
        
        start_time = datetime.now()
        while True:
            offset = self.db.get_offset(topic, consumer_group)
            messages = self.db.get_messages(topic, offset, 10)
            
            if messages or (datetime.now() - start_time).total_seconds() >= timeout:
                return web.json_response({
                    'messages': [{'id': m[0], 'message': json.loads(m[1])} for m in messages]
                })
            
            await asyncio.sleep(1)

    async def commit(self, request):
        data = await request.json()
        topic = data['topic']
        consumer_group = data['consumer_group']
        offset = data['offset']
        self.db.set_offset(topic, consumer_group, offset)
        return web.json_response({'status': 'ok'})

    def run(self):
        web.run_app(self.app)

if __name__ == '__main__':
    server = KafkaLikeServer()
    server.run()
