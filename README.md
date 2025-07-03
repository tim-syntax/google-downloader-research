# PDF Research Downloader

A modern, web-based PDF downloader tool that automatically searches and downloads PDF documents from Google search results based on customizable keywords and research fields.

## Features

- 🚀 **Web Interface**: Modern, responsive web application
- 📚 **Multiple Research Fields**: Pre-configured keywords for cybersecurity, AI, and more
- 🔧 **Customizable**: Add your own keywords and configure download settings
- 📊 **Real-time Status**: Monitor download progress and results
- 🛡️ **Anti-Detection**: Built-in mechanisms to avoid Google's bot detection
- 📁 **Organized Storage**: Automatic file organization by field and keyword
- ⚙️ **Configurable**: Environment-based configuration for easy deployment

## Project Structure

```
pdf-downloader/
├── app.py                 # Flask web application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── env_example.txt      # Environment variables example
├── google_Download.py   # Original script (for reference)
├── src/
│   ├── __init__.py
│   └── pdf_downloader.py # Core PDF downloader class
└── templates/
    └── index.html       # Web interface
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Git (for cloning)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/dreamjet31/pdf-research-google-downloade
   cd pdf-research-google-downloader
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   # Copy the example file
   cp env_example.txt .env

   # Edit .env with your settings
   nano .env
   ```

5. **Run the application**

   ```bash
   python app.py
   ```

6. **Access the web interface**
   Open your browser and go to: `http://localhost:5000`

## Configuration

### Environment Variables

Copy `env_example.txt` to `.env` and customize the settings:

```bash
# Application Settings
DEBUG=False
SECRET_KEY=your-secret-key-change-this-in-production

# Download Settings
MAX_PDF_PER_KEYWORD=200
MAX_PAGES_PER_SEARCH=3

# Timing Settings (in seconds)
MIN_SLEEP_TIME=2
MAX_SLEEP_TIME=5
PAGE_LOAD_TIMEOUT=10
REQUEST_TIMEOUT=15

# Browser Settings
HEADLESS_MODE=False
USER_AGENT_ROTATION=True

# File Storage
BASE_DOWNLOAD_DIR=downloads
```

### Adding Custom Keywords

You can add custom keywords in two ways:

1. **Through the web interface**: Use the "Custom Keywords" section
2. **In the configuration**: Edit `config.py` and add to `DEFAULT_FIELDS_KEYWORDS`

## Usage

### Web Interface

1. **Select Research Fields**: Choose from pre-configured fields or add custom keywords
2. **Configure Settings**: Adjust max PDFs per keyword and search pages
3. **Start Download**: Click "Start Download" to begin the process
4. **Monitor Progress**: Watch real-time status updates
5. **View Results**: See download statistics and results

### API Endpoints

- `GET /` - Main web interface
- `GET /api/fields` - Get available fields and keywords
- `POST /api/start-download` - Start download process
- `GET /api/download-status` - Get current download status
- `GET /api/downloads` - List downloaded files
- `GET /api/config` - Get current configuration
- `GET /api/health` - Health check

### Programmatic Usage

```python
from src.pdf_downloader import PDFDownloader
from config import Config

# Initialize downloader
downloader = PDFDownloader()

# Download for specific keywords
result = downloader.download_single_keyword(
    keyword="machine learning security",
    field_name="custom",
    max_pdfs=50
)

# Download for entire field
results = downloader.download_pdfs_for_field(
    field_name="cybersecurity",
    keywords=["network security", "data protection"],
    max_pdfs_per_keyword=100
)
```

## Deployment

### Local Development

```bash
python app.py
```

### Production Deployment

1. **Using Gunicorn**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Using Docker**

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   EXPOSE 5000

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

3. **Cloud Deployment**
   - **Heroku**: Add `Procfile` with `web: gunicorn app:app`
   - **AWS**: Use Elastic Beanstalk or EC2
   - **Google Cloud**: Use App Engine or Compute Engine
   - **Azure**: Use App Service

### Environment Variables for Production

```bash
DEBUG=False
SECRET_KEY=<generate-secure-random-key>
HEADLESS_MODE=True
USER_AGENT_ROTATION=True
```

## Security Considerations

- ⚠️ **Rate Limiting**: The tool includes random delays to avoid detection
- 🔒 **User Agent Rotation**: Automatically rotates user agents
- 🛡️ **Anti-Detection**: Built-in mechanisms to avoid Google's bot detection
- 📝 **Logging**: Comprehensive logging for monitoring and debugging

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**

   ```bash
   # Update Chrome browser
   # The tool automatically downloads the correct ChromeDriver version
   ```

2. **Robot Detection**

   - The tool will pause and wait for manual intervention
   - Complete the CAPTCHA and press Enter to continue

3. **Permission Errors**

   ```bash
   # Ensure write permissions to download directory
   chmod 755 downloads/
   ```

4. **Memory Issues**
   - Reduce `MAX_PDF_PER_KEYWORD` in configuration
   - Use `HEADLESS_MODE=True` for better performance

### Logs

Check the console output for detailed logs. The application provides real-time status updates through the web interface.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Please respect website terms of service and robots.txt files. The authors are not responsible for any misuse of this software.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs
3. Create an issue on GitHub
4. Contact the maintainers

---

**Happy Researching! 📚🔍**
