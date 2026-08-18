
# Example third-party module
def install(runtime):
    if getattr(runtime, "verbose", False):
        print("[MODULE] Example module installed into runtime.")
