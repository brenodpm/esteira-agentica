# DEFINIÇÕES GLOBAIS
- definição do contexto do projeto /context >> config
- definição de como trabalhar com o board /knowledge >> config
	- definição de board de bugs e demandas
- definição de como criar/editar issue

# DEFINIÇÕES POR PERFIL (agente)
- Definição de base de conhecimento (docs input) /knowledge >> config
- definição de artefatos gerados (output) /config
- definição do escopo de atuação do agente /config
- definição das permissões do agente /config

# DEFINIÇÃO DA ETAPA
- Definição do agente /prompt
- Definição de modelo /prompt
- Definição da profundidade do raciocínio effort /prompt
- Definição do flow do git /prompt
- Definição do evento do git [criar branch | solicitar merge] /prompt


- definição de para onde movimentar o issue  /prompt
- definição do que anotar no write /prompt

# DEFINIÇOES POR TAREFA (ISSUE)
- definição da branch a ser usada /prompt

# PROMPT FINAL
{se informado modelo: /model {modelo}}
{se informado profundidade: /effort {profundidade}}
/context {caminho do arquivo}
/knowledge {caminho do history}


Etapa: {nome da etapa}
Tarefa: {nome da issue}

Faça:
{se criar branch: - [ ] criar branch {nome da branch} a partir da {branch origem}}
{se não criar branch: - [ ] usar branch {nome da branch}}
- [ ] executar tarefa `{caminho do arquivo}`
- [ ] checar se as tarefas em `/blocked_by` foram concluidas, se não foram, anotar comentário em {endereço write} e encerrar processamento
- [ ] se houver dúvida abrir demanda, bloquear tarefa com a demanda, anotar comentário em {endereço write} e encerrar processamento
- [ ] fazer commit e push
{se solicitar merge: - [ ] criar merge request para {branch alvo}}
- [ ] Anotar um resumo curto do que foi executado em `{caminho do write}`
- [ ] fazer checkout para {branch base} e apagar todas as branchs locais ()


Após conclusão da tarefa mova o issue
{para cada opção: se {condição} >> mover para {diretório alvo} }

# LOG
prompt da solicitação
resumo escrito em write
tempo de execução
movimentação da issue

# PIPE CONTEXT
Diretório `.pipe/boards/` contém todos os boards
a estrutura de diretórios representa .pipe/boards/<nome do board>/<coluna do board>/<issue>.md
Ao lado de cada <issue>.md existe <issue>-history.md com o histórico da issue e <issue>-white.md arquivo que recebe a próxima anotação do histórico
para mover um issue entre colunas basta mover entre os diretórios de colunas ex: Todo >> in progress, basta executar `mv todo/<issue>.md in_progress/<issue>.md`, write e ristore são movidos automaticamente pela pipe
