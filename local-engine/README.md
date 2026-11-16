# FreeClaw Local Engine 0.4

Aplicativo gráfico em Python/Tkinter para Windows. Não é hospedado no GitHub Pages.

## Como utilizar

1. Baixe os três arquivos desta pasta: `app.py`, `engine.py` e `iniciar-freeclaw.bat` e deixe-os juntos no computador. Requer Python 3.10+ com Tkinter (nenhum pacote pip obrigatório).
2. Abra `iniciar-freeclaw.bat` com dois cliques, sem privilégios administrativos.
3. No site do FreeClaw AI Studio, acesse **AI Developer** e faça download do pacote `.md`.
4. No aplicativo local clique em **Escolher pacote .md**.
5. Digite o ID de um modelo da NVIDIA Build com acesso disponível na sua conta; informe a chave API localmente, no campo oculto.
6. Use **Pré-validar sem gastar tokens**. Revise privacidade e, se estiver de acordo, clique em **Enviar à NVIDIA (confirmar)**.
7. Revise a resposta e use **Salvar resposta .md**.

## Proteções e limites

- A chave é mantida só na memória; não é gravada em arquivos ou exposta no GitHub Pages. É enviada à NVIDIA apenas para autenticar a chamada.
- Não executa código gerado, não instala dependências, não publica no GitHub nem altera os documentos SPECTION.
- O filtro de tokens é parcial: revise manualmente informações sensíveis e não use dados reais de estudantes.
- NVIDIA pode impor cotas, alterar modelos e bloquear acesso; timeout não significa zero consumo.
- O site estático público **não acessa** o aplicativo local. Esta versão é um companion gráfico separado.
- A saída do modelo é sempre um rascunho que exige revisão e aprovação humana.

## Testes

Na raiz do repositório: `python -m unittest discover -s tests -p 'test_local_engine.py'`.
