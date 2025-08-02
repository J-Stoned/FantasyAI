# Fantasy AI Ultimate - Merged Project Setup Guide

This guide will help you set up and run the merged Fantasy AI Ultimate project that combines the Fantasy AI Ultimate platform with the Yahoo Fantasy Wrapper.

## 🎯 Project Overview

This merged project combines:
- **Fantasy AI Ultimate**: AI-powered fantasy sports analysis platform
- **Yahoo Fantasy Wrapper**: Python wrapper for Yahoo Fantasy Sports API

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 16+** (for frontend components)
- **Git**
- **PostgreSQL** (optional, SQLite is used by default)
- **Redis** (optional, for caching)

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd merged-fantasy-project/fantasy-ai-merged
```

### 2. Set Up Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your configuration
# At minimum, you'll need Yahoo API credentials
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for frontend)
npm install
```

### 4. Configure Yahoo Fantasy API

1. Go to [Yahoo Developer Console](https://developer.yahoo.com/apps/)
2. Create a new application
3. Get your Client ID and Client Secret
4. Add them to your `.env` file:
   ```
   YAHOO_CLIENT_ID=your_client_id_here
   YAHOO_CLIENT_SECRET=your_client_secret_here
   ```

### 5. Run the Application

```bash
# Start the backend API
python scripts/start.py

# In another terminal, start the frontend (if available)
npm run dev
```

## 🔧 Configuration

### Environment Variables

Key environment variables you should configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `YAHOO_CLIENT_ID` | Yahoo API Client ID | Required |
| `YAHOO_CLIENT_SECRET` | Yahoo API Client Secret | Required |
| `DATABASE_URL` | Database connection string | SQLite |
| `REDIS_URL` | Redis connection string | Optional |
| `SECRET_KEY` | Application secret key | Auto-generated |
| `DEBUG` | Enable debug mode | false |

### Database Setup

The application uses SQLite by default for development. For production:

1. **PostgreSQL Setup**:
   ```bash
   # Install PostgreSQL
   # Create database
   createdb fantasy_ai_db
   
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/fantasy_ai_db
   ```

2. **Redis Setup** (optional, for caching):
   ```bash
   # Install Redis
   # Update REDIS_URL in .env
   REDIS_URL=redis://localhost:6379
   ```

## 📁 Project Structure

```
fantasy-ai-merged/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── shared/
│   │   ├── models.py          # Data models
│   │   ├── database.py        # Database manager
│   │   └── ai_engine.py       # AI analysis engine
│   ├── yahoo_wrapper/         # Yahoo Fantasy API wrapper
│   └── fantasy-ai/            # Fantasy AI components
├── config/
│   └── settings.py            # Configuration settings
├── scripts/
│   └── start.py               # Startup script
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies
└── README.md                 # Project documentation
```

## 🧪 Testing

Run the test suite:

```bash
# Run Python tests
pytest

# Run frontend tests
npm test
```

## 🔍 API Endpoints

Once running, the API provides these endpoints:

### Yahoo Fantasy Integration
- `GET /yahoo/leagues` - Get user's leagues
- `GET /yahoo/league/{league_id}` - Get league info
- `GET /yahoo/players/{league_id}` - Get league players

### AI Analysis
- `POST /ai/analyze-player` - Analyze player with AI
- `POST /ai/predict-performance` - Predict player performance
- `POST /ai/team-optimization` - Optimize team lineup

### Data Access
- `GET /data/players` - Get comprehensive player data
- `GET /data/league-stats` - Get league statistics

### Documentation
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure you're in the correct directory
   cd merged-fantasy-project/fantasy-ai-merged
   
   # Add src to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

2. **Database Connection Issues**:
   ```bash
   # Check if database file exists
   ls -la fantasy_ai.db
   
   # Remove and recreate if corrupted
   rm fantasy_ai.db
   python scripts/start.py
   ```

3. **Yahoo API Issues**:
   - Verify your Client ID and Secret are correct
   - Check that your Yahoo app has the correct permissions
   - Ensure your redirect URI matches the configuration

4. **Port Already in Use**:
   ```bash
   # Change port in .env file
   API_PORT=8001
   ```

### Logs

Check logs for detailed error information:

```bash
# View application logs
tail -f logs/fantasy_ai.log

# Check system logs
journalctl -u fantasy-ai -f
```

## 🔄 Development

### Adding New Features

1. **Backend Features**:
   - Add new endpoints in `src/main.py`
   - Create models in `src/shared/models.py`
   - Implement business logic in appropriate modules

2. **AI Features**:
   - Extend `src/shared/ai_engine.py`
   - Add new analysis types
   - Implement new prediction models

3. **Frontend Features**:
   - Add React components
   - Update API calls
   - Enhance UI/UX

### Code Style

```bash
# Format Python code
black src/

# Lint Python code
flake8 src/

# Format JavaScript/TypeScript
npm run format

# Lint JavaScript/TypeScript
npm run lint
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Yahoo Fantasy Sports API](https://developer.yahoo.com/fantasysports/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error details
3. Search existing issues
4. Create a new issue with detailed information

---

**Happy coding! 🏈⚽🏀** 