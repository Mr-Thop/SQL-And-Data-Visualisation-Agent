from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import mysql.connector
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
logging.basicConfig(level=logging.INFO)

class StatefulSQLAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.states = []
        self.context = {}

    def log_state(self, state, message=None):
        state_info = {
            "state": state,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.states.append(state_info)
        logging.info(f"State {state}: {message or ''}")
        return state_info

    def generate_initial_sql(self, query, schema):
        try:
            self.log_state("PROCESS", "Generating initial SQL")
            schema_info = "\n".join(
                [f"Table {table} ({', '.join(columns)})" 
                 for table, columns in schema.items()]
            )
            
            prompt = f"""**Database Schema:**
{schema_info}

**Natural Language Query:**
{query}

Generate a MySQL query that satisfies the request. Consider:
1. Table relationships
2. Appropriate JOINs
3. Correct column names
4. Proper aggregation if needed

Return ONLY the SQL query without any explanations or formatting."""
            
            response = self.model.generate_content(prompt)
            sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
            self.context['current_sql'] = sql
            self.log_state("OBSERVATION", f"Generated initial SQL: {sql}")
            return True, sql
        except Exception as e:
            return False, str(e)

    def refine_sql(self, error, schema):
        try:
            self.log_state("PROCESS", "Refining SQL based on error")
            prompt = f"""**Previous Error:**
{error}

**Current SQL:**
{self.context['current_sql']}

**Database Schema:**
{schema}

Generate a corrected SQL query addressing the error. Return ONLY the SQL."""
            
            response = self.model.generate_content(prompt)
            sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
            self.context['current_sql'] = sql
            self.log_state("OBSERVATION", f"Refined SQL: {sql}")
            return True, sql
        except Exception as e:
            return False, str(e)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, host, user, password, database, port):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True, "Connected successfully"
        except mysql.connector.Error as err:
            return False, f"MySQL Error: {err}"

    def get_schema(self):
        try:
            schema = {}
            tables = self.get_tables()
            for table in tables:
                columns = self.get_columns(table)
                schema[table] = columns
            return True, schema
        except Exception as e:
            return False, str(e)

    def get_tables(self):
        self.cursor.execute("SHOW TABLES")
        return [row[f"Tables_in_{self.connection.database}"] for row in self.cursor.fetchall()]

    def get_columns(self, table):
        self.cursor.execute(f"DESCRIBE {table}")
        return [row['Field'] for row in self.cursor.fetchall()]

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            if self.cursor.with_rows:
                return self.cursor.fetchall(), None
            return "Query executed successfully", None
        except mysql.connector.Error as err:
            return None, f"MySQL Error: {err}"

# Initialize components
db_manager = DatabaseManager()
llm_agent = StatefulSQLAgent("API_KEY_HERE") #add your api key here

@app.route('/api/connect', methods=['POST'])
def connect():
    data = request.json
    success, message = db_manager.connect(
        data['host'],
        data['user'],
        data['password'],
        data['database'],
        data['port']
    )
    return jsonify({"success": success, "message": message})

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.json
    llm_agent.log_state("START")
    
    try:
        llm_agent.log_state("INPUT", f"Received query: {data['query']}")
        
        # Get schema information
        success, schema = db_manager.get_schema()
        if not success:
            raise Exception(schema)
        
        # Generate initial SQL
        success, sql = llm_agent.generate_initial_sql(data['query'], schema)
        if not success:
            raise Exception(sql)
        
        # Refinement loop
        max_retries = 3
        for attempt in range(max_retries):
            result, error = db_manager.execute_query(sql)
            if error:
                success, sql = llm_agent.refine_sql(error, schema)
                if not success:
                    raise Exception(sql)
            else:
                llm_agent.log_state("OUTPUT", "Query executed successfully")
                llm_agent.log_state("STOP", "Process completed successfully")
                return jsonify({
                    "status": "success",
                    "result": result,
                    "sql": sql,
                    "states": llm_agent.states
                })
        
        raise Exception("Maximum refinement attempts reached")
    
    except Exception as e:
        llm_agent.log_state("STOP", f"Process failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "states": llm_agent.states
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
