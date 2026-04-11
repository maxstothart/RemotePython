import Remote

r = Remote.remote("tennant", "main.py", "/var/tmp/tmp.py")
remoteDirectory = "/mnt/v1/thehrvea/Music/Store"
if 0:
  r.pushFile()
  r.run(remoteDirectory, "listDir")
if 1:
  r.UI(remoteDirectory)
r.delete()
