# SQL Agent

This project provides an interactive agent system that allows users to convert natural language queries into MySQL queries using Google Gemini API and execute them against a MySQL database. The system consists of multiple agents for managing authentication, SQL query generation, and database interaction.

## **Overview**

This system uses Google’s generative AI (Gemini) to translate natural language into MySQL queries. It then connects to a MySQL database and executes the generated query. The architecture includes:

- **LLM Agent**: Uses Google's Gemini API to generate SQL queries from natural language.
- **Authentication Agent**: Manages MySQL authentication and connects to the database.
- **Database Agent**: Executes the generated SQL queries against the connected MySQL database.
- **User Agent**: Facilitates interaction between the user and the system, managing database connections and query executions.

## **How it Works**

1. **Input**: The user inputs a natural language query (e.g., "Find all employees with salaries greater than 50000").
2. **Processing**: The query is converted to an SQL query using Google's Gemini AI model.
3. **Execution**: The generated SQL query is executed against the MySQL database.
4. **Output**: Results from the database are returned to the user.

## **Installation**

1. Clone the repository to your local machine.

```bash
git clone https://github.com/yourusername/SQL-And-Data-Visualisation-Agent.git
cd SQL-And-Data-Visualisation-Agent
```

2. Install the required Python libraries.

```bash
pip install -r requirements.txt
```

3. **Google Gemini API Key**: Ensure you have a valid API key from Google Generative AI (Gemini). Set the API key as an environment variable:

```bash
export API_KEY="your-gemini-api-key"
```

Alternatively, you can hard-code it in the script, but it's not recommended for security reasons.

4. Install the MySQL connector for Python.

```bash
pip install mysql-connector-python
```

## **Usage**

1. **Run the Script**: Start the application by running the `main.py` script.

```bash
python main.py
```

2. **Input Credentials**: When prompted, enter your MySQL database connection details:
    - Hostname: The address of your MySQL server (e.g., `localhost`).
    - User ID: Your MySQL username.
    - Password: Your MySQL password.
    - Database Name: The name of the database to interact with.

3. **Input Queries**: You can now input natural language queries. For example:
    - "Select all customers with an email address"
    - "Show me all employees hired after 2020"

4. **Exit**: Type `exit` to quit the program.

## **Code Explanation**

### **LLMAgent Class**

- This class handles communication with the Google Gemini API.
- It takes the user's natural language query and converts it into a valid MySQL query.
- Uses the `GenerativeModel` from the `google.generativeai` module to generate content based on a provided prompt.

### **AuthenticationAgent Class**

- This class handles authentication with the MySQL database using the `mysql.connector` library.
- It establishes a connection to the database using the provided credentials.

### **DatabaseAgent Class**

- This class is responsible for executing SQL queries on the connected MySQL database.
- It uses a MySQL cursor to run the query and handle the results (either fetch results or commit changes).

### **UserAgent Class**

- This class acts as a mediator between the user and the agents.
- It connects to the database, processes the user’s natural query, and returns the result of the executed SQL query.
- It uses both the `LLMAgent` and `AuthenticationAgent` to streamline the user experience.

## **Environment Variables**

- **API_KEY**: Google Gemini API key for accessing the generative model. Make sure to set this in your environment or directly in the script (not recommended for security reasons).

## **Error Handling**

- If there are issues with database authentication or query execution, appropriate error messages will be displayed.
- If the system is not connected to the database, it will prompt you to first establish a connection.

## **Future Enhancements**

- Support for more databases beyond MySQL (e.g., PostgreSQL, SQLite).
- Ability to handle more complex queries with enhanced validation.
- Option to log queries and results for auditing or debugging purposes.
- Implement more advanced natural language processing features for improved query accuracy.

## **Contributing**

If you would like to contribute to this project:

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a pull request with a description of the changes you have made.

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify the README as needed based on the actual setup and requirements of your project!
