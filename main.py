import argparse
from qtools_sxzq.qcalendar import CCalendar


def parse_args(names: list[str]):
    arg_parser = argparse.ArgumentParser(description="This project is designed to create preprocess data by instrument")
    arg_parser.add_argument("command", type=str, choices=names)
    arg_parser.add_argument("--freq", type=str, choices=("d", "m"), required=True)
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
    from logbook import Logger, StreamHandler, set_datetime_format
    from qtools_sxzq.qwidgets import SFG
    from config import cfg, data_desc_pv, data_desc_pv1m
    from solutions.calculators import main_process_sector_index
    from solutions.misc import get_init_price, get_init_amt, get_span

    StreamHandler(sys.stdout).push_application()
    set_datetime_format("local")
    logger = Logger(f"{SFG('SZST')}")

    calendar = CCalendar(calendar_path=cfg.path_calendar)

    args = parse_args(names=list(cfg.classifications.keys()))
    bgn, end = args.bgn, args.end or args.bgn
    if not validate_args(bgn, end, calendar=calendar, base_date=cfg.index_base.date):
        sys.exit(-1)

    span: tuple[str, str] = get_span(bgn, end, calendar=calendar)
    clsf = cfg.classifications[args.command]
    data_desc_pv.codes = clsf.codes
    data_desc_pv1m.codes = clsf.codes
    data_desc_md = data_desc_pv if args.freq == "d" else data_desc_pv1m
    data_desc_sec_idx = clsf.get_save_data_desc(cfg.dbs.user, args.freq)

    logger.info(f"Loading init price for {SFG(clsf.comb_name(args.freq))}")
    init_price = get_init_price(
        bgn_date=bgn,
        calendar=calendar,
        index_base=cfg.index_base,
        data_desc_sec_idx=data_desc_sec_idx,
    )
    init_amt = get_init_amt(
        bgn_date=bgn,
        calendar=calendar,
        data_desc_pv=data_desc_pv,
    )

    logger.info(f"Calculation for {SFG(clsf.comb_name(args.freq))}")
    main_process_sector_index(
        span=span,
        data_desc_md=data_desc_md,
        data_desc_amt=data_desc_pv,
        data_desc_sec_idx=data_desc_sec_idx,
        clsf=clsf,
        init_price=init_price,
        init_amt=init_amt,
        freq=args.freq,
    )
    logger.info(f"{SFG(clsf.comb_name(args.freq))} finishes")
