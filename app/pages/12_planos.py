import streamlit as st

from app.ui import page_header

st.set_page_config(
    page_title="Planos · Ponte Nexus",
    layout="wide",
    page_icon="⭐",
)

page_header(
    "Planos e Assinatura",
    "Escolha o plano que melhor atende à sua necessidade",
)

_PIX_PRO      = "00020101021126710014br.gov.bcb.pix0136ae3fdded-5c67-4140-a4b3-abf8eb09ee320209Plano Pro520400005303986540529.005802BR5919GUSTAVO H L MARTINS6011LAGOA SANTA62070503***6304C521"
_PIX_BUSINESS = "00020101021126760014br.gov.bcb.pix0136ae3fdded-5c67-4140-a4b3-abf8eb09ee320214Plano Business520400005303986540579.005802BR5919GUSTAVO H L MARTINS6011LAGOA SANTA62070503***63045677"
_PIX_KEY      = "ae3fdded-5c67-4140-a4b3-abf8eb09ee32"

_current_plan = st.session_state.get("user_plan", "free")

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
    .nx-plan-card.atual {
        border-color: #FFD600;
        box-shadow: 0 0 14px #FFD60022;
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
    .nx-plan-badge-atual {
        display: inline-block;
        background: #FFD60022;
        color: #FFD600;
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

_SPACER = '<div style="height:2.1rem"></div>'

with col_free:
    _badge_free = '<div class="nx-plan-badge-atual">⭐ Seu plano atual</div>' if _current_plan == "free" else _SPACER
    _class_free = "nx-plan-card atual" if _current_plan == "free" else "nx-plan-card"
    st.markdown(
        f"""
        <div class="{_class_free}">
            {_badge_free}
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
    _badge_pro = '<div class="nx-plan-badge-atual">⭐ Seu plano atual</div>' if _current_plan == "pro" else '<div class="nx-plan-badge">Mais popular</div>'
    _class_pro = "nx-plan-card atual" if _current_plan == "pro" else "nx-plan-card destacado"
    st.markdown(
        f"""
        <div class="{_class_pro}">
            {_badge_pro}
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
    _badge_biz = '<div class="nx-plan-badge-atual">⭐ Seu plano atual</div>' if _current_plan == "business" else _SPACER
    _class_biz = "nx-plan-card atual" if _current_plan == "business" else "nx-plan-card"
    st.markdown(
        f"""
        <div class="{_class_biz}">
            {_badge_biz}
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

# ── Pagamento via Pix ──────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<span class="nx-section-label">Assinar via Pix</span>',
    unsafe_allow_html=True,
)
st.caption(
    "Copie o código Pix abaixo, abra o app do seu banco e use **Pix Copia e Cola**. "
    "Após o pagamento, envie o comprovante por WhatsApp ou e-mail para ativar seu plano."
)

tab_pro_pix, tab_biz_pix = st.tabs(["⚡ Plano Pro — R$ 29/mês", "🚀 Plano Business — R$ 79/mês"])

with tab_pro_pix:
    col_info, col_code = st.columns([1, 2], gap="large")
    with col_info:
        st.markdown("**Chave Pix (aleatória)**")
        st.code(_PIX_KEY, language=None)
        st.caption("Titular: Gustavo H L Martins")
        st.caption("Cidade: Lagoa Santa — MG")
    with col_code:
        st.markdown("**Código Pix Copia e Cola**")
        st.code(_PIX_PRO, language=None)
        st.caption("Copie o código acima e cole em **Pix → Copia e Cola** no seu banco.")

with tab_biz_pix:
    col_info2, col_code2 = st.columns([1, 2], gap="large")
    with col_info2:
        st.markdown("**Chave Pix (aleatória)**")
        st.code(_PIX_KEY, language=None)
        st.caption("Titular: Gustavo H L Martins")
        st.caption("Cidade: Lagoa Santa — MG")
    with col_code2:
        st.markdown("**Código Pix Copia e Cola**")
        st.code(_PIX_BUSINESS, language=None)
        st.caption("Copie o código acima e cole em **Pix → Copia e Cola** no seu banco.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Envio de comprovante ───────────────────────────────────────────────────────
st.info(
    "📲 Após o pagamento, envie o **comprovante** com seu **e-mail de cadastro** "
    "por WhatsApp ou e-mail para ativarmos seu plano em até 1 hora útil.",
    icon="💡",
)

col_wp, col_em, _ = st.columns([2, 2, 4])
with col_wp:
    st.link_button(
        "💬 Enviar comprovante via WhatsApp",
        url="https://wa.me/5531982273761?text=Ol%C3%A1%2C%20realizei%20o%20pagamento%20do%20Ponte%20Nexus%20e%20quero%20ativar%20meu%20plano.",
        use_container_width=True,
        type="primary",
    )
with col_em:
    st.link_button(
        "✉️ Enviar por e-mail",
        url="mailto:contato@pontenexus.com.br?subject=Comprovante%20Ponte%20Nexus",
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
