from enum import Enum


class EntityType(str, Enum):
    PF = "PF"
    PJ = "PJ"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER_PF_TO_PJ = "transfer_pf_to_pj"
    TRANSFER_PJ_TO_PF = "transfer_pj_to_pf"
    INVESTMENT_PF_TO_PJ = "investment_pf_to_pj"
    LOAN_PF_TO_PJ = "loan_pf_to_pj"
    DIVIDEND_DISTRIBUTION = "dividend_distribution"
    PRO_LABORE = "pro_labore"
