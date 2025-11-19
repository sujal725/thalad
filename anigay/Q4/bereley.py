#!/usr/bin/env python3
"""
distributed_logging_berkeley.py

Single-file simulation of distributed logging using Berkeley clock synchronization.

How it works:
 - 3 Worker servers simulate unsynchronized physical clocks (static offset + small drift).
 - Each worker periodically generates log events stamped with its local raw timestamp.
 - A Master thread (Berkeley) periodically polls worker times, computes average,
   and applies a correction offset to each worker.
 - CentralLogManager merges logs from all workers using synchronized timestamps:
   sync_ts = raw_ts + worker.applied_correction_at_send_time (approximated)
 - Ties broken by server_id.

Run:
  python3 distributed_logging_berkeley.py
"""
import threading
import time
import random
from datetime import datetime

NUM_SERVERS = 3
LOG_INTERVAL = (0.5, 1.2)        # how often each server emits logs (random)
MASTER_POLL_INTERVAL = 5.0       # how often master performs Berkeley sync
MERGE_PRINT_INTERVAL = 5.0       # how often merged timeline is printed
SIMULATION_DURATION = 30.0       # total seconds to run before exiting (for demo)

class Worker:
    def __init__(self, server_id):
        self.server_id = server_id
        # local clock = real_time + static_offset + drift * elapsed + applied_correction
        self.static_offset = random.uniform(-3.0, 3.0)      # seconds
        self.drift_per_sec = random.uniform(-0.0008, 0.0008)
        self.start_real = time.time()
        self.start_local = self.start_real + self.static_offset
        self.applied_correction = 0.0
        self.lock = threading.Lock()
        self.logs = []

    def local_time(self):
        elapsed = time.time() - self.start_real
        return self.start_local + elapsed * (1.0 + self.drift_per_sec) + self.applied_correction

    def apply_correction(self, correction):
        with self.lock:
            # apply correction additively
            self.applied_correction += correction

    def generate_log(self):
        event = random.choice([
            "user_login", "file_uploaded", "db_write", "cache_miss",
            "scheduled_job", "config_change", "auth_fail", "heartbeat"
        ])
        raw_ts = self.local_time()
        log = {
            "server_id": self.server_id,
            "event": event,
            "raw_ts": raw_ts,
            # store a snapshot of current applied_correction to approximate sync_ts when merging
            "applied_corr_at_send": self.applied_correction,
            "recv_by_collector_at": time.time()
        }
        with self.lock:
            self.logs.append(log)
        print(f"[W{self.server_id}] Emitted '{event}' raw={raw_ts:.3f} corr={self.applied_correction:+.3f}")
        return log

    def get_and_clear_logs(self):
        with self.lock:
            copy = list(self.logs)
            # keep logs (do not clear) — central manager will read latest logs repeatedly
            return list(copy)

    def report_time_for_sync(self):
        # master uses this to get current local time snapshot
        return self.local_time()

class Master:
    def __init__(self, workers):
        self.workers = workers
        self.running = True

    def berkeley_loop(self):
        print("[MASTER] Berkeley sync started")
        while self.running:
            # collect times
            reports = []
            for w in self.workers:
                try:
                    t = w.report_time_for_sync()
                    reports.append((w, t))
                except Exception as e:
                    print(f"[MASTER] Failed to poll W{w.server_id}: {e}")

            if not reports:
                time.sleep(MASTER_POLL_INTERVAL)
                continue

            times = [t for (_, t) in reports]
            avg = sum(times) / len(times)

            # compute and apply corrections (avg - worker_time)
            for (w, t) in reports:
                corr = avg - t
                # safety bound on correction magnitude to simulate conservative adjust
                max_adj = 5.0
                adj = max(-max_adj, min(max_adj, corr))
                w.apply_correction(adj)
                print(f"[MASTER] Applied correction {adj:+.3f}s to W{w.server_id} (raw diff {corr:+.3f})")

            print(f"[MASTER] Sync done: avg_time={avg:.3f}")
            time.sleep(MASTER_POLL_INTERVAL)

