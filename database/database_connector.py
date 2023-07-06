import psycopg2


class DatabaseConnector:
    def __init__(self, db_config):
        """
        Initialize DatabaseConnector with db_config.
        """
        self.host = db_config["host"]
        self.port = db_config["port"]
        self.database = db_config["database"]
        self.user = db_config["user"]
        self.password = db_config["password"]

    def connect(self):
        """
        Try to establish a connection to the database.
        """
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Exception as e:
            print("Database Error: ", e)


class StreamLitDatabaseConnector:

    def connect(self, db_config):
        """
        Try to establish a connection to the database.
        """
        try:
            print(db_config)
            connection = psycopg2.connect(**db_config)
            return connection
        except Exception as e:
            print("Database Error: ", e)
