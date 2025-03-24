# Natural Language to SQL Assistant (Frontend)

A React-based frontend for converting natural language queries to SQL. Connects to a MySQL database and executes queries via a Flask backend.

## Features
- Database connection management
- Natural language to SQL conversion
- Query execution with results display
- State tracking (START, INPUT, PROCESS, OBSERVATION, OUTPUT, STOP)
- Error handling and validation

## Prerequisites
- Node.js (v16+)
- npm (v7+)
- Running Flask backend (port 5000)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/your-username/natural-language-sql-assistant.git
cd natural-language-sql-assistant/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```env
REACT_APP_BACKEND_URL=http://localhost:5000
```

## Available Scripts
```bash
npm start    # Starts development server
npm test     # Runs tests
npm run build # Creates production build
```

## API Endpoints
### Connect to Database
```bash
POST /api/connect
{
  "host": "localhost",
  "user": "root",
  "password": "password",
  "database": "test_db",
  "port": 3306
}
```

### Execute Query
```bash
POST /api/query 
{
  "query": "Show active users with their order counts"
}
```

## Folder Structure
```
frontend/
├── public
├── src
│   ├── components
│   ├── App.js
│   ├── App.css
│   └── index.js
├── package.json
└── README.md
```

## Troubleshooting
- **Connection Issues**: Verify backend is running and CORS configured
- **Missing Modules**: Delete `node_modules` and run `npm install`
- **Query Errors**: Check browser console and backend logs

## License
MIT License
