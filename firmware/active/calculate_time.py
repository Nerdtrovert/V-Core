
#!/usr/bin/env python3

# V-Core: Convert CPU cycle counts into elapsed-time estimates.

FREQUENCIES = {

    "160 MHz": 160_000_000,

    "240 MHz": 240_000_000,

}

# Median cycle counts collected from our experiments.

measurements = {

    "64-element dot product": {

        "cycles": 1974,

    },

    "1024-element dot product": {

        "cycles": 31716,

    },

}

print("=" * 65)

print("V-CORE: CYCLE COUNT -> EXECUTION TIME")

print("=" * 65)

for workload, data in measurements.items():

    cycles = data["cycles"]

    print(f"\n{workload}")

    print(f"Median cycles: {cycles:,}")

    print("-" * 50)

    for label, frequency in FREQUENCIES.items():

        seconds = cycles / frequency

        microseconds = seconds * 1_000_000

        nanoseconds = seconds * 1_000_000_000

        print(f"{label}:")

        print(f"  Execution time: {microseconds:.4f} us")

        print(f"  Execution time: {nanoseconds:.2f} ns")

print("\n" + "=" * 65)

print("NOTE: Times are calculated from cycle counts,")

print("not independently measured wall-clock durations.")

print("=" * 65)

