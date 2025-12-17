# 🎬 CineSync – Distributed Movie Booking Platform

CineSync is a **distributed movie ticket reservation system** built using **Flask** and **CockroachDB (NewSQL)**. The system is designed to demonstrate **real-world distributed database concepts**, including **fault tolerance, recovery, strong consistency, replication, partitioning, and secure communication using TLS certificates**.

The CockroachDB cluster is deployed across **multiple machines**, simulating a production-grade distributed environment.

---

## ✨ Key Highlights

* 🌐 **Multi-machine distributed database cluster**
* 🔁 **Fault-tolerant & recovery-capable architecture**
* 🔒 **Serializable isolation** (strong transactional consistency)
* 📦 **Data partitioning & replication** across nodes
* 🛡️ **End-to-end security using TLS certificates**
* 📈 **Horizontally scalable system design**

---

## 🚀 Features

* **Browse Movies**: View available movies with filters (type, language, rating)
* **Theater Listings**: Browse theaters across cities
* **Showtime Selection**: Choose movie showtimes per theater
* **Interactive Seat Selection**: Real-time seat availability visualization
* **Booking Management**: Booking confirmation and history
* **User Authentication**: Session-based login & registration
* **Responsive UI**: Mobile-friendly interface using Bootstrap 5

---

## 🧱 Technology Stack

* **Backend**: Flask (Python)
* **Database**: CockroachDB (NewSQL, PostgreSQL-compatible)
* **ORM**: SQLAlchemy
* **Frontend**: Bootstrap 5, Vanilla JavaScript
* **Security**: TLS certificates (CA, node, client certs)

---

## 🏗️ Distributed Cluster Architecture

* **Node 1 (MacOS)**: `<NODE_1_IP>`
* **Node 2 (Windows / Linux)**: `<NODE_2_IP>`
* **Deployment**: Multi-machine CockroachDB cluster
* **Consistency Model**: Serializable Isolation (default)
* **Security**: Mutual TLS authentication

> 🔐 **Note**: IP addresses and hostnames are anonymized for security. Replace placeholders during deployment.

---

## 📁 Project Structure

```
cinesync/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   └── static/
├── requirements.txt
├── run.py
├── .env.example
└── README.md
```

---

## 🧩 Prerequisites

* Python 3.8+
* CockroachDB installed on all nodes
* Multi-machine setup (VMs or physical machines)
* Existing database named `cinesync` with populated tables

---

## 🔐 Secure Distributed CockroachDB Setup (Step-by-Step)

### Step 1: Create Directories (Node 1)

```bash
mkdir -p ~/cockroach-data-node1/certs
mkdir -p ~/cockroach-data-node1/my-safe-directory
mkdir -p ~/cockroach-data-node1/data
```

---

### Step 2: Create Certificate Authority (CA)

```bash
cockroach cert create-ca \
  --certs-dir=~/cockroach-data-node1/certs \
  --ca-key=~/cockroach-data-node1/my-safe-directory/ca.key
```

---

### Step 3: Create Node Certificate (Node 1)

```bash
cockroach cert create-node \
  localhost 127.0.0.1 <NODE_1_IP> \
  --certs-dir=~/cockroach-data-node1/certs \
  --ca-key=~/cockroach-data-node1/my-safe-directory/ca.key
```

---

### Step 4: Prepare Certificates for Node 2

```bash
mkdir -p ~/cockroach-node2-certs
cp ~/cockroach-data-node1/certs/ca.crt ~/cockroach-node2-certs/ca.crt
```

---

### Step 5: Create Node Certificate (Node 2)

```bash
cockroach cert create-node \
  <NODE_2_IP> \
  --certs-dir=~/cockroach-node2-certs \
  --ca-key=~/cockroach-data-node1/my-safe-directory/ca.key
```

---

### Step 6: Create Client Certificate

```bash
cockroach cert create-client root \
  --certs-dir=~/cockroach-data-node1/certs \
  --ca-key=~/cockroach-data-node1/my-safe-directory/ca.key
```

---

### Step 7: Start CockroachDB Node 1

```bash
cockroach start \
  --certs-dir=~/cockroach-data-node1/certs \
  --store=~/cockroach-data-node1/data \
  --listen-addr=<NODE_1_IP>:26257 \
  --http-addr=<NODE_1_IP>:8080 \
  --join=<NODE_1_IP>:26257,<NODE_2_IP>:26257
```

* Admin UI: `https://<NODE_1_IP>:8080`

---

### Step 8: Initialize the Cluster (Run Once)

```bash
cockroach init \
  --host=<NODE_1_IP>:26257 \
  --certs-dir=~/cockroach-data-node1/certs
```

Once the cluster is initialized **from the primary machine (Node 1)**, it becomes the trusted root of the cluster.

🔐 **Important:**

* All other nodes join the cluster using the **CA and node certificates generated on the primary machine**.
* As long as the joining nodes possess certificates signed by the same CA, they can securely authenticate and join the cluster.
* This enables **secure node discovery, mutual authentication, and encrypted communication** across machines.

---

## 🗄️ Database Schema

Expected tables:

* events
* theaters
* customers_local
* auditoriums
* seats
* shows
* bookings
* booking_seats

> ⚠️ This application does **not** run migrations. Tables must exist beforehand.

---

## ⚙️ Application Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Configuration

```env
SECRET_KEY=your-secret-key
DATABASE_URL=cockroachdb://user@<NODE_1_IP>:26257/cinesync?sslmode=verify-full
FLASK_ENV=development
```

---

## ▶️ Run the Application

```bash
python run.py
```

Access:

```
http://localhost:5000
```

---

## 🧠 System Design Concepts Demonstrated

* Distributed transactions
* Serializable isolation guarantees
* Consensus-driven replication
* Failure recovery
* Secure inter-node communication
* Horizontal scalability

---

## 🔐 Security Notes

⚠️ This is a demo/academic project.

For production:

* Use password hashing (bcrypt/argon2)
* Enable CSRF protection
* Enforce HTTPS
* Add rate limiting
* Implement monitoring & logging

---

## 📜 License

Educational / Demonstration purpose only.

---

## 🤝 Contributions

Built using **Flask**, **CockroachDB**, and **Bootstrap 5**.

---

⭐ If you find this project interesting, feel free to star the repo!
