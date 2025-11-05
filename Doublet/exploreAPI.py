def explore_api(obj):
    print("=== Methods ===")
    for name in dir(obj):
        if callable(getattr(obj, name)) and not name.startswith("_"):
            print(" •", name)
    print("\n=== Properties ===")
    for name in dir(obj):
        if not callable(getattr(obj, name)) and not name.startswith("_"):
            print(" •", name)
            