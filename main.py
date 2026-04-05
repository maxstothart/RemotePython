import Remote

r = Remote.remote("tennant", "main.py", "/var/tmp/tmp.py")
r.pushFile()
r.run("/mnt/v1/thehrvea/Music/Store", "rTest", "Test123", "Test456")
r.delete()