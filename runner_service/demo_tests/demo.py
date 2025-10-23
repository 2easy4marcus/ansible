import os
import yaml
import ansible_runner
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

BASE_DIR = "/home/maj18/automation/runner_service/ansible"
INVENTORY_FILE = os.path.join(BASE_DIR, "inventory", "alpamayo.yml")
PLAYBOOK_FILE = os.path.join(BASE_DIR, "project", "hello.yml" )
ARTIFACT_DIR = os.path.join(BASE_DIR, "artifact")

def create_dynamic_inventory():
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=[INVENTORY_FILE])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    inventory.add_host("demo_host-1", group="alpamayo")
    
    inventory.add_group("demo")
    inventory.add_host("demo_host-2", group="demo")
    
    print("\n[INFO] In-memory inventory:")
    print(f"Groups: {[g.name for g in inventory.groups.values()]}")
    print(f"Hosts: {[h.name for h in inventory.get_hosts()]}")
    
    return inventory, variable_manager




def add_host(filename, write_file, key, value):
    with open(filename, "r") as f:
        data = yaml.safe_load(f)
        data["all"]["children"]["alpamayo"]["hosts"][key] = value
    with open(write_file, "w") as file:
        yaml.dump(data, file, sort_keys=False)
    print(f'{key} added permenantly to the inventory' )
    print(f"[INFO] Inventory saved at: {INVENTORY_FILE}")

def run_playbook():
    r = ansible_runner.run(
        private_data_dir=BASE_DIR,
        playbook=PLAYBOOK_FILE,
        inventory=INVENTORY_FILE,
        artifact_dir=ARTIFACT_DIR,
        extravars={"custom_var": "edge_node_B"},
        limit="demo-host-3"
    )
    print("[INFO] Playbook completed.")
    print(f"Status: {r.status}, RC: {r.rc}")
    print("Stats:", r.stats)
    if hasattr(r, "stdout"):
        print("\n--- Stdout ---")
        print(r.stdout.read())

if __name__ == "__main__":
    # Option 1: Just use file-based inventory
    add_host(INVENTORY_FILE, INVENTORY_FILE, "demo-host-3", {"ansible_host": "127.0.0.1", "ansible_user": "XXXXX"})
    run_playbook()
    
    # Option 2: Use in-memory inventory (uncomment to use)
    # inventory, variable_manager = create_dynamic_inventory()
    # The in-memory inventory has demo_host-1 and demo_host-2
    # But ansible_runner can't use it directly - you'd need to save it to a temp file first
