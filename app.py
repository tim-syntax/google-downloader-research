from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import threading
from datetime import datetime
from typing import Dict, List

from config import Config
from src.pdf_downloader import PDFDownloader

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Global variable to store download status
download_status = {
    'is_running': False,
    'progress': {},
    'results': {},
    'error': None,
    'captcha_detected': False,
    'captcha_message': None,
    'download_paused': False
}

# Global variable to store downloader instance
current_downloader = None

def run_download_task(fields_keywords: Dict[str, List[str]], custom_keywords: List[str] = None):
    """Run download task in background thread"""
    global download_status
    
    def update_status(status_updates):
        """Callback function to update global status"""
        global download_status
        download_status.update(status_updates)
    
    try:
        download_status['is_running'] = True
        download_status['progress'] = {}
        download_status['results'] = {}
        download_status['error'] = None
        download_status['captcha_detected'] = False
        download_status['captcha_message'] = None
        download_status['download_paused'] = False
        
        # Initialize downloader with status callback
        downloader = PDFDownloader(status_callback=update_status)
        
        # Store downloader instance globally
        global current_downloader
        current_downloader = downloader
        
        # Add custom keywords if provided
        if custom_keywords:
            fields_keywords['custom'] = custom_keywords
        
        # Start download process
        results = downloader.download_all_pdfs(fields_keywords)
        
        download_status['results'] = results
        download_status['is_running'] = False
        
        # Clean up downloader reference
        current_downloader = None
        
    except Exception as e:
        download_status['error'] = str(e)
        download_status['is_running'] = False
        current_downloader = None

@app.route('/')
def index():
    """Main page with download interface"""
    fields_keywords = Config.get_fields_keywords()
    return render_template('index.html', fields_keywords=fields_keywords)

@app.route('/api/start-download', methods=['POST'])
def start_download():
    """Start PDF download process"""
    global download_status
    
    if download_status['is_running']:
        return jsonify({'error': 'Download already in progress'}), 400
    
    try:
        data = request.get_json()
        fields_to_download = data.get('fields', [])
        custom_keywords = data.get('custom_keywords', [])
        max_pdfs = data.get('max_pdfs', Config.MAX_PDF_PER_KEYWORD)
        
        # Filter fields based on selection
        all_fields = Config.get_fields_keywords()
        selected_fields = {field: all_fields[field] for field in fields_to_download if field in all_fields}
        
        if not selected_fields and not custom_keywords:
            return jsonify({'error': 'No fields or keywords selected'}), 400
        
        # Start download in background thread
        thread = threading.Thread(
            target=run_download_task,
            args=(selected_fields, custom_keywords)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Download started successfully',
            'selected_fields': list(selected_fields.keys()),
            'custom_keywords_count': len(custom_keywords)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-status')
def get_download_status():
    """Get current download status"""
    return jsonify(download_status)

@app.route('/api/fields')
def get_fields():
    """Get available fields and keywords"""
    fields_keywords = Config.get_fields_keywords()
    return jsonify(fields_keywords)

@app.route('/api/downloads')
def list_downloads():
    """List all downloaded files"""
    try:
        download_path = Config.get_download_path()
        downloads = {}
        
        if os.path.exists(download_path):
            for field_dir in os.listdir(download_path):
                field_path = os.path.join(download_path, field_dir)
                if os.path.isdir(field_path):
                    downloads[field_dir] = {}
                    for keyword_dir in os.listdir(field_path):
                        keyword_path = os.path.join(field_path, keyword_dir)
                        if os.path.isdir(keyword_path):
                            pdf_files = [f for f in os.listdir(keyword_path) if f.endswith('.pdf')]
                            downloads[field_dir][keyword_dir] = {
                                'count': len(pdf_files),
                                'files': pdf_files
                            }
        
        return jsonify(downloads)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/downloads/<field>/<keyword>')
def download_files(field, keyword):
    """Download files for a specific field and keyword"""
    try:
        download_path = Config.get_download_path()
        keyword_path = os.path.join(download_path, field, keyword)
        
        if not os.path.exists(keyword_path):
            return jsonify({'error': 'Path not found'}), 404
        
        return send_from_directory(keyword_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    return jsonify({
        'max_pdf_per_keyword': Config.MAX_PDF_PER_KEYWORD,
        'max_pages_per_search': Config.MAX_PAGES_PER_SEARCH,
        'headless_mode': Config.HEADLESS_MODE,
        'user_agent_rotation': Config.USER_AGENT_ROTATION,
        'min_sleep_time': Config.MIN_SLEEP_TIME,
        'max_sleep_time': Config.MAX_SLEEP_TIME
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'download_running': download_status['is_running']
    })

@app.route('/api/resume-download', methods=['POST'])
def resume_download():
    """Resume download after CAPTCHA is solved"""
    global download_status, current_downloader
    
    if not download_status['captcha_detected']:
        return jsonify({'error': 'No CAPTCHA detected to resume from'}), 400
    
    if not current_downloader:
        return jsonify({'error': 'No active downloader found'}), 400
    
    try:
        # Call the downloader's resume method
        current_downloader.resume_download()
        
        # Reset CAPTCHA status
        download_status['captcha_detected'] = False
        download_status['captcha_message'] = None
        download_status['download_paused'] = False
        
        return jsonify({
            'message': 'Download resumed successfully',
            'status': 'resumed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-download', methods=['POST'])
def stop_download():
    """Stop the current download process"""
    global download_status, current_downloader
    
    if not download_status['is_running'] and not download_status['captcha_detected']:
        return jsonify({'error': 'No download in progress to stop'}), 400
    
    try:
        # Stop the downloader if it exists
        if current_downloader:
            current_downloader.stop_download()
            current_downloader = None
        
        # Update status to indicate download was stopped
        download_status['is_running'] = False
        download_status['captcha_detected'] = False
        download_status['captcha_message'] = None
        download_status['download_paused'] = False
        download_status['error'] = 'Download stopped by user'
        
        return jsonify({
            'message': 'Download stopped successfully',
            'status': 'stopped'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000) 