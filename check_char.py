def check_char(chapters: list[str], current_usage_path, max_usage, start: int) -> bool:
    """
    Check if exceeds tts limit
    -> True if proceed and within limit
    """
    total_chars = 0
    total_bytes = 0

    # get total char
    for idx, chap in enumerate(chapters, start=start):
        # print(f"sample chap {idx}: {chap[:100]}\n")
        chars = len(chap)
        bts = len(chap.encode("utf-8"))
        total_chars += chars
        total_bytes += bts
        # print(f"Chap {idx}, {chars:,}: chars, {bts:,}: bytes")

    print(f"\nTOTAL across {len(chapters)} files:")
    print(f"  {total_chars:,} characters")
    print(f"  {total_bytes:,} bytes")
    user = ""

    # store new usage char if proceed
    with open(current_usage_path, "r+") as usage:
        current_usage = int(usage.read())
        new_usage_char = current_usage + total_chars
        print(f"current usage char: {current_usage}")
        print(f"new usage char: {new_usage_char}")
        print(f"remaining char if proceed: {max_usage - new_usage_char}")
        if new_usage_char >= max_usage:
            return False

        user = input("proceed?(y/n) ").lower()
        if user == "y":
            usage.truncate(0)
            usage.write(str(new_usage_char))

    return user == 'y'