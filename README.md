The **SQL and Data Visualization Agent** is an interactive system designed to convert natural language queries into SQL commands using Google's Gemini API, execute them on a MySQL database, and present the results through various data visualizations. This tool streamlines the process of database querying and data analysis, making it accessible to users without extensive SQL knowledge.

## Features

- **Natural Language to SQL Conversion**: Utilizes Google's Gemini API to translate user-friendly language into precise SQL queries.
- **Database Interaction**: Connects to a MySQL database to execute generated SQL commands.
- **Data Visualization**: Presents query results through various visualization techniques, enhancing data interpretation.

## Components

1. **LLM Agent**: Interacts with the Gemini API to generate SQL queries from natural language inputs.
2. **Authentication Agent**: Manages authentication and establishes connections to the MySQL database.
3. **Database Agent**: Executes SQL queries and retrieves results from the database.
4. **User Agent**: Coordinates interactions between the user, LLM Agent, and Database Agent to facilitate seamless operations.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mr-Thop/SQL-And-Data-Visualisation-Agent.git
   cd SQL-And-Data-Visualisation-Agent
   ```


2. **Install Dependencies**:
   Ensure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


3. **Set Up Google Gemini API Key**:
   Obtain an API key from Google and set it as an environment variable:
   ```bash
   export GEMINI_API_KEY='your_api_key_here'
   ```


4. **Configure Database Connection**:
   Update the database configuration in the `config.py` file with your MySQL database credentials.

## Usage

1. **Start the Application**:
   ```bash
   python main.py
   ```


2. **Interact with the Agent**:
   Input your natural language queries when prompted. The system will process these inputs, generate SQL queries, execute them, and display the results along with appropriate visualizations.

## Example

- **User Input**: "Show the average sales per month for the last year."
- **System Process**:
  - Converts the input into an SQL query.
  - Executes the query on the connected MySQL database.
  - Generates a line chart displaying average sales per month.
- **Output**: A line chart visualizing the average monthly sales for the past year.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements or bug fixes.

## License

This project is licensed under the MIT License.

---

For more detailed information and the latest updates, please refer to the [GitHub repository](https://github.com/Mr-Thop/SQL-And-Data-Visualisation-Agent). 