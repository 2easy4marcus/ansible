# 🚀 Getting Started with Ansible — Deployment & Rollback Automation

> This guide explains how we use **Ansible** to deploy and manage our edge-node application across remote hosts.  
> It covers what Ansible is, how our setup is structured, and how to run deployments and rollbacks safely.

---

## 🧠 1️⃣ What is Ansible?

Ansible is an **automation and configuration management tool**.  
It lets you run commands, copy files, install software, and orchestrate entire deployments on remote machines — **without installing anything on them**.

### ✨ Key points
- **Agentless:** No daemon or agent needed on the remote host. It works over **SSH**.  
- **Idempotent:** Running a playbook twice gives the same result — no duplication or side effects.  
- **Declarative:** You describe *what you want*, not *how to do it*.  
- **Extensible:** You can organize configurations into inventories, playbooks, and reusable roles.

### 🔐 How it works
1. Ansible connects via **SSH** to each target machine (using `ansible_user` and `ansible_host`).
2. It executes modules remotely (like `file`, `copy`, `docker_compose`, etc.).
3. It applies changes described in your playbooks.

✅ Nothing needs to be installed on the target host — only **Python** (already preinstalled on most Linux systems).

---

## 📦 2️⃣ Inventory — Defining Hosts and Groups

The **inventory file** lists all your remote machines and organizes them into logical **groups** (like *welotec*, *staging*, or *production*).

Example `inventory.yml`:
```yaml
all:
  children:
    welotec:
      hosts:
        aycer:
          ansible_host: 100.64.0.6
          ansible_user: maj18
        node2:
          ansible_host: 100.64.0.7
    staging:
      hosts:
        demo-staging:
          ansible_host: 192.168.5.30
    production:
      hosts:
        demo-production:
          ansible_host: 192.168.4.1
```

### 🧩 Explanation
- `all`: Root group containing all hosts.
- `children`: Subgroups (logical categories).
- `hosts`: Each machine with its SSH credentials and variables.
- You can define **per-group variables** in `group_vars/` and **per-host variables** in `host_vars/`.

✅ Example:
- `group_vars/welotec.yml` → shared settings for all Welotec devices.
- `host_vars/aycer.yml` → configuration specific to host `aycer`.

---

## ⚙️ 3️⃣ Playbooks — Automation Logic

Playbooks are YAML files describing **what tasks to perform** on which hosts.  
They’re the core of how we deploy and roll back the edge-node system.

### 📁 Our Key Playbooks

#### 🟢 `deployment_playbook.yml`
Used to **deploy or update** the composable-edge-node application.

**What it does:**
1. Checks if Docker and Docker Compose are installed.  
2. Ensures deployment and backup directories exist.  
3. Executes `make full` locally to generate deployment configs.  
4. Pulls required Docker images.  
5. Archives the current version (creates a backup).  
6. Updates the `latest` symlink.  
7. Starts the application using Docker Compose.

**Used when:**
> You’re deploying a **new version** of the app or updating an existing one.

✅ Run with:
```bash
ansible-playbook ansible/playbook/deployment_playbook.yml   -i ansible/inventory.yml   --limit welotec   --tags deploy
```

---

#### 🔄 `rollback_playbook.yml`
Used to **restore the last working backup** if the new version fails.

**What it does:**
1. Stops running containers.  
2. Checks if a backup exists.  
3. Extracts the previous backup archive.  
4. Restarts the containers from the backup version.  
5. Confirms the rollback was successful.

**Used when:**
> A deployment introduced errors or instability and you need to **revert to the last known good version**.

✅ Run with:
```bash
ansible-playbook ansible/playbook/rollback_playbook.yml   -i ansible/inventory.yml   --limit aycer   -e "rollback_version=stable"   --tags rollback
```

---

## 🌍 4️⃣ Host Limitation — Targeting Specific Machines

Ansible can target **groups** or **individual hosts** dynamically using the `--limit` flag.  
This lets you run the same playbook on different environments easily.

### 🧩 Examples

| Command | Effect |
|----------|--------|
| `--limit aycer` | Run only on host *aycer* |
| `--limit welotec` | Run on all hosts in the *welotec* group |
| `--limit "staging,production"` | Run on both groups |
| `--limit "!production"` | Run everywhere except production |

**Playbook host logic:**  
> Actual hosts executed = (`hosts:` in playbook) ∩ (`--limit` on command line)

✅ Example:
```bash
ansible-playbook deploy.yml --limit welotec
```
→ Runs only on all hosts inside the `welotec` group.

---

## 🏷️ 5️⃣ Tags — Running Only Specific Steps

Tags let you **select which parts of a playbook** to execute.  
Each task or section can be labeled with one or more tags like `deploy`, `rollback`, or `verify`.

Example snippet:
```yaml
- name: Create backup before deploy
  tags: backup
  ansible.builtin.archive:
    path: /opt/app
    dest: /opt/backup/app.tar.gz

- name: Start containers
  tags: deploy
  community.docker.docker_compose:
    project_src: /opt/app
    state: present
```

### Common Tag Commands

| Command | What it does |
|----------|---------------|
| `--tags deploy` | Runs only tasks tagged *deploy* |
| `--tags "backup,deploy"` | Runs only *backup* and *deploy* |
| `--skip-tags verify` | Skips verification steps |
| `--list-tags` | Lists all tags in the playbook |

✅ Example:
```bash
ansible-playbook ansible/playbook/deployment_playbook.yml   --limit welotec   --tags backup,deploy
```

---

## ⚙️ 6️⃣ How It All Fits Together

Here’s what happens when you deploy:

1. **Inventory** defines your remote machines (`welotec`, `staging`, etc.).
2. **Playbook** (`deployment_playbook.yml`) defines the steps to run.
3. You target specific hosts or groups with `--limit`.
4. You run specific task sections with `--tags`.
5. Ansible connects via SSH and executes the tasks remotely.
6. All configuration and logs are stored on the host — nothing runs persistently on your local machine.

---

## 🧭 7️⃣ Quick Reference Commands

| Purpose | Command |
|----------|----------|
| Deploy new version | `ansible-playbook ansible/playbook/deployment_playbook.yml --limit welotec --tags deploy` |
| Roll back to last working version | `ansible-playbook ansible/playbook/rollback_playbook.yml --limit aycer --tags rollback` |
| Check Docker setup only | `ansible-playbook ansible/playbook/deployment_playbook.yml --limit aycer --tags precheck` |
| List all available tags | `ansible-playbook ansible/playbook/deployment_playbook.yml --list-tags` |

---

## ✅ 8️⃣ Key Takeaways

- Ansible connects via **SSH**, no agent or daemon needed.  
- Your **inventory** defines hosts and groups.  
- **Playbooks** automate deployments and rollbacks.  
- Use `--limit` to choose which hosts run.  
- Use `--tags` to choose which tasks run.  
- Variables are auto-loaded from `group_vars/` and `host_vars/`.  
- Everything is transparent, reproducible, and easy to maintain.

---

> 📘 **In short:**  
> With just one command, you can safely deploy, test, or roll back your application across all your edge devices — cleanly, reproducibly, and with full control.
