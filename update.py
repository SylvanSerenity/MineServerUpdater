import os
import json
import requests
import hashlib
from tqdm import tqdm
import concurrent.futures
from copy import deepcopy
import shutil

CONFIG_FILE = "servers.json"
INSTALL_DIR = os.path.abspath("minecraft-servers")
MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
USERNAME_URL = "https://api.mojang.com/users/profiles/minecraft/"
ICON_FILE = "server-icon.png"

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

def resolve_uuid(username):
	url = USERNAME_URL + username
	resp = requests.get(url)
	if resp.status_code == 200:
		raw = resp.json().get("id", "")
		return format_uuid(raw)
	return ""

def format_uuid(raw_uuid):
	return f"{raw_uuid[0:8]}-{raw_uuid[8:12]}-{raw_uuid[12:16]}-{raw_uuid[16:20]}-{raw_uuid[20:]}"

def load_json_file(path):
	if os.path.exists(path):
		with open(path, "r") as f:
			try:
				return json.load(f)
			except json.JSONDecodeError:
				return []
	return []

def save_json_file(path, data):
	with open(path, "w") as f:
		json.dump(data, f, indent=2)

def update_eula(server_dir, accepted):
	eula_path = os.path.join(server_dir, "eula.txt")
	current = None
	if os.path.exists(eula_path):
		with open(eula_path) as f:
			for line in f:
				if line.startswith("eula="):
					current = line.strip().split("=")[1] == "true"
					break
	if current != accepted:
		with open(eula_path, "w") as f:
			f.write(f"eula={'true' if accepted else 'false'}\n")
			print("📜 Wrote eula.txt")
	else:
		print("✅ eula.txt already matches")

def update_whitelist(server_dir, usernames):
	if not usernames:
		return
	path = os.path.join(server_dir, "whitelist.json")
	existing = load_json_file(path)
	existing_names = {entry["name"] for entry in existing}
	changed = False
	for name in usernames:
		if name not in existing_names:
			uuid = resolve_uuid(name)
			existing.append({
				"uuid": uuid,
				"name": name
			})
			changed = True
	if changed:
		save_json_file(path, existing)
		print("👤 Updated whitelist.json")
	else:
		print("✅ whitelist.json already matches")

def update_ops(server_dir, usernames):
	if not usernames:
		return
	path = os.path.join(server_dir, "ops.json")
	existing = load_json_file(path)
	existing_names = {op["name"] for op in existing}
	changed = False
	for name in usernames:
		if name not in existing_names:
			uuid = resolve_uuid(name)
			existing.append({
				"uuid": uuid,
				"name": name,
				"level": 4,
				"bypassesPlayerLimit": False
			})
			changed = True
	if changed:
		save_json_file(path, existing)
		print("🛡️  Updated ops.json")
	else:
		print("✅ ops.json already matches")

def update_banned_players(server_dir, usernames):
	if not usernames:
		return
	path = os.path.join(server_dir, "banned-players.json")
	existing = load_json_file(path)
	existing_names = {entry["name"] for entry in existing}
	changed = False
	for name in usernames:
		if name not in existing_names:
			uuid = resolve_uuid(name)
			existing.append({
				"uuid": uuid,
				"name": name,
				"created": "",
				"source": "",
				"expires": "forever",
				"reason": ""
			})
			changed = True
	if changed:
		save_json_file(path, existing)
		print("🚫 Updated banned-players.json")
	else:
		print("✅ whitelist.json already matches")

def update_banned_ips(server_dir, ips):
	if not ips:
		return
	path = os.path.join(server_dir, "banned-ips.json")
	existing = load_json_file(path)
	existing_ips = {entry["ip"] for entry in existing}
	changed = False
	for ip in ips:
		if ip not in existing_ips:
			existing.append({
				"ip": ip,
				"created": "",
				"source": "",
				"expires": "forever",
				"reason": ""
			})
			changed = True
	if changed:
		save_json_file(path, existing)
		print("🌐 Updated banned-ips.json")
	else:
		print("✅ whitelist.json already matches")


def install_server(server_id, server_config, manifest):
	print(f"Installing {server_id}...")

	server_dir = os.path.join(INSTALL_DIR, server_id)
	if not os.path.exists(server_dir):
		os.makedirs(server_dir)

	version_str = server_config["version"]
	version_id = version_str
	if version_str == "custom" or server_config.get("skip_download"):
		print(f"⚙️ Skipping server.jar download for {server_id} (custom)")
	else:
		version_id = resolve_version_id(version_str, manifest)
		version_meta = find_version_meta(version_id, manifest)
		version_json = fetch_json(version_meta["url"])

		server_dl = version_json.get("downloads", {}).get("server")
		if not server_dl:
			print(f"No server JAR found for {version_id}")
			return

		jar_path = os.path.join(server_dir, "server.jar")
		update_server(jar_path, server_dl, server_id, version_id)

	update_server_properties(server_id, server_dir, server_config.get("properties", {}))
	update_eula(server_dir, server_config.get("eula", True))
	update_whitelist(server_dir, server_config.get("whitelist", []))
	update_ops(server_dir, server_config.get("ops", []))
	update_banned_players(server_dir, server_config.get("banned_players", []))
	update_banned_ips(server_dir, server_config.get("banned_ips", []))

	icon_path = os.path.join(server_dir, ICON_FILE)
	if os.path.exists(ICON_FILE):
		if os.path.exists(icon_path):
			print("✅ Server icon already matches")
		else:
			shutil.copyfile(ICON_FILE, icon_path)
			print("🖼️ Updated server icon")

	print(f"Installed {server_id} ({version_id})")


def apply_defaults(server_cfg, defaults):
	cfg = deepcopy(defaults)
	cfg.update(server_cfg)

	# Merge nested 'properties' dict
	props = deepcopy(defaults.get("properties", {}))
	props.update(server_cfg.get("properties", {}))
	cfg["properties"] = props
	return cfg

def main():
	global INSTALL_DIR
	full_cfg = read_config()
	defaults = full_cfg.get("default", {})
	manifest = fetch_json(MANIFEST_URL)
	INSTALL_DIR = os.path.abspath(full_cfg["install_dir"])

	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = []
		for entry in full_cfg.get("servers", []):
			server_id = entry["id"]
			merged = apply_defaults(entry, defaults)
			futures.append(executor.submit(install_server, server_id, merged, manifest))

		for future in concurrent.futures.as_completed(futures):
			try:
				future.result()
			except Exception as e:
				server_id = futures[future]
				print(f"Failed to install {server_id}: {e}")

if __name__ == "__main__":
	main()
