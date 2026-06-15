Precisamos tornar a movimentação de cards o mais eficiente e econômica possível, precisamos tratá-las da seguinte maneira:

# Modificações prévias necessárias
- criar configuração de atributo `boards.create-remote-boards` no arquivo `pipe.yml`, sendo opcional, booleano e valor default = false; 
- criar configuração de atributo `boards.allow-del-remote-issue` no arquivo `pipe.yml`, sendo opcional, booleano e valor default = false; 
- remover os tatus de issues 'l-mv' e 'b-mv', usaremos 'l-sync' e 'b-sync' no lugar;


# Sincronização inicial do serviço
Trata-se da execução realizada ao iniciar a main

## Criação do projeto
Gatilho: não haver arquivo `.pipe/snapshot.json` no projeto
- Criar arquvo `.pipe/snapshot.json`;
- criar a estrutura base no arquivo snapshot;
- criar a estrutura de diretórios em `.pipe/boards` de acordo com spnapshot
- Caso o atributo `boards.create-remote-boards` no arquivo `pipe.yml` for igual a true:
    - criar boards no github
- Setar a data de atualização do arquivo pipe.yml no spapshot

## Quando o projeto já existe
Gatilho: haver arquivo `.pipe/snapshot.json` no projeto
- se a data de atualização do arquivo pipe.yml for diferente do snapshot:
    - Caso o atributo `boards.create-remote-boards` no arquivo `pipe.yml` for igual a true:
        - atualizar a estrutura de boards no githup de acordo com o arquivo pipe.yml
- atualizar o atributo `last_sync` em `.pipe/snapshot.json` com a data e hora atual
- Executar a sincronização de issues

# Sincronização a cada virada de dia (dentro do loop)
Gatilho: propriedade `last_sync` em `.pipe/snapshot.json` for ontem ou antes
- Caso o atributo `boards.create-remote-boards` no arquivo `pipe.yml` for igual a true:
    - atualizar a estrutura de boards no githup de acordo com o arquivo pipe.yml
- buscar do github a lista de todas as issues ativas e recuperar do arquivo snapshot a lista de todas as issues, faça:
    - se a issue existir no github e não existir no snapshot, ela deve ser registrada no snapshot com status 'b-new' com os dados id, name, column, b-time e created_at preenchidos, os demais nulos;
    - se a issue existir no snapshot e não existir no git hub e o status no snapshot for igual a 'ok', o status deve mudar para 'b-del'
- atualizar o atributo `last_sync` em `.pipe/snapshot.json` com a data e hora atual

# Sincronização a cada loop
Executado no inicio do loop a cada volta
- Executar a sincronização de issues

# Sincronização de issues
A sincronização precisa ser executada na ordem abaixo
1. Dos diretórios locais para o arquivo Snapshot:
    - vasculhar todos os diretórios dentro de `.pipe/boards` buscando por aquivos principais `<id>-<slug>.md`, para cada arquivo encontrado, faça:
        - se existe localmente e não existir em snapshot, crieo e sete o status como 'l-new';
        - se existir em snapshot, não existir localmente e o status for igual a 'ok', então o status deve ser modificado para 'l-del';
        - se existir em ambos e o atributo l-time for mais antigo que a data de modificação do arquivo, faça:
            - caso o atributo column for diferente do diretório atual do arquivo: atualize o column com o nome correto da coluna de acordo com o diretório atual do arquivo assim como atributo path;
            - Caso os arquivos write e ou history tenham ficado pra trás, o history deve ser removido e o write deve ser movido para o novo local, caso já existe um write no novo local e ambos estiverem preenchidos, neste caso, os arquivos deve ser mesclados;
            - mude o status para 'l-sync';
        - se existir em ambos e o atributo l-time for igual ou mais novo que a data de modificação do arquivo, não faça nada;
2. Do snapshot para os boards do GitHub:
    - para cada issue no snapshot com status igual a l-sync, faça:
        - se issue estiver em uma coluna do board diferente do atributo column do snapshot, então: mover o issue para a coluna correta;
        - se o body da issue estiver diferente do conteudo do body do arquivo, atualizar o body da issue com o conteúdo do body local;
        - se o write estiver preenchido, o conteúdo do write deve ser adicionado como comentário na issue e o arquivo deve ser limpo no final;
        - o arquivo history deve ser recriado com o histórico atualizado;
        - o atributo b-time deve ser atualizado com a data de modificação da issue no github
        - o atributo status da issue modificado para 'ok';
    - se o atributo `boards.allow-del-remote-issue` no arquivo `pipe.yml` for igual a true, faça:
        - para cada issue no snapshot com status igual a l-del, faça:
            - Anotar no compentário da issue "Issue removida via agent";
            - Fechar a issue no github;
            - remover a issus do snapshot;
3. Dos boards github para o arquivo Snapshot:
Afim de minimizar a utilização da api do github vamos utilizar a consulta por modificação após a data/hora da ultima consulta
    - Para cada issue retornada, se a data da modificação da issue for mais recente que o atributo b-time, faça:
        - o status da issue no snapshot deve ser modificado para b-sync;
        - se o body da issue no github for diferente do body no local, então o body local deve ser modificado;
        - o arquivo history local deve ser criado/modificado para refletir o hostórico atual;
        - o arquivo write deve ser criado/recriado em branco;
        - se a coluna da issue for diferente do atributo column do snapshot, então o atributo column deve ser modificado para o nome da nova coluna atual no github (usar o pipe.yml como referencia), imediatamente após, os arquivos da issue devem ser movidos para o diretório da nova coluna e os atributos path, history_path e write_path devem ser atualizados;
        - o atributo b-time recebe o updtatedat da issue no github
        - o status deve ser modificado para 'ok'
4. Remoção de residuos:
    - para cada issue no snapshot com status b-del: remova os arquivos locais da issue e remova o registro do snapshot
    - para cada issue no snapshot com status b-sync, faça:
        - se o body da issue no github for diferente do body no local, então o body local deve ser modificado;
        - o arquivo history local deve ser criado/modificado para refletir o hostórico atual;
        - o arquivo write deve ser criado/recriado em branco;
        - se a coluna da issue for diferente do atributo column do snapshot, então o atributo column deve ser modificado para o nome da nova coluna atual no github (usar o pipe.yml como referencia), imediatamente após, os arquivos da issue devem ser movidos para o diretório da nova coluna e os atributos path, history_path e write_path devem ser atualizados;
        - o atributo b-time recebe o updtatedat da issue no github
        - o status deve ser modificado para 'ok'