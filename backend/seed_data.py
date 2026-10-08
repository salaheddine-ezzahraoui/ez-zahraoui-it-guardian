from app.database import SessionLocal
from app.models.asset import Asset, AssetType, AssetStatus, CriticalityLevel
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus, IncidentPriority
from app.models.event import Event, EventType
from datetime import datetime, timedelta
import random
import socket

def get_local_ip():
    """Get the local machine's IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def seed_database():
    db = SessionLocal()
    local_ip = get_local_ip()
    base_ip = ".".join(local_ip.split(".")[:3])
    
    print(f"Using base IP: {base_ip}.x for assets")
    print(f"Local IP: {local_ip}")

    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Incident).delete()
        db.query(Event).delete()
        db.query(Asset).delete()
        db.commit()

        print("Seeding database with demo data...")

        # Create Production PCs - use different IPs in local subnet
        production_lines = ["Line 1", "Line 2", "Line 3", "Line 4"]
        locations = ["Workshop A", "Workshop B", "Workshop C", "Assembly Hall"]

        ip_counter = 100
        for i in range(1, 46):
            # Use different IPs in the local subnet range
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            
            asset = Asset(
                hostname=f"PROD-PC-{i:03d}",
                ip_address=ip,
                mac_address=f"00:1A:2B:3C:{i:02X}:{i:02X}",
                asset_type=AssetType.PRODUCTION_PC,
                operating_system="Windows 10 IoT Enterprise",
                location=random.choice(locations),
                production_line=random.choice(production_lines),
                status=AssetStatus.ONLINE,
                owner_team="Production IT",
                criticality=CriticalityLevel.HIGH,
                description=f"Production workstation {i} on {random.choice(production_lines)}",
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 30)),
            )
            db.add(asset)

        # Create Servers - use unique IPs
        servers = [
            ("SRV-AD-01", "Windows Server 2022", "Active Directory, DNS, DHCP"),
            ("SRV-ERP-01", "Windows Server 2022", "ERP System"),
            ("SRV-MES-01", "Windows Server 2022", "MES System"),
            ("SRV-FILE-01", "Windows Server 2022", "File Server"),
            ("SRV-BACKUP-01", "Ubuntu Server 22.04", "Backup Server"),
            ("SRV-DB-01", "Ubuntu Server 22.04", "PostgreSQL Database"),
            ("SRV-WEB-01", "Ubuntu Server 22.04", "Web Application"),
            ("SRV-MON-01", "Ubuntu Server 22.04", "Monitoring Server"),
        ]

        for idx, (hostname, os, desc) in enumerate(servers):
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            asset = Asset(
                hostname=hostname,
                ip_address=ip,
                mac_address=f"00:1A:2B:4D:{random.randint(10,99):02X}:{random.randint(10,99):02X}",
                asset_type=AssetType.SERVER,
                operating_system=os,
                location="Server Room",
                production_line=None,
                status=AssetStatus.ONLINE,
                owner_team="Infrastructure Team",
                criticality=CriticalityLevel.CRITICAL,
                description=desc,
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 10)),
            )
            db.add(asset)

        # Create Switches - use unique IPs
        for i in range(1, 13):
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            asset = Asset(
                hostname=f"SW-ACCESS-{i:02d}",
                ip_address=ip,
                mac_address=f"00:1A:2B:5E:{i:02X}:{i:02X}",
                asset_type=AssetType.SWITCH,
                operating_system="Cisco IOS 15.2",
                location=f"Network Cabinet {i}",
                production_line=None,
                status=AssetStatus.ONLINE,
                owner_team="Network Team",
                criticality=CriticalityLevel.HIGH,
                description=f"Access switch {i} - VLAN configuration",
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 15)),
            )
            db.add(asset)

        # Create Routers - use unique IPs
        for i in range(1, 5):
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            asset = Asset(
                hostname=f"RT-CORE-{i:02d}",
                ip_address=ip,
                mac_address=f"00:1A:2B:6F:{i:02X}:{i:02X}",
                asset_type=AssetType.ROUTER,
                operating_system="Cisco IOS-XE 17.3",
                location="Server Room",
                production_line=None,
                status=AssetStatus.ONLINE,
                owner_team="Network Team",
                criticality=CriticalityLevel.CRITICAL,
                description=f"Core router {i}",
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 10)),
            )
            db.add(asset)

        # Create Printers - use unique IPs
        for i in range(1, 6):
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            asset = Asset(
                hostname=f"PRN-OFFICE-{i:02d}",
                ip_address=ip,
                mac_address=f"00:1A:2B:7A:{i:02X}:{i:02X}",
                asset_type=AssetType.PRINTER,
                operating_system="Embedded Linux",
                location=random.choice(["Office 1", "Office 2", "Office 3", "Reception"]),
                production_line=None,
                status=AssetStatus.ONLINE,
                owner_team="IT Support",
                criticality=CriticalityLevel.LOW,
                description=f"Office printer {i}",
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(5, 60)),
            )
            db.add(asset)

        # Create Applications - use unique IPs
        apps = [
            ("APP-ERP", "ERP Production System"),
            ("APP-MES", "Manufacturing Execution System"),
            ("APP-WMS", "Warehouse Management System"),
            ("APP-SCADA", "SCADA HMI System"),
            ("APP-CRM", "Customer Relationship Management"),
        ]

        for hostname, desc in apps:
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            asset = Asset(
                hostname=hostname,
                ip_address=ip,
                mac_address=None,
                asset_type=AssetType.APPLICATION,
                operating_system="Windows Server 2022 / Linux",
                location="Server Room",
                production_line=None,
                status=AssetStatus.ONLINE,
                owner_team="Application Team",
                criticality=CriticalityLevel.HIGH,
                description=desc,
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 20)),
            )
            db.add(asset)

        # Create Network Services - use unique IPs
        services = [
            ("SVC-DNS", "DNS Service"),
            ("SVC-DHCP", "DHCP Service"),
            ("SVC-NTP", "NTP Time Service"),
            ("SVC-LDAP", "LDAP Authentication"),
        ]

        for hostname, desc in services:
            ip = f"{base_ip}.{ip_counter}"
            ip_counter += 1
            asset = Asset(
                hostname=hostname,
                ip_address=ip,
                mac_address=None,
                asset_type=AssetType.NETWORK_SERVICE,
                operating_system="Windows Server / Linux",
                location="Server Room",
                production_line=None,
                status=AssetStatus.ONLINE,
                owner_team="Infrastructure Team",
                criticality=CriticalityLevel.CRITICAL,
                description=desc,
                is_active=True,
                last_check=datetime.utcnow() - timedelta(minutes=random.randint(1, 10)),
            )
            db.add(asset)

        db.commit()
        print(f"Created {db.query(Asset).count()} assets")

        # Create some incidents
        incidents = [
            ("INC-1042", "PROD-PC-024", IncidentCategory.NETWORK, IncidentSeverity.HIGH, IncidentPriority.P2,
             "Production PC offline", "PROD-PC-024 is not responding to ping checks. Production Line 2 may be affected.",
             IncidentStatus.INVESTIGATING, "Ahmed Z."),
            ("INC-1041", "SW-ACCESS-03", IncidentCategory.NETWORK, IncidentSeverity.MEDIUM, IncidentPriority.P3,
             "High packet loss on switch", "Switch SW-ACCESS-03 reporting 18% packet loss on VLAN 20.",
             IncidentStatus.IN_PROGRESS, "Sarah M."),
            ("INC-1040", "SRV-ERP-01", IncidentCategory.SERVER, IncidentSeverity.HIGH, IncidentPriority.P2,
             "High CPU usage on ERP server", "SRV-ERP-01 CPU usage at 87% for over 15 minutes.",
             IncidentStatus.OPEN, None),
            ("INC-1039", "PROD-PC-015", IncidentCategory.WORKSTATION, IncidentSeverity.LOW, IncidentPriority.P4,
             "Workstation slow response", "PROD-PC-015 experiencing slow disk I/O.",
             IncidentStatus.RESOLVED, "Ahmed Z."),
            ("INC-1038", "RT-CORE-01", IncidentCategory.NETWORK, IncidentSeverity.CRITICAL, IncidentPriority.P1,
             "Core router high latency", "RT-CORE-01 showing 240ms average latency to production network.",
             IncidentStatus.INVESTIGATING, "Sarah M."),
            ("INC-1037", "APP-SCADA", IncidentCategory.APPLICATION, IncidentSeverity.MEDIUM, IncidentPriority.P3,
             "SCADA application timeout", "SCADA HMI application experiencing intermittent timeouts.",
             IncidentStatus.OPEN, None),
            ("INC-1036", "PRN-OFFICE-02", IncidentCategory.HARDWARE, IncidentSeverity.LOW, IncidentPriority.P4,
             "Printer offline", "Office printer 2 is offline.",
             IncidentStatus.CLOSED, "John D."),
            ("INC-1035", "SRV-DB-01", IncidentCategory.SERVER, IncidentSeverity.HIGH, IncidentPriority.P2,
             "Database connection pool exhausted", "PostgreSQL connection pool at 95% capacity.",
             IncidentStatus.IN_PROGRESS, "Sarah M."),
            ("INC-1034", "PROD-PC-031", IncidentCategory.WORKSTATION, IncidentSeverity.MEDIUM, IncidentPriority.P3,
             "Workstation disk space low", "PROD-PC-031 disk usage at 92%.",
             IncidentStatus.OPEN, None),
            ("INC-1033", "SW-ACCESS-07", IncidentCategory.NETWORK, IncidentSeverity.MEDIUM, IncidentPriority.P3,
             "Switch port flapping", "Switch SW-ACCESS-07 port 12 experiencing flapping.",
             IncidentStatus.INVESTIGATING, "Ahmed Z."),
        ]

        for inc_id, hostname, category, severity, priority, title, desc, status, tech in incidents:
            asset = db.query(Asset).filter(Asset.hostname == hostname).first()
            if asset:
                incident = Incident(
                    incident_id=inc_id,
                    asset_id=asset.id,
                    category=category,
                    severity=severity,
                    priority=priority,
                    status=status,
                    title=title,
                    description=desc,
                    detected_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                    assigned_technician=tech,
                    risk_score=random.randint(20, 80) if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL] else None,
                    production_impact="HIGH" if severity == IncidentSeverity.CRITICAL else ("MEDIUM" if severity == IncidentSeverity.HIGH else None),
                )
                db.add(incident)

        db.commit()
        print(f"Created {db.query(Incident).count()} incidents")

        # Create some events
        events = [
            (EventType.SYSTEM, "Monitoring engine started"),
            (EventType.MONITORING_CHECK, "ICMP check completed for 83 assets"),
            (EventType.INCIDENT_CREATED, "INC-1042 created: PROD-PC-024 offline"),
            (EventType.INCIDENT_UPDATED, "INC-1041 assigned to Sarah M."),
            (EventType.MONITORING_CHECK, "TCP port check completed for 8 servers"),
            (EventType.SYSTEM, "Database backup completed successfully"),
            (EventType.INCIDENT_RESOLVED, "INC-1039 resolved: Workstation slow response"),
            (EventType.MONITORING_CHECK, "HTTP health check completed for 5 applications"),
        ]

        for event_type, message in events:
            event = Event(
                event_type=event_type,
                message=message,
            )
            db.add(event)

        db.commit()
        print(f"Created {db.query(Event).count()} events")

        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()