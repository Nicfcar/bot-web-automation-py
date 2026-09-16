"""
bot_web_automation.py
------------------------------------------------------------
Bot de automação web com Playwright: login, navegação e extração
de dados de forma resiliente (sem depender de sorte de timing).

Site alvo: https://the-internet.herokuapp.com — um site público
mantido justamente para treino de automação (QA/testing). As
credenciais usadas abaixo são de teste, públicas por design do
próprio site, não pertencem a ninguém.

Técnicas demonstradas:
  - Login automatizado com espera por elementos (sem sleeps fixos)
  - Espera explícita por mudança de URL como checkpoint confiável
  - Tratamento de timeout sem derrubar o script
  - Screenshot automático no momento da falha, pra debug
  - Modo "debug" (navegador visível, mais lento) vs modo "headless"
    (invisível, rápido — ideal pra automação agendada)
  - Log estruturado de cada etapa executada

Instalação:
    pip install playwright
    playwright install chromium

Uso:
    python bot_web_automation.py            # roda headless
    python bot_web_automation.py --debug    # roda com navegador visível
"""

import argparse
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ----------------- CONFIG -----------------
URL_LOGIN = "https://the-internet.herokuapp.com/login"

# Credenciais de teste públicas do próprio site (não são segredo).
USUARIO_TESTE = "tomsmith"
SENHA_TESTE = "SuperSecretPassword!"

PASTA_SAIDA = Path("saida")
# -------------------------------------------


def log(etapa: str) -> None:
    print(f"[passo] {etapa}")


def rodar_bot(headless: bool = True) -> bool:
    PASTA_SAIDA.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=150 if not headless else 0)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1) Login
            log("Abrindo página de login")
            page.goto(URL_LOGIN)

            page.locator("#username").fill(USUARIO_TESTE)
            page.locator("#password").fill(SENHA_TESTE)
            page.locator("button[type='submit']").click()

            # Espera a URL mudar pra área logada — mais confiável do que
            # esperar a rede "acalmar" (que pode nunca acontecer se o
            # site tiver qualquer chamada em background).
            log("Aguardando confirmação de login")
            page.wait_for_url("**/secure", timeout=15000)

            mensagem = page.locator("#flash").inner_text()
            log(f"Login confirmado: {mensagem.strip()}")

            # 2) Navega pra outra página de teste (carregamento dinâmico),
            # só pra demonstrar espera explícita por conteúdo assíncrono.
            log("Testando espera por conteúdo carregado dinamicamente")
            page.goto("https://the-internet.herokuapp.com/dynamic_loading/2")
            page.locator("#start button").click()

            resultado = page.locator("#finish h4")
            resultado.wait_for(state="visible", timeout=10000)
            log(f"Conteúdo dinâmico carregado: '{resultado.inner_text()}'")

            # 3) Salva print de sucesso como evidência
            page.screenshot(path=str(PASTA_SAIDA / "sucesso.png"))
            log("Print salvo em saida/sucesso.png")

            print("\nExecução concluída com sucesso!")
            return True

        except PWTimeout:
            print(f"\nAlgum elemento esperado não apareceu a tempo. "
                  f"URL no momento da falha: {page.url}")
            page.screenshot(path=str(PASTA_SAIDA / "erro_debug.png"))
            print("Print salvo em saida/erro_debug.png para investigação.")
            return False

        finally:
            browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot de automação web de demonstração (Playwright).")
    parser.add_argument("--debug", action="store_true", help="roda com navegador visível e mais devagar")
    args = parser.parse_args()

    sucesso = rodar_bot(headless=not args.debug)
    sys.exit(0 if sucesso else 1)
