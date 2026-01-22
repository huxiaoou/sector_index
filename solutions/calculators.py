import numpy as np
import pandas as pd
from transmatrix import SignalMatrix
from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_factor_table
from qtools_sxzq.qdata import CDataDescriptor
from typedef import TInstruMap, TLevel


def cal_wgt_ret(ret: pd.Series, wgt: pd.Series) -> float:
    if (s := wgt.sum()) > 0:
        return ret @ wgt / s
    return 0


class _CSectorIndex(SignalStrategy):
    def __init__(self, data_desc_pv: CDataDescriptor, instru_map: TInstruMap, init_price: pd.Series):
        self.data_desc_pv: CDataDescriptor
        self.instru_map: TInstruMap
        self.init_price: pd.Series
        super().__init__(data_desc_pv, instru_map, init_price)

    def init(self):
        raise NotImplementedError

    def on_clock(self):
        amt = self.pv.get_dict("turnover")
        ret = self.pv.get_dict("pre_close_ret")
        mkt_data = pd.DataFrame(
            {
                "amt": amt,
                "ret": ret,
            }
        ).fillna(0)
        mkt_data["sector"] = mkt_data.index.map(lambda z: self.instru_map.get(z))
        mkt_data["rel_wgt"] = np.sqrt(mkt_data["amt"])
        selected_data = mkt_data.dropna(axis=0, subset=["sector"], how="any")
        r = selected_data.groupby(by="sector").apply(lambda z: cal_wgt_ret(z["ret"], z["rel_wgt"]))
        r_sorted = r[self.codes]
        self.init_price *= 1 + r_sorted
        self.update_factor("ret", r_sorted.to_numpy())
        self.update_factor("close", self.init_price.to_numpy())


class CSectorIndexD(_CSectorIndex):
    def init(self):
        self.add_clock(milestones="15:00:00")
        self.subscribe_data("pv", self.data_desc_pv.to_args())
        self.create_factor_table(["ret", "close"])


class CSectorIndexM(_CSectorIndex):
    def init(self):
        self.add_scheduler(freq="1min", handler=self.on_clock)
        self.subscribe_data("pv", self.data_desc_pv.to_args())
        self.create_factor_table(["ret", "close"])


def main_process_sector_index(
    span: tuple[str, str],
    data_desc_pv: CDataDescriptor,
    data_desc_sec_idx: CDataDescriptor,
    instru_map: TInstruMap,
    init_price: pd.Series,
    lvl: TLevel,
):
    cfg = {
        "span": span,
        "codes": data_desc_sec_idx.codes,
        "cache_data": False,
        "progress_bar": True,
    }

    # --- run
    mat = SignalMatrix(cfg)
    if lvl == "lvl1":
        sector_index = CSectorIndexD(
            data_desc_pv=data_desc_pv,
            instru_map=instru_map,
            init_price=init_price,
        )
    elif lvl == "lvl2":
        sector_index = CSectorIndexM(
            data_desc_pv=data_desc_pv,
            instru_map=instru_map,
            init_price=init_price,
        )
    else:
        raise ValueError(f"[ERR] Invalid level = {lvl}")
    sector_index.set_name("sector_index")
    mat.add_component(sector_index)
    mat.init()
    mat.run()

    # --- save
    dst_path = f"{data_desc_sec_idx.db_name}.{data_desc_sec_idx.table_name}"
    create_factor_table(dst_path)
    sector_index.save_factors(dst_path)
    return 0
