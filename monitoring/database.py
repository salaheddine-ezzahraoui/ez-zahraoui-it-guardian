import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL
import traceback

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_active_assets():
    """Get all active assets from the database"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, hostname, ip_address, asset_type, status, production_line, criticality
        FROM assets
        WHERE is_active = TRUE
    """)
    assets = cur.fetchall()
    cur.close()
    conn.close()
    return assets

def save_monitoring_result(asset_id, check_type, result, response_time_ms=None, packet_loss=None, status_code=None, message=None):
    """Save a monitoring result to the database"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Convert to uppercase for database enum
        check_type_enum = check_type.upper()
        result_enum = result.upper()
        cur.execute("""
            INSERT INTO monitoring_results (asset_id, check_type, result, response_time_ms, packet_loss_percent, status_code, message)
            VALUES (%s, %s::checktype, %s::checkresult, %s, %s, %s, %s)
        """, (asset_id, check_type_enum, result_enum, response_time_ms, packet_loss, status_code, message))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Error saving monitoring result: {e}")
        traceback.print_exc()

def update_asset_status(asset_id, status):
    """Update an asset's status"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        status_enum = status.upper()
        cur.execute("""
            UPDATE assets
            SET status = %s::assetstatus, last_check = NOW()
            WHERE id = %s
        """, (status_enum, asset_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Error updating asset status: {e}")
        traceback.print_exc()

def create_event(event_type, message):
    """Create an event log entry"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (event_type, message)
            VALUES (%s::eventtype, %s)
        """, (event_type.upper(), message))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB] Error creating event: {e}")
        traceback.print_exc()

def create_incident(asset_id, category, severity, priority, title, description):
    """Create an incident if one doesn't already exist for this asset"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if there's already an active incident for this asset
        cur.execute("""
            SELECT id FROM incidents
            WHERE asset_id = %s AND status IN ('OPEN', 'INVESTIGATING', 'IN_PROGRESS')
            LIMIT 1
        """, (asset_id,))
        
        if cur.fetchone():
            cur.close()
            conn.close()
            return None
        
        # Generate incident ID
        cur.execute("SELECT COUNT(*) FROM incidents")
        count = cur.fetchone()['count']
        incident_id = f"INC-{1043 + count}"
        
        cur.execute("""
            INSERT INTO incidents (incident_id, asset_id, category, severity, priority, status, title, description)
            VALUES (%s, %s, %s::incidentcategory, %s::incidentseverity, %s::incidentpriority, %s::incidentstatus, %s, %s)
        """, (incident_id, asset_id, category.upper(), severity.upper(), priority.upper(), 'OPEN', title, description))
        
        conn.commit()
        cur.close()
        conn.close()
        return incident_id
    except Exception as e:
        print(f"[DB] Error creating incident: {e}")
        traceback.print_exc()
        return None