def channel(func):
    def wrapper(*args, **kwargs):
        if kwargs.get("ch"):
            ch = kwargs.get("ch")
        else:
            ch = args[1]
        print(f"ch {ch}")

        func(*args, **kwargs)

        print("=====================")

    return wrapper
