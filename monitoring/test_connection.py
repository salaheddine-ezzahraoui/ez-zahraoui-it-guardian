from database import get_active_assets

assets = get_active_assets()
print(f"Found {len(assets)} active assets")
for a in assets[:5]:
    print(f"  {a['hostname']} ({a['ip_address']}) - {a['status']}")
print("  ...")
print("Database connection OK!")
