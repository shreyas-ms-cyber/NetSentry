#!/usr/bin/env python3
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = "postgresql://neondb_owner:npg_LAkZPgOJ73Ve@ep-shiny-lab-ayqht9jl-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    parsed = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        user=parsed.username,
        password=parsed.password,
        dbname=parsed.path.lstrip('/'),
        sslmode='require'
    )
    cur = conn.cursor()
    
    # Check all columns
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='traffic_stats'
        ORDER BY ordinal_position
    """)
    
    print("📊 Columns in traffic_stats:")
    for col in cur.fetchall():
        print(f"  - {col[0]} ({col[1]})")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
