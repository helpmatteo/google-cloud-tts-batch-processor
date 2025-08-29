#!/bin/bash

# Advanced Text-to-Speech Batch Processor Installation Script

echo "🚀 Installing Advanced Text-to-Speech Batch Processor..."
echo ""

# Check if Python 3.7+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version detected (>= $required_version required)"
else
    echo "❌ Python 3.7+ is required. Please install Python 3.7 or higher."
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies. Please check your Python environment."
    exit 1
fi

# Create example credentials file
echo ""
echo "🔑 Setting up Google Cloud credentials..."
if [ ! -f "google-credentials.json" ]; then
    echo "📝 Creating example credentials file..."
    cat > google-credentials-example.json << EOF
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
}
EOF
    echo "✅ Example credentials file created: google-credentials-example.json"
    echo "⚠️  Please replace with your actual Google Cloud credentials"
else
    echo "✅ Google Cloud credentials file already exists"
fi

# Test the installation
echo ""
echo "🧪 Testing installation..."
python3 -c "import google.cloud.texttospeech; print('✅ Google Cloud TTS library imported successfully')"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "📖 Next steps:"
    echo "1. Set up your Google Cloud credentials (see README.md)"
    echo "2. Test with a small batch: python3 tts_batch_processor.py examples_en.txt --credentials google-credentials.json --max-sentences 5"
    echo "3. Check the documentation in README.md for advanced usage"
    echo ""
    echo "Happy Text-to-Speech Processing! 🎤✨"
else
    echo "❌ Installation test failed. Please check your setup."
    exit 1
fi
