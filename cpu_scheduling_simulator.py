import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from collections import deque
import time


class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.original_burst = int(burst)


def merge_gantt(gantt):
    merged = []
    for pid, start, end in gantt:
        if start == end:
            continue
        if merged and merged[-1][0] == pid and merged[-1][2] == start:
            merged[-1] = (pid, merged[-1][1], end)
        else:
            merged.append((pid, start, end))
    return merged


def fcfs(processes):
    """ First Come First Served CPU Scheduling Algorithm """
    processes = sorted(processes, key=lambda x: x.arrival)
    time_now = 0
    gantt = []

    for p in processes:
        if time_now < p.arrival:
            time_now = p.arrival

        start = time_now
        end = time_now + p.burst
        gantt.append((p.pid, start, end))
        time_now = end

    return gantt

def sjf_non_preemptive(processes):
    processes = sorted(processes, key=lambda x: x.arrival)
    time_now = 0
    gantt = []
    ready = []

    while processes or ready:
        while processes and processes[0].arrival <= time_now:
            ready.append(processes.pop(0))

        if not ready:
            time_now = processes[0].arrival
            continue

        ready.sort(key=lambda x: (x.burst, x.arrival, x.pid))
        p = ready.pop(0)

        start = time_now
        end = time_now + p.burst
        gantt.append((p.pid, start, end))
        time_now = end

    return gantt


def sjf_preemptive(processes):
    # Preemptive SJF is also called SRTF: Shortest Remaining Time First.
    processes = sorted(processes, key=lambda x: x.arrival)
    time_now = 0
    gantt = []
    ready = []

    while processes or ready:
        while processes and processes[0].arrival <= time_now:
            ready.append(processes.pop(0))

        if not ready:
            time_now = processes[0].arrival
            continue

        ready.sort(key=lambda x: (x.burst, x.arrival, x.pid))
        p = ready[0]

        start = time_now
        time_now += 1
        p.burst -= 1
        gantt.append((p.pid, start, time_now))

        if p.burst == 0:
            ready.pop(0)

    return merge_gantt(gantt)


def round_robin(processes, quantum):
    processes = sorted(processes, key=lambda x: x.arrival)
    ready = deque()
    gantt = []
    time_now = 0
    index = 0

    while index < len(processes) or ready:
        if not ready and index < len(processes) and time_now < processes[index].arrival:
            time_now = processes[index].arrival

        while index < len(processes) and processes[index].arrival <= time_now:
            ready.append(processes[index])
            index += 1

        if not ready:
            continue

        p = ready.popleft()
        exec_time = min(p.burst, quantum)
        start = time_now
        end = time_now + exec_time

        gantt.append((p.pid, start, end))
        time_now = end
        p.burst -= exec_time

        while index < len(processes) and processes[index].arrival <= time_now:
            ready.append(processes[index])
            index += 1

        if p.burst > 0:
            ready.append(p)

    return gantt


def calculate_metrics(gantt, processes):
    metrics = {}

    for p in processes:
        metrics[p.pid] = {
            "arrival": p.arrival,
            "burst": p.original_burst,
            "first_start": None,
            "completion": None,
            "run_intervals": [],
            "waiting_intervals": [],
            "waiting": 0,
            "turnaround": 0,
            "response": 0,
        }

    for pid, start, end in gantt:
        if metrics[pid]["first_start"] is None:
            metrics[pid]["first_start"] = start
        metrics[pid]["completion"] = end
        metrics[pid]["run_intervals"].append((start, end))

    for pid, data in metrics.items():
        data["turnaround"] = data["completion"] - data["arrival"]
        data["response"] = data["first_start"] - data["arrival"]

        waiting_intervals = []
        wait_start = data["arrival"]
        for start, end in data["run_intervals"]:
            if wait_start < start:
                waiting_intervals.append((wait_start, start))
            wait_start = end

        data["waiting_intervals"] = waiting_intervals
        data["waiting"] = sum(end - start for start, end in waiting_intervals)

    averages = {
        "waiting": sum(data["waiting"] for data in metrics.values()) / len(metrics),
        "turnaround": sum(data["turnaround"] for data in metrics.values()) / len(metrics),
        "response": sum(data["response"] for data in metrics.values()) / len(metrics),
    }

    return metrics, averages


