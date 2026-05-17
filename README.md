# CPU-Scheduling-Simulator-OS-Graphics-

## 📌 Project Overview
This project is a **CPU Scheduling Simulator** built using **Python (Tkinter)**.  
It simulates how the operating system schedules processes using different algorithms and visualizes execution using **Gantt Charts + Performance Metrics graphs**.

---

## ⚙️ Features
- Add processes with:
  - Process ID (PID)
  - Arrival Time
  - Burst Time
- Choose scheduling mode:
  - Preemptive
  - Non-preemptive
- Supports multiple CPU Scheduling Algorithms:
  - FCFS (First Come First Serve)
  - SJF (Shortest Job First)
  - Round Robin
- Visual **Gantt Chart animation**
- Performance analysis charts:
  - Waiting Time
  - Turnaround Time
  - Response Time
- Calculates:
  - Completion Time
  - Waiting Time
  - Turnaround Time
  - Response Time
  - Averages for all metrics

---

## Algorithms Implemented
### 1️⃣ FCFS
Processes executed in order of arrival time (non-preemptive).

### 2️⃣ SJF (Shortest Job First)
- Non-preemptive version
- Preemptive version (SRTF - Shortest Remaining Time First)

### 3️⃣ Round Robin
- Uses time quantum
- Cyclic execution using queue (deque)

---

## 🖥️ Technologies Used
- Python 3
- Tkinter (GUI)
- Matplotlib (Data Visualization)
- Collections (deque)
- Time module

---

## 📊 Outputs
The simulator generates:

### 🎯 Gantt Chart
- Shows execution timeline of processes
- Animated step-by-step execution

### 📈 Performance Charts
- Waiting Time per process
- Turnaround Time per process
- Response Time per process
- Average values displayed clearly

---
### 1. Install requirements
```bash
pip install matplotlib
