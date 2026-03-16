from enum import Enum


class EntityType(str, Enum):
    PF = "PF"
    PJ = "PJ"


class AccountType(str, Enum):
    """Tipos de conta financeira suportados pelo sistema."""
    CONTA_BANCARIA = "conta_bancaria"
    CAIXA          = "caixa"
    COFRE          = "cofre"
    INVESTIMENTOS  = "investimentos"
    PROVISAO       = "provisao"
    OUTRA          = "outra"


class TransactionType(str, Enum):
    RECEITA               = "receita"
    DESPESA               = "despesa"
    TRANSFERENCIA_PF_PJ   = "transferencia_pf_pj"
    TRANSFERENCIA_PJ_PF   = "transferencia_pj_pf"
    APORTE_PF_PJ          = "aporte_pf_pj"
    EMPRESTIMO_PF_PJ      = "emprestimo_pf_pj"
    DIVIDENDOS            = "dividendos"
    PRO_LABORE            = "pro_labore"


class IncomeSourceType(str, Enum):
    """Tipos de fonte de renda para classificação de receitas nomeadas."""
    SALARIO      = "salario"
    FREELANCE    = "freelance"
    DIVIDENDOS   = "dividendos"
    PRO_LABORE   = "pro_labore"
    INVESTIMENTO = "investimento"
    ALUGUEL      = "aluguel"
    OUTRO        = "outro"


class UserRole(str, Enum):
    """Papel do usuário no sistema."""
    ADMIN = "admin"
    USER  = "user"


class UserPlan(str, Enum):
    """Plano de acesso do usuário."""
    FREE = "free"
    PRO  = "pro"
