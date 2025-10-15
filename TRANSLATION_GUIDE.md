# 🌍 Internationalization (i18n) Guide

This guide explains how to manage translations for Slovak (SK) and Czech (CZ) languages in the Wishlist application.

## 📁 Translation Files Structure

```
translations/
├── sk/LC_MESSAGES/
│   ├── messages.po    # Slovak translations (editable)
│   └── messages.mo    # Compiled Slovak translations
└── cs/LC_MESSAGES/
    ├── messages.po    # Czech translations (editable)
    └── messages.mo    # Compiled Czech translations
```

## 🚀 Quick Start

### 1. Extract New Strings
When you add new translatable strings to templates or Python files:
```bash
./translate.sh extract
```

### 2. Update Translation Files
Update existing translation files with new strings:
```bash
./translate.sh update
```

### 3. Edit Translations
Edit the `.po` files in `translations/sk/LC_MESSAGES/` and `translations/cs/LC_MESSAGES/`:
- Fill in the `msgstr` fields with translations
- Keep `msgid` fields unchanged

### 4. Compile Translations
Compile the `.po` files to `.mo` files:
```bash
./translate.sh compile
```

### 5. Test
Restart the application and test the translations.

## 🔧 Translation Management Script

Use the `translate.sh` script for common translation tasks:

```bash
# Extract all translatable strings
./translate.sh extract

# Update existing translation files
./translate.sh update

# Compile translation files
./translate.sh compile

# Run full process (extract + update + compile)
./translate.sh full

# Initialize new language (if needed)
./translate.sh init-sk
./translate.sh init-cs
```

## 📝 Adding New Translatable Strings

### In Templates
Use the `gettext()` function:
```html
<h1>{{ gettext('Welcome to the App') }}</h1>
<p>{{ gettext('Please enter your password') }}</p>
```

### In Python Files
Import and use `gettext`:
```python
from flask_babel import gettext

# In forms
name = StringField(gettext('Name'), validators=[DataRequired()])

# In routes
flash(gettext('Login successful!'))
```

## 🌐 Language Switching

The application includes a language switcher in the navigation bar:
- **SK** - Slovak (default)
- **CZ** - Czech

Users can switch languages by clicking the language links in the top navigation.

## 🔄 Complete Workflow

1. **Add new strings** to templates/Python files using `gettext()`
2. **Extract strings**: `./translate.sh extract`
3. **Update translations**: `./translate.sh update`
4. **Edit translation files** in `translations/*/LC_MESSAGES/messages.po`
5. **Compile translations**: `./translate.sh compile`
6. **Test the application**

## 📋 Translation File Format

Each `.po` file contains entries like this:
```po
#: templates/login.html:10
msgid "Welcome to the App"
msgstr "Vitajte v aplikácii"

#: app.py:127
msgid "Login"
msgstr "Prihlásiť sa"
```

- `msgid` - Original string (don't change)
- `msgstr` - Translation (fill this in)
- Comments show where the string is used

## 🎯 Best Practices

1. **Keep translations consistent** - Use the same terms throughout
2. **Test both languages** - Make sure all strings are translated
3. **Use context** - Add comments in `.po` files for clarity
4. **Regular updates** - Update translations when adding new features
5. **Backup translations** - Keep copies of your `.po` files

## 🐛 Troubleshooting

### Translations not showing?
1. Check if `.mo` files exist and are up-to-date
2. Run `./translate.sh compile`
3. Restart the application
4. Clear browser cache

### Missing translations?
1. Run `./translate.sh extract` to find new strings
2. Run `./translate.sh update` to add them to translation files
3. Edit the `.po` files to add translations
4. Run `./translate.sh compile`

### Language switcher not working?
1. Check if the `set_language` route exists in `app.py`
2. Verify the language codes match (`sk`, `cs`)
3. Check if Flask-Babel is properly configured

## 📚 Additional Resources

- [Flask-Babel Documentation](https://flask-babel.tkte.ch/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)
- [Babel Documentation](https://babel.pocoo.org/)
