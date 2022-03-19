import psycopg2
from psycopg2.sql import SQL
from settings import DATABASE_URL


class Database:

    INIT_DATABASE = SQL("""
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            data BYTEA NOT NULL
        );
    """)

    INSERT_IMAGE = SQL("""
        INSERT INTO images (data) VALUES (%s) RETURNING id;
    """)

    SELECT_IMAGE = SQL("""
        SELECT data FROM images WHERE id = %s;
    """)


    conn = None


    @classmethod
    def init_database(cls) -> None:
        try:
            cls.conn = psycopg2.connect(DATABASE_URL)
        except Exception as e:
            print(e)
            quit()
            
        with cls.conn.cursor() as cursor:
            cursor.execute(cls.INIT_DATABASE)
        cls.conn.commit()


    @classmethod
    def insert_image(cls, image: bytes) -> int:
        with cls.conn.cursor() as cursor:
            cursor.execute(cls.INSERT_IMAGE, (image,))
            cls.conn.commit()
            return cursor.fetchone()[0]


    @classmethod
    def select_image(cls, image_id: int) -> bytes | None:
        with cls.conn.cursor() as cursor:
            cursor.execute(cls.SELECT_IMAGE, (image_id,))
            data = cursor.fetchone()
            if data is None:
                return None
            return data[0].tobytes()


