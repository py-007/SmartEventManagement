#!/bin/bash
# ══════════════════════════════════════════════
# EMS — One-Command Setup Script
# ══════════════════════════════════════════════
set -e

echo "🚀 Setting up Event Management System..."
echo ""

# 1. Create virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# 2. Activate
source venv/bin/activate

# 3. Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# 4. Apply migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# 5. Seed demo data
echo "🌱 Seeding demo data..."
python manage.py seed_data

# 6. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "  🔐 Demo Accounts:"
echo "  ┌─────────────────────────────────────────┐"
echo "  │  admin      / admin123   → Admin         │"
echo "  │  alice_mgr  / manager123 → Event Manager │"
echo "  │  bob_mgr    / manager123 → Event Manager │"
echo "  │  john_doe   / attendee123→ Attendee       │"
echo "  └─────────────────────────────────────────┘"
echo ""
echo "  🌐 Start the server:"
echo "  python manage.py runserver"
echo ""
echo "  Then open: http://127.0.0.1:8000"
echo ""
