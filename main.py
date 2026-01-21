import argparse
from qtools_sxzq.qcalendar import CCalendar


def parse_args(names: list[str]):
    arg_parser = argparse.ArgumentParser(description="This project is designed to create preprocess data by instrument")
    arg_parser.add_argument("command", type=str, choices=names)
    arg_parser.add_argument("--bgn", type=str, required=True, help="begin date, format = 'YYYYMMDD'")
    arg_parser.add_argument("--end", type=str, default=None, help="end date, format = 'YYYYMMDD'")
    return arg_parser.parse_args()


def validate_args(bgn_date: str, end_date: str, calendar: CCalendar, base_date: str) -> bool:
    if not calendar.is_trade_date(bgn_date) or not calendar.is_trade_date(end_date):
        print(f"[ERR] {bgn_date=:} or {end_date=:} is not in trade calendar, please check again.")
        return False
    if bgn_date <= base_date:
        print(f"[ERR] {bgn_date=:} is before {base_date=:}, please check again.")
        return False
    return True


if __name__ == "__main__":
    import sys
    from config import cfg, data_desc_pv
    from solutions.calculators import main_process_sector_index

    args = parse_args(names=list(cfg.classifications.keys()))
    bgn, end = args.bgn, args.end or args.bgn
    calendar = CCalendar(calendar_path=cfg.path_calendar)
    if not validate_args(bgn, end, calendar=calendar, base_date=cfg.index_base.date):
        sys.exit(-1)

    span: tuple[str, str] = (bgn, end)
    sector_classification = cfg.classifications[args.command]
    data_desc_pv.codes = sector_classification.codes
    main_process_sector_index(
        span=span,
        data_desc_pv=data_desc_pv,
        data_desc_sec_idx=sector_classification.save_table(cfg.dbs.user),
        instru_map=sector_classification.instru_map,
    )
