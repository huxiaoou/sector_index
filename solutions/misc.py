import numpy as np
import pandas as pd
from qtools_sxzq.qwidgets import SFG, SFR, SFY
from qtools_sxzq.qcalendar import CCalendar
from qtools_sxzq.qdataviewer import fetch
from qtools_sxzq.qdata import CDataDescriptor
from typedef import CCfgIndexBase


def get_span(bgn_date: str, end_date: str, calendar: CCalendar) -> tuple[str, str]:
    prev_date = calendar.get_next_date(bgn_date, shift=-1)
    bgn_str = f"{prev_date} 21:00:00"
    end_str = f"{end_date} 15:00:00"
    return bgn_str, end_str


def get_init_price(
    bgn_date: str,
    calendar: CCalendar,
    index_base: CCfgIndexBase,
    data_desc_sec_idx: CDataDescriptor,
) -> pd.Series:
    prev_date = calendar.get_next_date(bgn_date, shift=-1)
    if prev_date == index_base.date:
        init_price = pd.Series(data=index_base.value, index=data_desc_sec_idx.codes)
    else:
        buff_data: pd.DataFrame = fetch(
            lib=data_desc_sec_idx.db_name,
            table=data_desc_sec_idx.table_name,
            names=["code", "`close`"],
            conds=f"datetime == '{prev_date[0:4]}-{prev_date[4:6]}-{prev_date[6:8]} 15:00:00'",
        )
        init_price: pd.Series = pd.Series(dtype=np.float64)
        if not buff_data.empty:
            init_price = buff_data.set_index("code").loc[data_desc_sec_idx.codes, "close"]  # type:ignore
        if len(init_price) < len(data_desc_sec_idx.codes):
            print(
                f"[{SFR('WRN')}] Init prices are not found @{SFY(prev_date)} for bgn={SFY(bgn_date)}, init_price is:\n{init_price}"
            )
            raise ValueError
    print(f"Init price @ {SFG(prev_date)} for bgn={SFG(bgn_date)} is:\n{init_price}")
    return init_price


def get_init_amt(
    bgn_date: str,
    calendar: CCalendar,
    data_desc_pv: CDataDescriptor,
) -> pd.Series:
    prev_date = calendar.get_next_date(bgn_date, shift=-1)
    buff_data: pd.DataFrame = fetch(
        lib=data_desc_pv.db_name,
        table=data_desc_pv.table_name,
        names=["code", "turnover"],
        conds=f"datetime == '{prev_date[0:4]}-{prev_date[4:6]}-{prev_date[6:8]} 15:00:00'",
    )
    raw_data = buff_data.set_index("code")["turnover"].to_dict()
    init_amt = pd.Series({code: raw_data.get(code, 0) for code in data_desc_pv.codes})
    return init_amt
