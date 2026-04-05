from tools import get_csv_summary


def main() -> None:
    summary = get_csv_summary("sales.csv")
    print(summary)


if __name__ == "__main__":
    main()
