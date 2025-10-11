# 🎁 Family Gift List

A simple and senior-friendly gift list web application perfect for families! Parents can create gift lists for their children, and family members (like grandparents) can easily see what's available and mark gifts as purchased.

## ✨ Features

- **Simple, Clear Interface**: Large text, obvious buttons, and clear status indicators designed for ease of use
- **Public Gift Lists**: Anyone can view gift lists and mark items as purchased by entering their name
- **Admin Dashboard**: Easy-to-use CRUD interface for managing children and their gift lists
- **Real-time Status**: Clear visual feedback showing which gifts are available vs. purchased
- **No Login Required**: Public access makes it easy for everyone to participate

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation & Running

#### Option 1: Quick Start (Easiest)

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

These scripts will automatically install dependencies and start the server!

#### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```
   
   Or on some systems:
   ```bash
   python3 app.py
   ```

3. **Open in Browser**
   
   The app will start on `http://localhost:5000`

   - **Public Gift Lists**: `http://localhost:5000/`
   - **Admin Dashboard**: `http://localhost:5000/admin`

## 📖 How to Use

### For Parents (Admin)

1. Go to the **Admin Dashboard** (`/admin`)
2. Click **"+ Add New Child"** to add your children
3. For each child, click **"Manage Gifts"** to add gift ideas
4. Fill in gift details including name, description, and optional link to where it can be purchased

### For Gift Buyers (Grandparents, Family)

1. Go to the homepage to see all children
2. Click on a child's name to see their gift list
3. Browse available gifts (marked in **green**)
4. When you want to buy a gift:
   - Enter your name in the form
   - Click **"I Will Buy This Gift"**
   - The gift will be marked as **PURCHASED** (shown in gray)
5. If you made a mistake, click **"Undo Purchase"**

## 🎨 Design Features for Seniors

- **Extra Large Text**: Easy to read font sizes (18px+ base)
- **High Contrast Colors**: Clear distinction between available (green) and purchased (gray) gifts
- **Big Buttons**: Large, obvious click targets
- **Simple Navigation**: Minimal steps to accomplish any task
- **Clear Confirmations**: Prompts before important actions to prevent mistakes
- **No Complex Interactions**: Straightforward forms with clear labels

## 📁 Project Structure

```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── wishlist.db            # SQLite database (created automatically)
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html         # Homepage with children list
│   ├── child_gifts.html   # Gift list for a child
│   └── admin/             # Admin templates
│       ├── dashboard.html
│       ├── child_form.html
│       ├── gift_form.html
│       └── gifts.html
└── static/
    └── css/
        └── style.css      # Styling with large, clear UI elements

```

## 🔒 Security Note

This is a simple family app designed for trusted users. For production use, consider adding:
- Authentication for admin routes
- CSRF protection
- Rate limiting
- Environment-based secret keys

## 🛠️ Customization

### Change the Port

Edit `app.py` and modify the last line:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change 5000 to your preferred port
```

### Change the Database Location

Edit `app.py` and modify:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path/to/your/database.db'
```

## 💡 Tips

- The database file (`wishlist.db`) is created automatically on first run
- All gift statuses are saved in the database
- You can reset everything by deleting `wishlist.db` and restarting the app
- The app works great on mobile devices too!

## 🤝 Support

Perfect for family gatherings, holidays, and birthdays. Share the URL with your family members and make gift-giving easier for everyone!
