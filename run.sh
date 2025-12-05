#!/bin/bash

echo "----------------------------------------"
echo "🚀 MTJ Coders – ER Triage & Queue Manager"
echo "----------------------------------------"

# Auto-detect and activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
elif [ -d "env" ]; then
    echo "🔧 Activating virtual environment..."
    source env/bin/activate
else
    echo "❌ No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo "📦 Installing dependencies (if needed)..."
python3 -m pip install --upgrade pip
python3 -m pip install nicegui

echo "🚀 Starting ER Triage System..."
python3 main.py
