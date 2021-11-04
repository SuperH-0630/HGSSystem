def mysql_str(text: str):
    return (text
            .replace("\n", r"\n")
            .replace(r"'", r"\'")
            .replace(r'"', r'\"')
            .replace("\b", r"\b")
            .replace("\r", "")
            .replace("\t", r"\t"))
