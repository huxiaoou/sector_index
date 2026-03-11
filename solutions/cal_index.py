import numpy as np
import pandas as pd
from transmatrix import SignalMatrix
from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_factor_table
from qtools_sxzq.qdata import CDataDescriptor
from typedef import TFreq, CSectorClassification


class _CSectorIndex(SignalStrategy):
    def __init__(
        self,
        data_desc_md: CDataDescriptor,
        data_desc_amt: CDataDescriptor,
        clsf: CSectorClassification,
        init_price: pd.Series,
        init_amt: pd.Series,
    ):
        self.data_desc_md: CDataDescriptor
        self.data_desc_amt: CDataDescriptor
        self.clsf: CSectorClassification
        self.init_price: pd.Series
        self.init_amt: pd.Series
        super().__init__(data_desc_md, data_desc_amt, clsf, init_price, init_amt)
        self.sec_df = pd.DataFrame(self.clsf.instru_map)[init_price.index].fillna(0)
        self.weight = np.sqrt(init_amt)
        self.nrm_wgt = pd.DataFrame()
        self.update_nrm_wgt()

    def init(self):
        self.subscribe_data("md", self.data_desc_md.to_args())
        self.subscribe_data("amt", self.data_desc_amt.to_args())
        self.add_scheduler(milestones=["16:00:00"], handler=self.update_weight)
        self.create_factor_table(["ret", "close"])

    def update_weight(self):
        amt = self.amt.get_dict("turnover")
        self.weight = np.sqrt(pd.Series(amt))
        self.update_nrm_wgt()

    def update_nrm_wgt(self):
        raw_wgt = self.sec_df.mul(self.weight, axis=0)
        wgt_sum = raw_wgt.sum(axis=0)
        self.nrm_wgt = (raw_wgt / wgt_sum).fillna(0)

    def on_clock(self):
        ret = self.md.get_dict("pre_close_ret")
        r_sorted = pd.Series(ret).fillna(0) @ self.nrm_wgt
        self.init_price *= 1 + r_sorted
        self.update_factor("ret", r_sorted.to_numpy())
        self.update_factor("close", self.init_price.to_numpy())


class CSectorIndexD(_CSectorIndex):
    def init(self):
        super().init()
        self.add_clock(milestones="15:00:00")


class CSectorIndexM(_CSectorIndex):
    def init(self):
        super().init()
        self.add_scheduler(with_data="md", handler=self.on_clock)


def main_process_sector_index(
    span: tuple[str, str],
    data_desc_md: CDataDescriptor,
    data_desc_amt: CDataDescriptor,
    data_desc_sec_idx: CDataDescriptor,
    clsf: CSectorClassification,
    init_price: pd.Series,
    init_amt: pd.Series,
    freq: TFreq,
):
    cfg = {
        "span": span,
        "codes": data_desc_sec_idx.codes,
        "cache_data": False,
        "progress_bar": True,
    }

    # --- run
    mat = SignalMatrix(cfg)
    strategy_type: type[_CSectorIndex]
    if freq == "d":
        strategy_type = CSectorIndexD
    elif freq == "m":
        strategy_type = CSectorIndexM
    else:
        raise ValueError(f"[ERR] Invalid level = {freq}")
    sector_index = strategy_type(
        data_desc_md=data_desc_md,
        data_desc_amt=data_desc_amt,
        clsf=clsf,
        init_price=init_price,
        init_amt=init_amt,
    )
    sector_index.set_name("sector_index")
    mat.add_component(sector_index)
    mat.init()
    mat.run()

    # --- save
    dst_path = f"{data_desc_sec_idx.db_name}.{data_desc_sec_idx.table_name}"
    create_factor_table(dst_path)
    sector_index.save_factors(dst_path)
    return 0
