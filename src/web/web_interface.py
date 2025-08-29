#!/usr/bin/env python3
"""
Web Interface for Advanced TTS Batch Processor
Provides a user-friendly web interface for TTS processing
"""

from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
import threading
import queue
from typing import Dict, Any, List
import uuid

# Import our TTS processor
from ..core.tts_batch_processor import AdvancedTTSProcessor
from ..core.config_manager import ConfigManager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global configuration
config_manager = ConfigManager()
active_jobs = {}  # Store active processing jobs
job_queue = queue.Queue()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced TTS Batch Processor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        textarea {
            height: 150px;
            resize: vertical;
        }
        .btn {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .btn-secondary {
            background-color: #6c757d;
        }
        .btn-secondary:hover {
            background-color: #545b62;
        }
        .progress {
            width: 100%;
            height: 20px;
            background-color: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-bar {
            height: 100%;
            background-color: #007bff;
            transition: width 0.3s ease;
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .results {
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .file-list {
            list-style: none;
            padding: 0;
        }
        .file-list li {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .download-btn {
            background-color: #28a745;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        .download-btn:hover {
            background-color: #218838;
        }
        .quick-actions {
            margin-top: 20px;
        }
        .quick-actions .btn {
            margin: 5px;
            font-size: 14px;
            padding: 8px 16px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-indicator.ready {
            background-color: #28a745;
        }
        .status-indicator.processing {
            background-color: #ffc107;
            animation: pulse 1s infinite;
        }
        .status-indicator.error {
            background-color: #dc3545;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .feature-highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
        .feature-highlight h3 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }
        .feature-highlight p {
            margin: 0;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Advanced TTS Batch Processor</h1>
            <p>High-performance text-to-speech processing with Google Cloud</p>
            <div class="quick-actions">
                <button class="btn btn-secondary" onclick="loadExample('en')">Load English Example</button>
                <button class="btn btn-secondary" onclick="loadExample('ja')">Load Japanese Example</button>
                <button class="btn btn-secondary" onclick="loadExample('es')">Load Spanish Example</button>
                <button class="btn btn-secondary" onclick="clearForm()">Clear All</button>
            </div>
        </div>

        <div class="feature-highlight">
            <h3>🚀 Quick Start</h3>
            <p>Click the buttons above to load example text, or paste your own sentences below</p>
        </div>

        <form id="ttsForm">
            <div class="form-group">
                <label for="textInput">
                    <span class="status-indicator ready"></span>
                    Text to Process (one sentence per line):
                </label>
                <textarea id="textInput" name="text" placeholder="Enter your text here, one sentence per line...&#10;&#10;Example:&#10;Hello, how are you today?&#10;The weather is beautiful this morning.&#10;I love learning new languages."></textarea>
            </div>

            <div class="form-group">
                <label for="language">Language:</label>
                <select id="language" name="language">
                    <option value="en-US">English (US)</option>
                    <option value="ja-JP">Japanese</option>
                    <option value="es-ES">Spanish (Spain)</option>
                    <option value="fr-FR">French</option>
                    <option value="de-DE">German</option>
                </select>
            </div>

            <div class="form-group">
                <label for="voice">Voice (when rotation disabled):</label>
                <select id="voice" name="voice">
                    <option value="en-US-Neural2-A">en-US-Neural2-A (Female)</option>
                    <option value="en-US-Neural2-C">en-US-Neural2-C (Male)</option>
                    <option value="en-US-Neural2-D">en-US-Neural2-D (Female)</option>
                    <option value="en-US-Neural2-E">en-US-Neural2-E (Male)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="format">Audio Format:</label>
                <select id="format" name="format">
                    <option value="MP3">MP3 (Recommended)</option>
                    <option value="WAV">WAV</option>
                    <option value="OGG">OGG</option>
                    <option value="FLAC">FLAC</option>
                </select>
            </div>

            <div class="form-group">
                <label for="sampleRate">Sample Rate:</label>
                <select id="sampleRate" name="sampleRate">
                    <option value="24000">24,000 Hz (Recommended)</option>
                    <option value="16000">16,000 Hz</option>
                    <option value="48000">48,000 Hz</option>
                </select>
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" id="voiceRotation" name="voiceRotation" checked>
                    Enable Voice Rotation
                </label>
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" id="caching" name="caching" checked>
                    Enable Caching
                </label>
            </div>

                            <button type="submit" class="btn" id="submitBtn">🚀 Start Processing</button>
                <button type="button" class="btn btn-secondary" onclick="clearForm()">🗑️ Clear</button>
                <button type="button" class="btn btn-secondary" onclick="showTips()">💡 Tips</button>
        </form>

        <div id="progressSection" style="display: none;">
            <h3>Processing Progress</h3>
            <div class="progress">
                <div class="progress-bar" id="progressBar" style="width: 0%"></div>
            </div>
            <div id="progressText">Initializing...</div>
            <div id="status" class="status info">Processing started...</div>
        </div>

        <div id="resultsSection" style="display: none;">
            <div class="results">
                <h3>Processing Results</h3>
                <div id="resultsContent"></div>
            </div>
        </div>
    </div>

                <script>
                let currentJobId = null;
                
                // Example texts
                const examples = {
                    'en': `Hello, how are you today?
The weather is beautiful this morning.
I love learning new languages.
Technology makes our lives easier.
Have a wonderful day!`,
                    'ja': `こんにちは、お元気ですか？
今日は良い天気ですね。
新しい言語を学ぶのが大好きです。
テクノロジーは私たちの生活を便利にします。
素晴らしい一日をお過ごしください！`,
                    'es': `¡Hola! ¿Cómo estás hoy?
El clima está hermoso esta mañana.
Me encanta aprender nuevos idiomas.
La tecnología hace nuestras vidas más fáciles.
¡Que tengas un día maravilloso!`
                };

                        // Load example text
                function loadExample(lang) {
                    document.getElementById('textInput').value = examples[lang] || '';
                    document.getElementById('language').value = lang === 'ja' ? 'ja-JP' : lang === 'es' ? 'es-ES' : 'en-US';
                    updateVoiceOptions();
                }
                
                // Show tips
                function showTips() {
                    alert(`💡 Tips for Best Results:

1. 📝 One sentence per line for best results
2. 🌍 Match language with text content
3. 🎵 Enable voice rotation for variety
4. 💾 Use caching for faster repeat processing
5. 🎯 Keep sentences under 500 characters
6. 📁 Use MP3 format for compatibility
7. ⚡ Use 24kHz sample rate for good quality/size balance

Need help? Check the documentation or run the setup wizard!`);
                }
                
                // Update voice options when language changes
                function updateVoiceOptions() {
                    const language = document.getElementById('language').value;
                    const voiceSelect = document.getElementById('voice');
                    
                    // Clear current options
                    voiceSelect.innerHTML = '';
                    
                    // Add new options based on language
                    const voices = {
                        'en-US': [
                            'en-US-Neural2-A', 'en-US-Neural2-C', 'en-US-Neural2-D', 'en-US-Neural2-E',
                            'en-US-Neural2-F', 'en-US-Neural2-G', 'en-US-Neural2-H', 'en-US-Neural2-I', 'en-US-Neural2-J'
                        ],
                        'ja-JP': ['ja-JP-Neural2-B', 'ja-JP-Neural2-C', 'ja-JP-Neural2-D', 'ja-JP-Neural2-E'],
                        'es-ES': ['es-ES-Neural2-A', 'es-ES-Neural2-B', 'es-ES-Neural2-C', 'es-ES-Neural2-D'],
                        'fr-FR': ['fr-FR-Neural2-A', 'fr-FR-Neural2-B', 'fr-FR-Neural2-C', 'fr-FR-Neural2-D'],
                        'de-DE': ['de-DE-Neural2-A', 'de-DE-Neural2-B', 'de-DE-Neural2-C', 'de-DE-Neural2-D']
                    };
                    
                    voices[language].forEach(voice => {
                        const option = document.createElement('option');
                        option.value = voice;
                        option.textContent = voice;
                        voiceSelect.appendChild(option);
                    });
                }
                
                document.getElementById('ttsForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                text: formData.get('text'),
                language: formData.get('language'),
                voice: formData.get('voice'),
                format: formData.get('format'),
                sampleRate: parseInt(formData.get('sampleRate')),
                voiceRotation: formData.get('voiceRotation') === 'on',
                caching: formData.get('caching') === 'on'
            };

                                // Show progress section
                    document.getElementById('progressSection').style.display = 'block';
                    document.getElementById('resultsSection').style.display = 'none';
                    
                    // Update status indicator
                    document.querySelector('.status-indicator').className = 'status-indicator processing';
                    
                    // Disable submit button
                    document.getElementById('submitBtn').disabled = true;
                    document.getElementById('submitBtn').textContent = '⏳ Processing...';

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                
                if (result.success) {
                    currentJobId = result.job_id;
                    document.getElementById('status').className = 'status info';
                    document.getElementById('status').textContent = 'Processing started...';
                    
                    // Start polling for progress
                    pollProgress();
                                        } else {
                            document.getElementById('status').className = 'status error';
                            document.getElementById('status').textContent = 'Error: ' + result.error;
                            
                            // Reset status indicator and button
                            document.querySelector('.status-indicator').className = 'status-indicator error';
                            document.getElementById('submitBtn').disabled = false;
                            document.getElementById('submitBtn').textContent = '🚀 Start Processing';
                        }
            } catch (error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        });

        async function pollProgress() {
            if (!currentJobId) return;

            try {
                const response = await fetch(`/api/status/${currentJobId}`);
                const result = await response.json();

                                        if (result.status === 'completed') {
                            document.getElementById('progressBar').style.width = '100%';
                            document.getElementById('progressText').textContent = 'Processing completed!';
                            document.getElementById('status').className = 'status success';
                            document.getElementById('status').textContent = 'Processing completed successfully!';
                            
                            // Reset status indicator and button
                            document.querySelector('.status-indicator').className = 'status-indicator ready';
                            document.getElementById('submitBtn').disabled = false;
                            document.getElementById('submitBtn').textContent = '🚀 Start Processing';
                    
                    // Show results
                    showResults(result.results);
                                        } else if (result.status === 'failed') {
                            document.getElementById('status').className = 'status error';
                            document.getElementById('status').textContent = 'Processing failed: ' + result.error;
                            
                            // Reset status indicator and button
                            document.querySelector('.status-indicator').className = 'status-indicator error';
                            document.getElementById('submitBtn').disabled = false;
                            document.getElementById('submitBtn').textContent = '🚀 Start Processing';
                } else {
                    // Update progress
                    const progress = (result.processed / result.total) * 100;
                    document.getElementById('progressBar').style.width = progress + '%';
                    document.getElementById('progressText').textContent = 
                        `Processed ${result.processed} of ${result.total} sentences (${progress.toFixed(1)}%)`;
                    
                    // Continue polling
                    setTimeout(pollProgress, 1000);
                }
            } catch (error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = 'Error checking progress: ' + error.message;
            }
        }

        function showResults(results) {
            const resultsSection = document.getElementById('resultsSection');
            const resultsContent = document.getElementById('resultsContent');
            
            resultsContent.innerHTML = `
                <p><strong>Total:</strong> ${results.total} sentences</p>
                <p><strong>Successful:</strong> ${results.successful} sentences</p>
                <p><strong>Failed:</strong> ${results.failed} sentences</p>
                <p><strong>Success Rate:</strong> ${((results.successful / results.total) * 100).toFixed(1)}%</p>
                <p><strong>Processing Time:</strong> ${results.processing_time.toFixed(2)} seconds</p>
                
                <h4>Generated Files:</h4>
                <ul class="file-list">
                    ${results.files.map(file => `
                        <li>
                            ${file.sentence.substring(0, 50)}...
                            <button class="download-btn" onclick="downloadFile('${file.filepath}')">Download</button>
                        </li>
                    `).join('')}
                </ul>
            `;
            
            resultsSection.style.display = 'block';
        }

        async function downloadFile(filepath) {
            try {
                const response = await fetch(`/api/download/${encodeURIComponent(filepath)}`);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filepath.split('/').pop();
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                alert('Error downloading file: ' + error.message);
            }
        }

                        function clearForm() {
                    document.getElementById('ttsForm').reset();
                    document.getElementById('progressSection').style.display = 'none';
                    document.getElementById('resultsSection').style.display = 'none';
                    
                    // Reset status indicator
                    document.querySelector('.status-indicator').className = 'status-indicator ready';
                    
                    // Reset button
                    document.getElementById('submitBtn').disabled = false;
                    document.getElementById('submitBtn').textContent = '🚀 Start Processing';
                }

                        // Initialize voice options
                updateVoiceOptions();
                
                // Update voice options when language changes
                document.getElementById('language').addEventListener('change', updateVoiceOptions);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/process', methods=['POST'])
def process_tts():
    """Process TTS request"""
    try:
        data = request.json
        
        # Validate input
        if not data.get('text'):
            return jsonify({'success': False, 'error': 'No text provided'})
        
        # Create temporary file for text
        sentences = [line.strip() for line in data['text'].split('\n') if line.strip()]
        if not sentences:
            return jsonify({'success': False, 'error': 'No valid sentences found'})
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create job info
        job_info = {
            'id': job_id,
            'status': 'processing',
            'total': len(sentences),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now(),
            'results': None,
            'error': None
        }
        
        active_jobs[job_id] = job_info
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_job,
            args=(job_id, sentences, data)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Processing started'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def process_job(job_id: str, sentences: List[str], config: Dict[str, Any]):
    """Process TTS job in background thread"""
    try:
        # Create temporary output directory
        output_dir = Path(f"temp_output_{job_id}")
        output_dir.mkdir(exist_ok=True)
        
        # Create processor configuration
        from ..core.tts_batch_processor import UltraProcessingConfig
        
        processor_config = UltraProcessingConfig(
            voice_name=config.get('voice', 'en-US-Neural2-A'),
            audio_format=config.get('format', 'MP3'),
            sample_rate=config.get('sampleRate', 24000),
            enable_caching=config.get('caching', True),
            voice_rotation_enabled=config.get('voiceRotation', True)
        )
        
        # Initialize processor
        processor = AdvancedTTSProcessor(
            credentials_path=os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-credentials.json'),
            output_dir=str(output_dir),
            config=processor_config,
            language_code=config.get('language', 'en-US')
        )
        
        # Process sentences
        results = processor.process_batch_ultra(sentences)
        
        # Update job status
        active_jobs[job_id]['status'] = 'completed'
        active_jobs[job_id]['results'] = results
        active_jobs[job_id]['processed'] = results['total']
        active_jobs[job_id]['successful'] = results['successful']
        active_jobs[job_id]['failed'] = results['failed']
        
    except Exception as e:
        active_jobs[job_id]['status'] = 'failed'
        active_jobs[job_id]['error'] = str(e)

@app.route('/api/status/<job_id>')
def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = active_jobs[job_id]
    
    if job['status'] == 'completed':
        return jsonify({
            'status': 'completed',
            'total': job['total'],
            'processed': job['processed'],
            'successful': job['successful'],
            'failed': job['failed'],
            'results': job['results']
        })
    elif job['status'] == 'failed':
        return jsonify({
            'status': 'failed',
            'error': job['error']
        })
    else:
        return jsonify({
            'status': 'processing',
            'total': job['total'],
            'processed': job.get('processed', 0)
        })

@app.route('/api/download/<path:filepath>')
def download_file(filepath: str):
    """Download generated audio file"""
    try:
        file_path = Path(filepath)
        if file_path.exists():
            return send_file(str(file_path), as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    return jsonify(config_manager.config)

@app.route('/api/languages')
def get_languages():
    """Get available languages"""
    languages = config_manager.config.get('languages', {})
    return jsonify(languages)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
