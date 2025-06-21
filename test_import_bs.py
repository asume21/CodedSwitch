import traceback

print("Attempting to import beat_studio_professional...")
try:
    import beat_studio_professional as bs
    print("✅ Imported successfully!")
except Exception as e:
    print("❌ Import failed:", e)
    traceback.print_exc()
