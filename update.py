import os
import json
import requests
import hashlib
from tqdm import tqdm

CONFIG_FILE = "servers.json"
BASE_DIR = os.path.abspath("minecraft_servers")
MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest.json"

def read_config():
	with open(CONFIG_FILE) as f:
		return json.load(f)

def fetch_json(url):
	return requests.get(url).json()

def sha1sum(path):
	h = hashlib.sha1()
	with open(path, "rb") as f:
		for chunk in iter(lambda: f.read(8192), b""):
			h.update(chunk)
	return h.hexdigest()

def resolve_version_id(version, manifest):
	if version.startswith("latest:"):
		key = version.split(":")[1]
		return manifest["latest"][key]
	return version

def find_version_meta(version_id, manifest):
	for entry in manifest["versions"]:
		if entry["id"] == version_id:
			return entry
	raise ValueError(f"Version {version_id} not found in manifest")

def install_server(server_id, server_config, manifest):
	version_str = server_config["version"]
	version_id = resolve_version_id(version_str, manifest)
	version_meta = find_version_meta(version_id, manifest)
	version_json = fetch_json(version_meta["url"])

	server_dl = version_json.get("downloads", {}).get("server")
	if not server_dl:
		print(f"No server JAR found for {version_id}")
		return

	server_dir = os.path.join(BASE_DIR, server_id)
	jar_path = os.path.join(server_dir, "server.jar")

	# Compare SHA1 if file exists
	if os.path.exists(jar_path):
		local_sha = sha1sum(jar_path)
		if local_sha == server_dl["sha1"]:
			print(f"✅ {server_id} already has latest server.jar")
			return
		else:
			print(f"🔁 {server_id} outdated. Updating server.jar...")

	dl_url = server_dl["url"]
	print(f"Downloading server v{version_str} from: {dl_url}")
	download_file(dl_url, jar_path)
	print(f"Installed {server_id} ({version_id})")

def download_file(url, dest):
	os.makedirs(os.path.dirname(dest), exist_ok=True)
	r = requests.get(url, stream=True)
	total = int(r.headers.get("content-length", 0))
	with open(dest, "wb") as f, tqdm(
		total=total, unit='B', unit_scale=True, desc=os.path.basename(dest)
	) as bar:
		for chunk in r.iter_content(chunk_size=8192):
			f.write(chunk)
			bar.update(len(chunk))

def main():
	config = read_config()
	manifest = fetch_json(MANIFEST_URL)

	for server_id, server_config in config.items():
		print(f"\nInstalling {server_id}...")
		try:
			install_server(server_id, server_config, manifest)
		except Exception as e:
			print(f"Failed to install {server_id}: {e}")

if __name__ == "__main__":
	main()
