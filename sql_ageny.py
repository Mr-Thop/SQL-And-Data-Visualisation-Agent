import google.generativeai as genai
import mysql.connector

import google.generativeai as genai

class LLMAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def convert_to_sql(self, user_query):
        prompt = (
            "Convert the following natural language request into a MySQL query. "
            "ONLY return the SQL statement with no explanation, no formatting, and no markdown: "
            f"'{user_query}'"
        )

        response = self.model.generate_content(prompt)

        sql_query = response.text.strip()

        # to remove the unwanted markedown coming 
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        return sql_query


class AuthenticationAgent:
    def __init__(self, hostname, user_id, password, db_name):
        self.hostname = hostname
        self.user_id = user_id
        self.password = password
        self.db_name = db_name
        self.connection = None

    def authenticate(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.hostname,
                user=self.user_id,
                password=self.password,
                database=self.db_name
            )
            return self.connection
        except mysql.connector.Error as err:
            return f"Error: {err}"


class DatabaseAgent:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return "Query executed successfully."
        except mysql.connector.Error as err:
            return f"Error: {err}"


class UserAgent:
    def __init__(self, auth_agent, llm_agent):
        self.auth_agent = auth_agent
        self.llm_agent = llm_agent
        self.db_agent = None

    def connect(self):
        connection = self.auth_agent.authenticate()
        if isinstance(connection, str):  
            return connection
        self.db_agent = DatabaseAgent(connection)
        return "Connected to database."

    def process_natural_query(self, user_query):
        sql_query = self.llm_agent.convert_to_sql(user_query)
        if self.db_agent:
            return self.db_agent.execute_query(sql_query)
        return "Not connected to the database."


if __name__ == "__main__":
    GEMINI_API_KEY = "AIzaSyCvgsI2AYmYHv27I1IfMF5X1wNWENP2tsU"  

    hostname = input("Enter hostname: ")
    user_id = input("Enter user ID: ")
    password = input("Enter password: ")
    db_name = input("Enter database name: ")

    auth_agent = AuthenticationAgent(hostname, user_id, password, db_name)
    llm_agent = LLMAgent(GEMINI_API_KEY)
    user_agent = UserAgent(auth_agent, llm_agent)

    print(user_agent.connect())  # Authenticate & connect

    while True:
        user_query = input("Enter your request (or 'exit' to quit): ")
        if user_query.lower() == "exit":
            break
        print(user_agent.process_natural_query(user_query))
