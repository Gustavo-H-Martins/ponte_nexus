from enum import Enum


class EntityType(str, Enum):
    PF = "PF"
    PJ = "PJ"


class TransactionType(str, Enum):
    RECEITA               = "receita"
    DESPESA               = "despesa"
    TRANSFERENCIA_PF_PJ   = "transferencia_pf_pj"
    TRANSFERENCIA_PJ_PF   = "transferencia_pj_pf"
    APORTE_PF_PJ          = "aporte_pf_pj"
    EMPRESTIMO_PF_PJ      = "emprestimo_pf_pj"
    DIVIDENDOS            = "dividendos"
    PRO_LABORE            = "pro_labore"
