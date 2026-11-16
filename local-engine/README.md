# FreeClaw Local Engine 0.5

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

## 0.5 - Gerador de projetos para revisão

1. Abra o aplicativo e selecione o pacote SPECTION exportado do AI Studio.
2. Clique em **Preparar pedido de arquivos** para solicitar à NVIDIA blocos nomeados `### Arquivo: src/arquivo.py` seguidos por código `python` cercado por três crases.
3. Revise e autorize **Enviar à NVIDIA**. Esta operação utiliza cota do seu provedor.
4. Quando houver uma proposta, clique em **Revisar arquivos Python**, escolha um arquivo e leia o código integral.
5. Clique em **Exportar ZIP revisável (não executa)**. O ZIP inclui `REVIEW_REQUIRED.md` e os arquivos `src/*.py` e `tests/*.py` propostos.

O gerador recusa caminhos absolutos, traversal com `..`, extensões não Python, duplicidades, blocos incompletos e alguns padrões de segredo. Esses controles não tornam o código da IA seguro para executar. Não extrai nem escreve arquivos dentro do projeto automaticamente, não executa scripts, não instala dependências e não faz push ao GitHub.

Se a NVIDIA responder apenas com um plano descritivo, o botão avisará que não encontrou blocos de arquivos. Isso é esperado e não deve ser tratado como implementação concluída.

## Próximos marcos
- Comparação de diferenças com arquivos existentes antes de aceitar alterações
- Execução de testes em sandbox após autorização explícita
- Integração autenticada do frontend com serviço local, sem expor a chave no GitHub Pages
