# Papocobot

Bot de rojão em texto para Telegram, separado do Bandejão e do assistente Hermes.

**Bot do projeto:** [@Papocoobot](https://t.me/Papocoobot), nome exibido **Papocobot2**. Abra a conversa, toque em Iniciar e envie `/acende`.

## Comportamento

### /acende

O comando `/acende` envia **seis mensagens**, nesta ordem, com uma pausa de um segundo entre elas:

```text
Fizzzzzz

pra pra pra pra pra pra pra pra

pra pra

pra

pra

POOOOOWW
```

### /bomba_de_mil

Envia as falas abaixo em mensagens separadas, com uma pausa de um segundo entre elas, e termina com uma explosão compacta em uma sexta mensagem de texto simples:

```text
Fiiiiiizzzzzzzzzzzzzzzzzzz

Zzzzzzzzzzzz

Zzzzzzzzzzzzz

Zzzzzzzzzzzzz ZZZZ

CATAPUUUUUMMMMMM
```

**Explosão final:** ˗ˏˋ ⋆✴︎˚｡⋆ˎˊ˗

Símbolo Unicode fornecido e escolhido pelo usuário. É enviado como texto simples, sem HTML ou bloco monoespaçado. Seus caracteres, espaços e o seletor de apresentação textual (U+FE0E) são preservados.

Em grupos: `/bomba_de_mil@Papocoobot`. Os dois efeitos compartilham o intervalo de proteção por conversa, evitando sequências sobrepostas.

### Regras comuns

- `Fizzzzzz` é uma personalização solicitada por Leonardo, não uma característica atribuída ao original.
- A sequência é fixa, sem o agrupamento aleatório nem o final `...` do módulo Ruby.
- `/start` e `/ajuda` mostram as instruções.
- Em grupos, use `/acende@Papocoobot` para direcionar o comando à instância do projeto. Se criar outra instância, substitua pelo @usuário correspondente.
- Intervalo mínimo de dez segundos entre acionamentos da mesma conversa, contado desde o início. Acionamentos repetidos são ignorados silenciosamente.
- Uma sequência em andamento não se sobrepõe a outra na mesma conversa. Conversas diferentes são processadas concorrentemente.
- O bot não exige privilégios de administrador; precisa de permissão para enviar mensagens.
- Não há IA, banco de dados, persistência de mensagens ou dependências da USP. O controle de intervalo fica em memória e é reiniciado junto com o processo.
- Se o Telegram recusar um envio, a sequência para, libera a conversa e registra somente o tipo do erro. O bot não tenta reenviar automaticamente uma sequência incompleta.

## Origem

Clone de `gp2112/bandejao-bot`, commit `d778ec7386d50ba7343b67fea8e7718572f27374`. O código Ruby de referência foi preservado em `legacy/bandejao/`. Ele não é executado pelo novo bot. Consulte `NOTICE.md` e `LICENSE`.

A implementação Python é independente. Não foi comprovado vínculo entre o repositório de referência e a conta original `@Papocobot`.

## Instalação

Validado com Python 3.11. Instalação isolada:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip check
.venv/bin/python -m unittest -v
```

`requirements.txt` fixa a dependência direta; `requirements.lock` registra também suas dependências transitivas utilizadas nos testes.

## Criar e ativar o bot

1. Abra o perfil oficial `@BotFather` e use `/newbot`.
2. Use `Papocobot` como nome exibido e escolha um @usuário disponível terminado em `bot`.
3. Guarde o token em local privado. Não o publique em repositórios nem o reutilize em outro serviço.
4. Para executar manualmente em Bash, sem colocar o token no histórico:

```bash
read -rsp 'Token do novo bot: ' PAPOCO_BOT_TOKEN
export PAPOCO_BOT_TOKEN
.venv/bin/python papoco.py
```

Ao iniciar, atualizações antigas pendentes são descartadas para evitar rajadas de respostas atrasadas. Só deve existir uma instância de polling para este token.

O modo de privacidade pode permanecer habilitado; prefira o comando com @usuário nos grupos. Não é necessário ler as outras mensagens do grupo.

## Serviço no servidor

O arquivo `deploy/papocobot.service` é o modelo para executar o bot em `/home/hermes/projects/Papocobot`. Na instância do projeto, o serviço independente `papocobot.service` está configurado para inicialização automática. Para consultar o estado no servidor:

```bash
systemctl is-active papocobot.service
systemctl is-enabled papocobot.service
```

Para ativação, é necessário primeiro criar `.env` com `PAPOCO_BOT_TOKEN=...`, permissões `0600` e proprietário `hermes`. O modelo sem segredo é `.env.example`. O systemd lê esse arquivo; a execução manual exige exportar a variável como acima.

Nenhum serviço do Hermes precisa ser reiniciado. Se o projeto for movido, ajuste os caminhos da unidade systemd.

## Estado da validação

Os testes verificam a sequência exata, pausas, controle de intervalo, bloqueio de sobreposição, liberação após erro, comandos direcionados ao próprio bot, rejeição de comandos para outro bot e proteção das mensagens de erro. O roteamento real da biblioteca Telegram é exercitado com transporte simulado, sem envio à API externa.

A autenticação do bot e o cadastro dos comandos foram verificados na API real do Telegram. Para validar o fluxo ponta a ponta, envie `/acende` ao bot e confira as seis mensagens. Os testes locais e a confirmação de processo ativo não substituem essa verificação na conversa.
