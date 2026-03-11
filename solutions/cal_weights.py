import numpy as np
import pandas as pd
from transmatrix import SignalMatrix
from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_factor_table
from qtools_sxzq.qdata import CDataDescriptor
from typedef import CSectorClassification


class CSectorIndexWeights(SignalStrategy):
    def __init__(
        self,
        data_desc_amt: CDataDescriptor,
        clsf: CSectorClassification,
        init_amt: pd.Series,
    ):
        self.data_desc_amt: CDataDescriptor
        self.clsf: CSectorClassification
        self.init_amt: pd.Series
        super().__init__(data_desc_amt, clsf, init_amt)
        self.sec_df = pd.DataFrame(self.clsf.instru_map).fillna(0)
        self.weight = np.sqrt(init_amt)
        self.nrm_wgt = pd.DataFrame()
        self.update_nrm_wgt()

    def init(self):
        self.subscribe_data("amt", self.data_desc_amt.to_args())
        self.add_scheduler(milestones=["16:00:00"], handler=self.update_weight)
        self.add_clock(milestones="15:00:00")
        self.create_factor_table(self.clsf.sectors)

    def update_weight(self):
        amt = self.amt.get_dict("turnover")
        self.weight = np.sqrt(pd.Series(amt))
        self.update_nrm_wgt()

    def update_nrm_wgt(self):
        raw_wgt = self.sec_df.mul(self.weight, axis=0)
        wgt_sum = raw_wgt.sum(axis=0)
        self.nrm_wgt = (raw_wgt / wgt_sum).fillna(0)

    def on_clock(self):
        for sector in self.clsf.sectors:
            self.update_factor(sector, self.nrm_wgt.loc[self.clsf.codes, sector])


def main_process_sector_index_weight(
    span: tuple[str, str],
    data_desc_amt: CDataDescriptor,
    data_desc_sec_idx_wgt: CDataDescriptor,
    clsf: CSectorClassification,
    init_amt: pd.Series,
):
    cfg = {
        "span": span,
        "codes": clsf.codes,
        "cache_data": False,
        "progress_bar": True,
    }

    # --- run
    mat = SignalMatrix(cfg)
    sector_index = CSectorIndexWeights(
        data_desc_amt=data_desc_amt,
        clsf=clsf,
        init_amt=init_amt,
    )
    sector_index.set_name("sector_index_weight")
    mat.add_component(sector_index)
    mat.init()
    mat.run()

    # --- save
    dst_path = f"{data_desc_sec_idx_wgt.db_name}.{data_desc_sec_idx_wgt.table_name}"
    create_factor_table(dst_path)
    sector_index.save_factors(dst_path)
    return 0
