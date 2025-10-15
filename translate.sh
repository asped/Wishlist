#!/bin/bash

# Translation Management Script for Wishlist App
# This script helps manage translations for Slovak and Czech languages

echo "🌍 Wishlist Translation Management"
echo "=================================="

case "$1" in
    "extract")
        echo "📝 Extracting translatable strings..."
        pybabel extract -F babel.cfg -k gettext -o messages.pot .
        echo "✅ Extraction complete! Check messages.pot"
        ;;
    "update")
        echo "🔄 Updating translation files..."
        pybabel update -i messages.pot -d translations
        echo "✅ Translation files updated!"
        echo "📝 Please edit the .po files in translations/sk/LC_MESSAGES/ and translations/cs/LC_MESSAGES/"
        ;;
    "compile")
        echo "🔨 Compiling translation files..."
        pybabel compile -d translations
        echo "✅ Translation files compiled!"
        ;;
    "init-sk")
        echo "🇸🇰 Initializing Slovak translations..."
        pybabel init -i messages.pot -d translations -l sk
        echo "✅ Slovak translations initialized!"
        ;;
    "init-cs")
        echo "🇨🇿 Initializing Czech translations..."
        pybabel init -i messages.pot -d translations -l cs
        echo "✅ Czech translations initialized!"
        ;;
    "full")
        echo "🚀 Running full translation update process..."
        pybabel extract -F babel.cfg -k gettext -o messages.pot .
        pybabel update -i messages.pot -d translations
        pybabel compile -d translations
        echo "✅ Full translation process complete!"
        ;;
    *)
        echo "Usage: $0 {extract|update|compile|init-sk|init-cs|full}"
        echo ""
        echo "Commands:"
        echo "  extract  - Extract translatable strings to messages.pot"
        echo "  update   - Update existing translation files with new strings"
        echo "  compile  - Compile .po files to .mo files"
        echo "  init-sk  - Initialize Slovak translations"
        echo "  init-cs  - Initialize Czech translations"
        echo "  full     - Run extract + update + compile"
        echo ""
        echo "Workflow:"
        echo "  1. Make changes to templates/Python files"
        echo "  2. Run: $0 extract"
        echo "  3. Run: $0 update"
        echo "  4. Edit translation files in translations/*/LC_MESSAGES/"
        echo "  5. Run: $0 compile"
        echo "  6. Test the application"
        ;;
esac
