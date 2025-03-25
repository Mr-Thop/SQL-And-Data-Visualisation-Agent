import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import logging
from datetime import datetime
from io import BytesIO
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import mysql.connector
import os



app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Configure Generative AI model
API_KEY = os.getenv("API_KEY")
genai.configure(api_key= API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Store user session data
user_data = {}

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

class AIVisualizer:
    def __init__(self, df):
        self.df = df
        self.state = "START"
        self.log_state("Initialization complete.")

    def log_state(self, message):
        logging.info(f"State: {self.state} | {message}")
        self.state = message

    def generate_visualization(self, query):
        self.log_state("PROCESS - AI interpreting query")

        prompt = f"""
        Given the dataset with columns {list(self.df.columns)}, interpret the following query:
        "{query}"
        
        Identify the visualization type from: ["histogram", "scatter plot", "box plot", "bar chart", "pair plot", "pie chart", "heatmap"].
        based on the user Query and in the response provide the visualisation from the above format itself. Dont give any columns when the visualization is pairplot or heatmap.
        **Example Format:**

        User Query: "Show me a bar chart of sales by category."
        Response: {{ "visualization": "bar chart", "columns": ["Category", "Sales"] }}

        Return a JSON in this format:
        {{ "visualization": "chosen_type", "columns": ["col1", "col2"] }}
        """


        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip() if response and response.text else ""

            logging.info(f"AI Response: {response_text}")

            if not response_text:
                self.log_state("ERROR - AI returned an empty response.")
                return None

            # ✅ Ensure AI response is JSON
            # Remove triple backticks if present
            response_text = response_text.strip("```json").strip("```")

            try:
                result = json.loads(response_text)
                vis_type = result.get("visualization")
                columns = result.get("columns", [])

                if not vis_type or not columns:
                    self.log_state("ERROR - Missing keys in AI response.")
                    return None

                return self.create_plot(vis_type, columns)
            except json.JSONDecodeError:
                self.log_state("ERROR - Failed to interpret AI response: Invalid JSON format.")
                return None

        except Exception as e:
            self.log_state(f"ERROR - Unexpected error: {e}")
            return None
    
    def create_plot(self, vis_type, columns):
        self.log_state(f"PROCESS - Generating {vis_type} for {columns}")
        plt.figure(figsize=(8, 6))

        try:
            if vis_type == "histogram":
                sns.histplot(self.df[columns[0]], kde=True)
            elif vis_type == "scatter plot" and len(columns) >= 2:
                sns.scatterplot(x=self.df[columns[0]], y=self.df[columns[1]])
            elif vis_type == "box plot":
                sns.boxplot(x=self.df[columns[0]])
            elif vis_type == "bar chart":
                self.df[columns[0]].value_counts().plot(kind='bar')
            elif vis_type == "line graph":
                self.df[columns].plot(kind='line')
            elif vis_type == "pie chart":
                self.df[columns[0]].value_counts().plot(kind='pie', autopct='%1.1f%%')
            elif vis_type == "heatmap":
                sns.heatmap(self.df.corr(), annot=True, cmap="coolwarm")
            else:
                self.log_state("ERROR - Unknown visualization type")
                return None
            
            return self._plot_to_base64()
        except Exception as e:
            self.log_state(f"ERROR - Failed to generate plot: {e}")
            return None
    
    def _plot_to_base64(self):
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

# Initialize components
db_manager = DatabaseManager()
llm_agent = StatefulSQLAgent(API_KEY)

@app.route('/connect', methods=['GET','POST'])
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

@app.route('/query', methods=['GET','POST'])
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

@app.route('/upload', methods=['GET','POST'])
def upload_csv():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        csv_base64 = data.get('csv_data')
        
        if not csv_base64:
            return jsonify({"error": "No CSV data provided"}), 400
        
        csv_bytes = base64.b64decode(csv_base64)
        df = pd.read_csv(BytesIO(csv_bytes))
        user_data[user_id] = df
        
        return jsonify({"user_id": user_id, "columns": df.columns.tolist()})
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/visualize', methods=['GET','POST'])
def visualize():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        query = data.get('query')

        if user_id not in user_data:
            return jsonify({"error": "No data uploaded for this user"}), 400
        
        df = user_data[user_id]
        visualizer = AIVisualizer(df)
        image_base64 = visualizer.generate_visualization(query)
        
        if image_base64:
            return jsonify({"image": image_base64, "query": query})
        else:
            return jsonify({"error": "Failed to generate visualization"}), 500
    except Exception as e:
        logging.error(f"Error generating visualization: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/',methods=['GET'])
def hello():
    return 'Agent\'s Backend is Running Successfully'

if __name__ == '__main__':
    app.run(debug=True)