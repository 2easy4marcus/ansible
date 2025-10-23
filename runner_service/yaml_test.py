import yaml


def read_and_modify_one_block_of_yaml_data(filename, write_file, key, value):
    with open(filename, "r") as f:
        data = yaml.safe_load(f)
        data["all"]["children"]["alpamayo"]["hosts"][key] = value
        print(data)
    with open(write_file, "w") as file:
        yaml.dump(data, file, sort_keys=False)
    print("done!")


read_and_modify_one_block_of_yaml_data(
    "ansible/inventory/alpamayo.yml",
    "output5.yaml",
    key="demo",
    value={
        "ansible_host": "192.168.1.100",
        "ansible_user": "admin",
        "custom_var": "some_value"
    }
)



