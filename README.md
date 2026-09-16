# bot-web-automation

Bot de automação web feito com [Playwright](https://playwright.dev/python/) para demonstrar
técnicas de automação resiliente de sites: login automatizado, espera explícita por
elementos (em vez de `sleep()` fixo), tratamento de timeout sem quebrar a execução, e
captura de evidências (screenshots) em cada etapa.

Site usado como alvo: [the-internet.herokuapp.com](https://the-internet.herokuapp.com/), mantido
publicamente para treino de automação e testes (QA). As credenciais usadas no script são as
credenciais de demonstração do próprio site — públicas por design, não pertencem a ninguém.

## O que o script faz

1. Acessa a página de login e autentica com as credenciais de teste
2. Confirma o login esperando a URL mudar para a área autenticada (checkpoint confiável,
   em vez de depender da rede "ficar quieta")
3. Navega até uma página de carregamento dinâmico e espera o conteúdo assíncrono aparecer
4. Salva um screenshot como evidência de sucesso
5. Em caso de falha em qualquer etapa, salva um screenshot do estado da página e informa
   a URL no momento do erro, pra facilitar o debug

## Como rodar

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install playwright
playwright install chromium

python bot_web_automation.py --debug   # com navegador visível
python bot_web_automation.py           # modo headless (silencioso)
```

## Estrutura

```
bot_web_automation.py   # script principal
saida/                  # criado automaticamente, guarda os screenshots
```

## Técnicas demonstradas

- **Espera baseada em estado, não em tempo**: em vez de `time.sleep(5)`, o script espera
  por sinais reais de que a página está pronta (mudança de URL, elemento visível).
- **Seletores robustos**: uso de `id` real do elemento em vez de casar por texto solto,
  que pode quebrar se o texto estiver fragmentado em múltiplos elementos de HTML.
- **Falha graciosa**: timeouts são capturados e tratados, com log e screenshot, em vez de
  o script simplesmente quebrar com stack trace.
- **Modo debug vs produção**: flag `--debug` alterna entre navegador visível (para
  desenvolvimento) e headless (para rodar agendado/silencioso).
