import os
import ansible_runner

from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager


BASE_DIR = "/home/maj18/automation/runner_service/ansible"
PROJECT_DIR = os.path.join(BASE_DIR, "project")
INVENTORY_DIR = os.path.join(BASE_DIR, "inventory")
ARTIFACT_DIR = os.path.join(BASE_DIR, "artifact")


def get_resources():
    playbooks = [f for f in os.listdir(PROJECT_DIR) if f.endswith((".yml", ".yaml"))]
    inventories = [f for f in os.listdir(INVENTORY_DIR) if os.path.isfile(os.path.join(INVENTORY_DIR, f))]
    return {"playbooks": playbooks, "inventories": inventories}

def create_inventory(inventory_name, groupe_name='all' ) :
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources='INVENTORY_DIR')
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    inventory.add_group()
    inventory.add_host('demo host', group='demo')

def parse_inventory(inventory_file, base_dir):
    path_to_inventory = os.path.join(base_dir, "inventory", inventory_file)
    # inventory_data = ansible_runner.interface.get_inventory(action="host", inventories=[path_to_inventory])
    inventory_data = ansible_runner.interface.get_inventory(action="list", inventories=[path_to_inventory])
    # inventory_data = ansible_runner.interface.get_inventory(action="graph", inventories=[path_to_inventory])

    return inventory_data


def execute_playbook(playbook, inventory, extravars=None):
    runner = ansible_runner.run(
        private_data_dir=BASE_DIR,
        playbook=playbook,
        inventory=inventory,
        extravars=extravars or {
            "message_name": "testcase1"
        },
        artifact_dir=ARTIFACT_DIR,
        limit=virtual_factory
    )
    return {
        "status": runner.status,
        "rc": runner.rc,
        "stdout": runner.stdout.read() if hasattr(runner, "stdout") else None,
        "stats": runner.stats,
    }


if __name__ == "__main__":
    resources = get_resources()
    print("Available Resources:", resources)

    if resources["playbooks"] and resources["inventories"]:
        playbook = resources["playbooks"][0]
        inventory = resources["inventories"][0]
        print(f"\nExecuting Playbook: {playbook} with Inventory: {inventory}\n")
        inventory_data = parse_inventory(inventory, BASE_DIR)
        result = execute_playbook(playbook, inventory)
        print("Execution Result:", result)
        
    else:
        print("No playbooks or inventories found.")
