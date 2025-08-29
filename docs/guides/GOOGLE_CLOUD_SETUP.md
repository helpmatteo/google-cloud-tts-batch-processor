# 🔑 Google Cloud Setup Guide - Advanced TTS Batch Processor

## 🎯 **Overview**

This guide will walk you through setting up Google Cloud credentials for the TTS Batch Processor. This is **required** to use the text-to-speech functionality.

## ⚡ **Quick Setup (5 minutes)**

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create a New Project**
   - Click "Select a project" at the top
   - Click "New Project"
   - Enter a project name (e.g., "my-tts-project")
   - Click "Create"

### Step 2: Enable Text-to-Speech API

1. **Navigate to APIs & Services**
   - In your project, go to "APIs & Services" → "Library"

2. **Find and Enable the API**
   - Search for "Cloud Text-to-Speech API"
   - Click on it
   - Click "Enable"

### Step 3: Create Service Account

1. **Go to Credentials**
   - Navigate to "APIs & Services" → "Credentials"

2. **Create Service Account**
   - Click "Create Credentials" → "Service Account"
   - Enter service account name (e.g., "tts-service")
   - Click "Create and Continue"
   - Skip role assignment, click "Continue"
   - Click "Done"

### Step 4: Create API Key

1. **Access Service Account**
   - Click on your newly created service account

2. **Create Key**
   - Go to "Keys" tab
   - Click "Add Key" → "Create New Key"
   - Choose "JSON" format
   - Click "Create" (this downloads the key file)

### Step 5: Save Credentials

1. **Rename the file**
   - Rename the downloaded file to `google-credentials.json`

2. **Move to project directory**
   - Move the file to your TTS project directory
   - Ensure it's in the same folder as `tts_batch_processor.py`

## 🔧 **Detailed Setup Guide**

### Prerequisites

- Google account
- Web browser
- Basic computer skills

### Step-by-Step Instructions

#### 1. **Access Google Cloud Console**

1. Open your web browser
2. Go to: https://console.cloud.google.com
3. Sign in with your Google account
4. If you see a welcome screen, click "Get started for free"

#### 2. **Create a New Project**

1. Click "Select a project" at the top of the page
2. Click "New Project"
3. Enter a project name:
   - Use something descriptive like "my-tts-project"
   - Project names must be unique globally
4. Click "Create"
5. Wait for the project to be created

#### 3. **Enable Billing (Required)**

1. Google Cloud requires billing to be enabled
2. Click "Enable billing" when prompted
3. Follow the billing setup process
4. Don't worry - there's a generous free tier!

#### 4. **Enable Text-to-Speech API**

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Cloud Text-to-Speech API"
3. Click on the API
4. Click "Enable"
5. Wait for the API to be enabled

#### 5. **Create Service Account**

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the details:
   - **Service account name**: `tts-service` (or any name you prefer)
   - **Service account ID**: Will auto-generate
   - **Description**: "Service account for TTS processing"
4. Click "Create and Continue"
5. For "Grant this service account access to project":
   - Skip this step (click "Continue")
6. Click "Done"

#### 6. **Create and Download API Key**

1. Click on your newly created service account
2. Go to the "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose "JSON" format
5. Click "Create"
6. The JSON file will download automatically

#### 7. **Save and Secure the Credentials**

1. **Rename the file**:
   - Rename the downloaded file to `google-credentials.json`
   - Make sure it has a `.json` extension

2. **Move to project directory**:
   - Move the file to your TTS project directory
   - It should be in the same folder as your Python scripts

3. **Verify the file**:
   - The file should contain JSON with fields like:
     - `type`: "service_account"
     - `project_id`: Your project ID
     - `private_key_id`: A long string
     - `private_key`: A long private key
     - `client_email`: Your service account email

## 🔒 **Security Best Practices**

### Keep Credentials Secure

- **Never share** your credentials file
- **Don't commit** it to version control (it's already in `.gitignore`)
- **Store securely** on your local machine
- **Backup safely** if needed

### File Permissions

- Set appropriate file permissions (readable only by you)
- On Unix/Linux: `chmod 600 google-credentials.json`

### Environment Variables (Alternative)

Instead of a file, you can use environment variables:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google-credentials.json"
```

## 💰 **Cost Information**

### Free Tier

- **4 million characters per month** are free
- This is typically enough for testing and small projects
- No credit card required for free tier

### Paid Usage

- After free tier: ~$4 per 1 million characters
- Very cost-effective for most use cases
- You can set up billing alerts to control costs

### Cost Examples

- **1,000 sentences** (~20,000 characters): **FREE**
- **10,000 sentences** (~200,000 characters): **FREE**
- **100,000 sentences** (~2 million characters): **FREE**
- **200,000 sentences** (~4 million characters): **FREE**

## 🧪 **Testing Your Setup**

### Quick Test

1. Run the setup wizard:
   ```bash
   python setup_wizard.py
   ```

2. Select "I have credentials file" when prompted

3. Provide the path to your `google-credentials.json`

4. The wizard will validate your credentials

### Test with Sample Data

1. Run the main processor:
   ```bash
   python tts_batch_processor.py examples_en.txt --credentials google-credentials.json --max-sentences 3
   ```

2. Check that audio files are generated in the output directory

## 🚨 **Troubleshooting**

### Common Issues

#### "File not found" error
- Ensure the credentials file is in the correct location
- Check the file path is correct
- Verify the file has a `.json` extension

#### "Invalid credentials" error
- Ensure you downloaded the JSON key (not the P12 key)
- Check that the file contains valid JSON
- Verify all required fields are present

#### "API not enabled" error
- Go to Google Cloud Console
- Navigate to "APIs & Services" → "Library"
- Search for "Cloud Text-to-Speech API"
- Click "Enable"

#### "Billing not enabled" error
- Enable billing in your Google Cloud project
- The free tier is available even with billing enabled

### Getting Help

1. **Check the setup wizard**: `python setup_wizard.py`
2. **Run the launcher**: `python launch.py`
3. **Use smart CLI**: `python smart_cli.py`
4. **Check documentation**: README.md and other guides

## 🎉 **Next Steps**

Once you have your credentials set up:

1. **Run the setup wizard** to configure preferences:
   ```bash
   python setup_wizard.py
   ```

2. **Try the web interface**:
   ```bash
   python start_web_interface.py
   ```

3. **Process your first sentences**:
   ```bash
   python tts_batch_processor.py examples_en.txt --credentials google-credentials.json
   ```

4. **Explore all features**:
   ```bash
   python demo.py
   ```

## 📞 **Support**

If you encounter issues:

1. Check this guide first
2. Run the setup wizard for guided help
3. Check the troubleshooting section above
4. Review the main README.md file

**Happy Text-to-Speech Processing! 🎤✨**
