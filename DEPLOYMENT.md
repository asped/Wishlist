# 🚀 Deployment Guide

This guide will help you deploy the Family Gift List app to various platforms so it's accessible online.

## 🏠 Local Network Deployment

To make the app available to family members on your local network:

1. Start the app:
   ```bash
   python3 app.py
   ```

2. Find your local IP address:
   - **Linux/Mac**: `ifconfig` or `ip addr`
   - **Windows**: `ipconfig`

3. Share the URL with family members:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```
   
   Example: `http://192.168.1.100:5000`

> **Note**: Your firewall may need to allow incoming connections on port 5000

## ☁️ Cloud Deployment Options

### Option 1: PythonAnywhere (Easiest - Free Tier Available)

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a Bash console and clone/upload your project
3. Install dependencies:
   ```bash
   pip3 install --user -r requirements.txt
   ```
4. Configure a new web app:
   - Framework: Flask
   - Python version: 3.10
   - Source code: `/home/yourusername/your-project`
   - WSGI configuration: Point to `app.py`

5. Your app will be available at: `https://yourusername.pythonanywhere.com`

### Option 2: Heroku

1. Install Heroku CLI
2. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Add `gunicorn` to `requirements.txt`:
   ```bash
   echo "gunicorn==21.2.0" >> requirements.txt
   ```
4. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 3: Railway (Very Easy)

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect Flask and deploy
5. Your app will be available at a Railway-provided URL

### Option 4: Render (Free Tier Available)

1. Go to [render.com](https://render.com)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Deploy!

### Option 5: DigitalOcean App Platform

1. Create a DigitalOcean account
2. Use App Platform to deploy from GitHub
3. Select Python environment
4. Configure build and run commands
5. Deploy with one click

## 🔐 Production Considerations

Before deploying to production, update these settings in `app.py`:

1. **Change the Secret Key**:
   ```python
   app.config['SECRET_KEY'] = 'your-secure-random-secret-key-here'
   ```
   
   Generate a secure key:
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Disable Debug Mode**:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

3. **Use Environment Variables**:
   ```python
   import os
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
   ```

4. **Consider Adding Authentication** for the admin routes:
   ```python
   from flask_httpauth import HTTPBasicAuth
   # Add basic auth to admin routes
   ```

5. **Use a Production Database** (for platforms that restart frequently):
   - PostgreSQL
   - MySQL
   - Or use persistent storage for SQLite

## 🌐 Making it Accessible

### Custom Domain

Most platforms allow you to connect a custom domain:

1. Purchase a domain (e.g., from Namecheap, Google Domains)
2. Follow your hosting platform's instructions to connect it
3. Example: `familygifts.yourfamily.com`

### Sharing with Family

Once deployed, simply share the URL:
```
✉️ "Visit our family gift list at: https://your-app.com"
```

## 📱 Mobile Access

The app is already mobile-friendly! Family members can:
- Add it to their phone's home screen
- Bookmark it for easy access
- Use it just like any other website

## 🔄 Updating the App

After making changes:

1. **Local Network**: Just restart the app
2. **Cloud Platforms**: 
   - Push changes to GitHub
   - Most platforms auto-deploy
   - Or manually trigger deployment

## 💾 Database Backups

To backup your gift lists:

1. The database is stored in `wishlist.db`
2. Download it regularly from your hosting platform
3. Or set up automatic backups through your hosting provider

## 🆘 Troubleshooting

**App won't start:**
- Check Python version (needs 3.8+)
- Verify all dependencies are installed
- Check logs for error messages

**Can't access from other devices:**
- Check firewall settings
- Verify the correct IP address
- Ensure devices are on the same network (for local deployment)

**Database resets:**
- Make sure `wishlist.db` is in persistent storage
- Check if your hosting platform supports persistent files

## 📚 Additional Resources

- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)
- [SQLite in Production](https://www.sqlite.org/whentouse.html)
- Platform-specific documentation for your chosen host
