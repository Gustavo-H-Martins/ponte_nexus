import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app.ui import page_header

st.set_page_config(
    page_title="Planos · Ponte Nexus",
    layout="wide",
    page_icon="💠",
)

page_header(
    "Planos e Assinatura",
    "Escolha o plano que melhor atende à sua necessidade",
)

# ── Cards de plano ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .nx-plan-card {
        border: 1px solid #1E3A5F;
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        background: #112240;
        height: 100%;
    }
    .nx-plan-card.destacado {
        border-color: #64FFDA;
        box-shadow: 0 0 18px #64FFDA22;
    }
    .nx-plan-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #CCD6F6;
        margin-bottom: 0.3rem;
    }
    .nx-plan-price {
        font-size: 2rem;
        font-weight: 700;
        color: #64FFDA;
        margin: 0.6rem 0;
    }
    .nx-plan-price small {
        font-size: 0.85rem;
        color: #8892B0;
        font-weight: 400;
    }
    .nx-plan-badge {
        display: inline-block;
        background: #64FFDA22;
        color: #64FFDA;
        border-radius: 6px;
        padding: 0.15rem 0.6rem;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .nx-feature-ok  { color: #64FFDA; margin-right: 0.4rem; }
    .nx-feature-no  { color: #FF6B6B; margin-right: 0.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

col_free, col_pro, col_business = st.columns(3, gap="large")

with col_free:
    st.markdown(
        """
        <div class="nx-plan-card">
            <div class="nx-plan-title">Gratuito</div>
            <div class="nx-plan-price">R$ 0<small>/mês</small></div>
            <p style="color:#8892B0;font-size:0.82rem;margin-bottom:1rem;">
                Ideal para quem está começando a organizar as finanças.
            </p>
            <ul style="list-style:none;padding:0;font-size:0.87rem;line-height:2rem;">
                <li><span class="nx-feature-ok">✔</span> Até 100 lançamentos/mês</li>
                <li><span class="nx-feature-ok">✔</span> 1 empresa (PJ)</li>
                <li><span class="nx-feature-ok">✔</span> Dashboard e Extrato</li>
                <li><span class="nx-feature-ok">✔</span> Importação CSV/XLSX/JSON</li>
                <li><span class="nx-feature-no">✘</span> Exportação PDF</li>
                <li><span class="nx-feature-no">✘</span> Múltiplas empresas</li>
                <li><span class="nx-feature-no">✘</span> Suporte prioritário</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_pro:
    st.markdown(
        """
        <div class="nx-plan-card destacado">
            <div class="nx-plan-badge">Mais popular</div>
            <div class="nx-plan-title">Pro</div>
            <div class="nx-plan-price">R$ 29<small>/mês</small></div>
            <p style="color:#8892B0;font-size:0.82rem;margin-bottom:1rem;">
                Para profissionais autônomos e sócios que querem controle total.
            </p>
            <ul style="list-style:none;padding:0;font-size:0.87rem;line-height:2rem;">
                <li><span class="nx-feature-ok">✔</span> Lançamentos ilimitados</li>
                <li><span class="nx-feature-ok">✔</span> Até 3 empresas (PJ)</li>
                <li><span class="nx-feature-ok">✔</span> Todos os relatórios</li>
                <li><span class="nx-feature-ok">✔</span> Importação CSV/XLSX/JSON</li>
                <li><span class="nx-feature-ok">✔</span> Exportação Excel e PDF</li>
                <li><span class="nx-feature-ok">✔</span> Metas e Orçamento</li>
                <li><span class="nx-feature-no">✘</span> Suporte prioritário</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_business:
    st.markdown(
        """
        <div class="nx-plan-card">
            <div class="nx-plan-title">Business</div>
            <div class="nx-plan-price">R$ 79<small>/mês</small></div>
            <p style="color:#8892B0;font-size:0.82rem;margin-bottom:1rem;">
                Para escritórios contábeis e gestão de múltiplos CNPJs.
            </p>
            <ul style="list-style:none;padding:0;font-size:0.87rem;line-height:2rem;">
                <li><span class="nx-feature-ok">✔</span> Lançamentos ilimitados</li>
                <li><span class="nx-feature-ok">✔</span> Empresas ilimitadas</li>
                <li><span class="nx-feature-ok">✔</span> Todos os relatórios</li>
                <li><span class="nx-feature-ok">✔</span> Importação e Exportação completas</li>
                <li><span class="nx-feature-ok">✔</span> Metas e Orçamento</li>
                <li><span class="nx-feature-ok">✔</span> Suporte prioritário por e-mail</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Links de pagamento ─────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<span class="nx-section-label">Assinar agora</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "Entre em contato para ativar seu plano. Aceitamos **PIX**, **cartão de crédito** e **boleto**."
)

col_wp, col_em, _ = st.columns([2, 2, 4])
with col_wp:
    st.link_button(
        "💬 WhatsApp",
        url="https://wa.me/5531982273761?text=Olá%2C%20tenho%20interesse%20no%20Ponte%20Nexus",
        use_container_width=True,
    )
with col_em:
    st.link_button(
        "✉️ E-mail",
        url="mailto:contato@pontenexus.com.br?subject=Interesse%20no%20Plano%20Pro",
        use_container_width=True,
    )

st.divider()

# ── Perguntas frequentes sobre planos ──────────────────────────────────────────
st.markdown("## ❓ Dúvidas sobre os planos")

with st.expander("Posso cancelar a qualquer momento?"):
    st.markdown("""
    Sim. Não há fidelidade mínima. O cancelamento encerra sua assinatura ao fim do período pago.
    """)

with st.expander("O que acontece com meus dados ao cancelar?"):
    st.markdown("""
    Seus dados ficam disponíveis por 30 dias após o cancelamento para exportação.
    Após esse período, são removidos dos nossos servidores.
    """)

with st.expander("Como funciona o período de teste?"):
    st.markdown("""
    Novos usuários têm **14 dias** de acesso ao plano Pro sem precisar de cartão de crédito.
    Ao final do período, o plano é convertido automaticamente para o Gratuito.
    """)

with st.expander("Aceita nota fiscal?"):
    st.markdown("""
    Sim. Emitimos NF-e para todos os planos pagos. Informe seu CNPJ no momento da assinatura.
    """)
