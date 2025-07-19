import os
import json
import requests
import hashlib
from tqdm import tqdm
import concurrent.futures

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
	print(f"\nInstalling {server_id}...")
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
	update_server(jar_path, server_dl, server_id, version_id)

	props = server_config.get("properties", {})
	update_server_properties(server_id, server_dir, props)

	print(f"Installed {server_id} ({version_id})")

def update_server(jar_path, server_dl, server_id, version_id):
	# Compare SHA1 if file exists
	if os.path.exists(jar_path):
		local_sha = sha1sum(jar_path)
		if local_sha == server_dl["sha1"]:
			print(f"✅ {server_id} already has latest server.jar")
			return
		else:
			print(f"🔁 {server_id} outdated. Updating server.jar...")
	else:
		print(f"🔁 {server_id} does not exist. Downloading server.jar...")

	download_file(version_id, server_dl["url"], jar_path)

def download_file(version_id, url, dest):
	print(f"Downloading server v{version_id} from: {url}")
	os.makedirs(os.path.dirname(dest), exist_ok=True)
	r = requests.get(url, stream=True)
	total = int(r.headers.get("content-length", 0))
	with open(dest, "wb") as f, tqdm(
		total=total, unit='B', unit_scale=True, desc=os.path.basename(dest)
	) as bar:
		for chunk in r.iter_content(chunk_size=8192):
			f.write(chunk)
			bar.update(len(chunk))

def update_server_properties(server_id, server_dir, new_props):
	props_path = os.path.join(server_dir, "server.properties")
	props = {}

	# Load existing if it exists
	if os.path.exists(props_path):
		with open(props_path, "r") as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith("#") or "=" not in line:
					continue
				key, value = line.split("=", 1)
				props[key.strip()] = value.strip()

	changed = False
	for key, val in new_props.items():
		if props.get(key) != str(val):
			props[key] = str(val)
			changed = True

	if changed or not os.path.exists(props_path):
		with open(props_path, "w") as f:
			for k, v in sorted(props.items()):
				f.write(f"{k}={v}\n")
		print(f"📝 Updated server.properties for {server_id}")
	else:
		print(f"✅ server.properties for {server_id} already up to date")

def main():
	config = read_config()
	manifest = fetch_json(MANIFEST_URL)

	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = {
			executor.submit(install_server, server_id, server_config, manifest): server_id
			for server_id, server_config in config.items()
		}
		for future in concurrent.futures.as_completed(futures):
			try:
				future.result()
			except Exception as e:
				server_id = futures[future]
				print(f"Failed to install {server_id}: {e}")

if __name__ == "__main__":
	main()