class CentralLogManager:
    def __init__(self, workers):
        self.workers = workers
        self.central_logs = []
        self.lock = threading.Lock()
        self.running = True

    def merge_and_store(self):
        # read all logs from workers and compute synchronized timestamp
        merged = []
        for w in self.workers:
            worker_logs = w.get_and_clear_logs()
            for entry in worker_logs:
                # approximate synchronized timestamp:
                # sync_ts = raw_ts + applied_correction_at_send
                sync_ts = entry["raw_ts"] + entry.get("applied_corr_at_send", 0.0)
                merged.append({
                    "server_id": entry["server_id"],
                    "event": entry["event"],
                    "raw_ts": entry["raw_ts"],
                    "sync_ts": sync_ts,
                    "recv_by_collector_at": entry["recv_by_collector_at"]
                })

        # sort by sync_ts then server_id
        merged.sort(key=lambda x: (x["sync_ts"], x["server_id"]))
        with self.lock:
            self.central_logs = merged

    def pretty_print(self):
        with self.lock:
            logs = list(self.central_logs)
        print("\n=== CENTRALIZED LOG VIEW (BERKELEY) ===")
        print(f"{'Order':<6} {'Server':<6} {'Sync Time':<25} {'Raw Time':<25} {'Event'}")
        print("-" * 100)
        for i, l in enumerate(logs, 1):
            sync_str = datetime.fromtimestamp(l["sync_ts"]).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            raw_str = datetime.fromtimestamp(l["raw_ts"]).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"{i:<6} {l['server_id']:<6} {sync_str:<25} {raw_str:<25} {l['event']}")
        print("-" * 100 + "\n")

def worker_loop(worker, stop_at):
    while time.time() < stop_at:
        time.sleep(random.uniform(*LOG_INTERVAL))
        worker.generate_log()

def master_loop(master, stop_at):
    # run until time is up
    while time.time() < stop_at:
        master.berkeley_loop()
        # master.berkeley_loop has sleep inside; but in case we break, continue
    master.running = False

def central_merge_loop(manager, stop_at):
    while time.time() < stop_at:
        manager.merge_and_store()
        manager.pretty_print()
        time.sleep(MERGE_PRINT_INTERVAL)
    manager.running = False

def simulate():
    print("=== DISTRIBUTED LOGGING WITH BERKELEY CLOCK SYNC ===")
    workers = [Worker(i+1) for i in range(NUM_SERVERS)]
    master = Master(workers)
    manager = CentralLogManager(workers)

    stop_at = time.time() + SIMULATION_DURATION

    # start workers
    wthreads = []
    for w in workers:
        t = threading.Thread(target=worker_loop, args=(w, stop_at), daemon=True)
        t.start()
        wthreads.append(t)

    # start master in its own thread (use a wrapper so master.berkeley_loop doesn't block forever)
    def master_wrapper():
        # master.berkeley_loop runs a loop; we implement periodic single sync to allow stopping
        print("[MASTER] wrapper started")
        while time.time() < stop_at:
            # one synchronization round:
            reports = []
            for wk in workers:
                try:
                    tval = wk.report_time_for_sync()
                    reports.append((wk, tval))
                except:
                    pass
            if reports:
                times = [t for (_, t) in reports]
                avg = sum(times) / len(times)
                for (wk, tval) in reports:
                    corr = avg - tval
                    # limit adjustment for safety
                    max_adj = 5.0
                    adj = max(-max_adj, min(max_adj, corr))
                    wk.apply_correction(adj)
                    print(f"[MASTER] Applied correction {adj:+.3f}s to W{wk.server_id} (raw diff {corr:+.3f})")
                print(f"[MASTER] Sync round done: avg_time={avg:.3f}")
            time.sleep(MASTER_POLL_INTERVAL)
        print("[MASTER] wrapper exiting")

    mthread = threading.Thread(target=master_wrapper, daemon=True)
    mthread.start()

    # start central merge printer
    cthread = threading.Thread(target=central_merge_loop, args=(manager, stop_at), daemon=True)
    cthread.start()

    # wait for workers to finish
    try:
        while time.time() < stop_at:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupted by user")

    # final merge & print
    manager.merge_and_store()
    manager.pretty_print()
    print("=== SIMULATION COMPLETE ===")

if __name__ == "__main__":
    simulate()