def draw_gantt(gantt, processes):
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 3))

    burst_map = {p.pid: p.original_burst for p in processes}
    min_burst = min(burst_map.values())
    max_burst = max(burst_map.values())

    def get_color(pid):
        burst = burst_map[pid]
        if max_burst == min_burst:
            norm = 0.5
        else:
            norm = (burst - min_burst) / (max_burst - min_burst)
        return (norm, 0.2, 1 - norm)

    ax.set_xlabel("Time")
    ax.set_yticks([])
    ax.set_ylim(-0.6, 0.6)

    current_max_time = 0

    for pid, start, end in gantt:
        duration = end - start
        color = get_color(pid)

        ax.barh(0, duration, left=start, height=0.5, color=color, edgecolor="black")
        ax.text(
            start + duration / 2,
            0,
            pid,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
        )

        current_max_time = max(current_max_time, end)
        ax.set_xlim(0, current_max_time + 1)
        ax.set_title(f"Running: {pid} | {start} -> {end}")

        plt.draw()
        plt.pause(0.01)
        time.sleep(0.4)

    ax.set_xticks(range(0, current_max_time + 1))
    ax.set_title("Gantt Chart")
    plt.ioff()
    plt.show()


def draw_metric_chart(metrics, averages, metric_key, title, color):
    pids = list(metrics.keys())
    average = averages[metric_key]

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, max(3, len(pids) * 0.7)))

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_yticks(range(len(pids)))
    ax.set_yticklabels(pids)
    ax.set_ylim(-0.7, len(pids) - 0.3)

    max_time = max(data["completion"] for data in metrics.values())

    for row, pid in enumerate(pids):
        value = metrics[pid][metric_key]

        if metric_key == "waiting":
            intervals = metrics[pid]["waiting_intervals"]
        elif metric_key == "turnaround":
            intervals = [(metrics[pid]["arrival"], metrics[pid]["completion"])]
        else:
            intervals = [(metrics[pid]["arrival"], metrics[pid]["first_start"])]

        if not intervals or value == 0:
            marker_time = metrics[pid]["arrival"]
            if metric_key == "turnaround":
                marker_time = metrics[pid]["completion"]

            ax.plot(marker_time, row, marker="o", color=color)
            ax.text(
                marker_time,
                row + 0.28,
                f"{pid} = 0",
                ha="center",
                va="center",
                color="black",
                fontweight="bold",
            )
            ax.set_xlim(0, max_time + 1)
            ax.set_title(f"{title}: {pid} = {value}")
            plt.draw()
            plt.pause(0.01)
            time.sleep(0.4)
            continue

        for start, end in intervals:
            duration = end - start
            if duration <= 0:
                continue

            ax.barh(row, duration, left=start, height=0.5, color=color, edgecolor="black")
            ax.text(
                start + duration / 2,
                row,
                pid,
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
            )

        ax.set_title(f"{title}: {pid} = {value}")
        ax.set_xlim(0, max_time + 1)
        plt.draw()
        plt.pause(0.01)
        time.sleep(0.4)

    ax.set_xticks(range(0, max_time + 1))
    ax.set_title(title)
    fig.text(0.5, 0.02, f"Average {title}: {average:.2f}", ha="center", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    plt.ioff()
    plt.show()


def draw_metric_charts(metrics, averages):
    draw_metric_chart(metrics, averages, "waiting", "Waiting Time", "#efdddd")
    draw_metric_chart(metrics, averages, "turnaround", "Turnaround Time", "#59a14f")
    draw_metric_chart(metrics, averages, "response", "Response Time", "#f28e2b")


process_list = []
mode_var = None


def set_mode(mode):
    mode_var.set(mode)
    if mode == "preemptive":
        btn_preemptive.config(relief=tk.SUNKEN, bg="#cdeffd")
        btn_non_preemptive.config(relief=tk.RAISED, bg="SystemButtonFace")
    else:
        btn_non_preemptive.config(relief=tk.SUNKEN, bg="#cdeffd")
        btn_preemptive.config(relief=tk.RAISED, bg="SystemButtonFace")


def add_process():
    pid = entry_pid.get().strip()
    arrival = entry_arrival.get().strip()
    burst = entry_burst.get().strip()

    if not pid or not arrival or not burst:
        messagebox.showerror("Error", "Fill all fields")
        return

    try:
        arrival_int = int(arrival)
        burst_int = int(burst)
    except ValueError:
        messagebox.showerror("Error", "Arrival and burst must be numbers")
        return

    if arrival_int < 0 or burst_int <= 0:
        messagebox.showerror("Error", "Arrival must be >= 0 and burst must be > 0")
        return

    if any(p.pid == pid for p in process_list):
        messagebox.showerror("Error", "Process ID must be unique")
        return

    process_list.append(Process(pid, arrival_int, burst_int))
    tree.insert("", "end", values=(pid, arrival_int, burst_int))

    entry_pid.delete(0, tk.END)
    entry_arrival.delete(0, tk.END)
    entry_burst.delete(0, tk.END)


def run_algorithm():
    if not process_list:
        messagebox.showerror("Error", "No processes added")
        return

    algo = combo_algo.get()
    processes_copy = [Process(p.pid, p.arrival, p.original_burst) for p in process_list]
    is_preemptive = mode_var.get() == "preemptive"

    if algo == "FCFS":
        if is_preemptive:
            messagebox.showinfo("Note", "FCFS is normally non-preemptive. Running FCFS as non-preemptive.")
        gantt = fcfs(processes_copy)

    elif algo == "SJF":
        if is_preemptive:
            gantt = sjf_preemptive(processes_copy)
        else:
            gantt = sjf_non_preemptive(processes_copy)

    elif algo == "Round Robin":
        try:
            quantum = int(entry_quantum.get())
        except ValueError:
            messagebox.showerror("Error", "Enter valid quantum")
            return

        if quantum <= 0:
            messagebox.showerror("Error", "Quantum must be greater than 0")
            return

        gantt = round_robin(processes_copy, quantum)

    else:
        messagebox.showerror("Error", "Select algorithm")
        return

    metrics, averages = calculate_metrics(gantt, process_list)
    draw_gantt(gantt, process_list)
    draw_metric_charts(metrics, averages)


root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("620x580")

mode_var = tk.StringVar(value="non_preemptive")

tk.Label(root, text="Process ID").pack()
entry_pid = tk.Entry(root)
entry_pid.pack()

tk.Label(root, text="Arrival Time").pack()
entry_arrival = tk.Entry(root)
entry_arrival.pack()

tk.Label(root, text="Burst Time").pack()
entry_burst = tk.Entry(root)
entry_burst.pack()

tk.Button(root, text="Add Process", command=add_process).pack(pady=5)

mode_frame = tk.Frame(root)
mode_frame.pack(pady=8)

btn_preemptive = tk.Button(
    mode_frame,
    text="Preemptive",
    width=16,
    command=lambda: set_mode("preemptive"),
)
btn_preemptive.pack(side=tk.LEFT, padx=5)

btn_non_preemptive = tk.Button(
    mode_frame,
    text="Non-preemptive",
    width=16,
    command=lambda: set_mode("non_preemptive"),
)
btn_non_preemptive.pack(side=tk.LEFT, padx=5)

tree = ttk.Treeview(root, columns=("PID", "Arrival", "Burst"), show="headings")
tree.heading("PID", text="PID")
tree.heading("Arrival", text="Arrival")
tree.heading("Burst", text="Burst")
tree.pack(pady=10)

tk.Label(root, text="Select Algorithm").pack()
combo_algo = ttk.Combobox(root, values=["FCFS", "SJF", "Round Robin"], state="readonly")
combo_algo.pack()

tk.Label(root, text="Time Quantum (Round Robin only)").pack()
entry_quantum = tk.Entry(root)
entry_quantum.pack()

tk.Button(root, text="Run", command=run_algorithm).pack(pady=20)

set_mode("non_preemptive")
root.mainloop()
