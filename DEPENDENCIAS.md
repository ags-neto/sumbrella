# Dependências externas

## DS3231 — biblioteca de relógio em tempo real

- **Usada por:** `Projeto.ino` — `#include <DS3231.h>` e `DS3231 rtc(SDA, SCL)`.
- **Versão:** 1.01 (25 de Agosto de 2014); a 1.0 é de 17 de Agosto de 2014.
- **Origem:** Rinky-Dink Electronics, Henning Karlsen — http://www.RinkyDinkElectronics.com/
- **Licença:** CC BY-NC-SA 3.0 (Atribuição – NãoComercial – CompartilhaIgual).

Porque não está neste repositório: a CC BY-NC-SA 3.0 proíbe uso comercial e
obriga a licenciar obras derivadas sob a mesma licença, o que é incompatível
com a licença MIT deste repositório (que autoriza uso comercial). A biblioteca
foi retirada do repositório e tem de ser instalada à parte:

1. Descarregar a versão 1.01 em http://www.RinkyDinkElectronics.com/ (DS3231).
2. Instalar na pasta `libraries/` do Arduino IDE, ou declarar como dependência
   se construíres com PlatformIO ou `arduino-cli` (o IDE do Arduino não procura
   uma pasta `libs/` dentro do sketch).
3. Uso comercial da biblioteca exige uma licença paga ao autor dela.

A remoção foi feita **no repositório** (índice e histórico a partir daqui); não
apaga nenhuma cópia da biblioteca que exista fora do Git, no disco do autor.

## Como a dependência é declarada agora

`lib_deps` em `platformio.ini` (projecto do `Projeto.ino`):

```ini
lib_deps =
    https://github.com/whonore/DS3231.git#v1.01
```

A biblioteca **não está no registry oficial do PlatformIO**: foram verificados
os 87 resultados da pesquisa por `DS3231` e nenhum expõe a API que `Projeto.ino`
usa (`class Time` com o campo `hour`, `char *getTimeStr()`, e o construtor
`DS3231(data_pin, sclk_pin)`). Por isso fica fixa à tag `v1.01` de um espelho,
cujos ficheiros foram comparados byte a byte com o `libs/DS3231` que saiu deste
repositório: `DS3231.h`, `DS3231.cpp`, `hardware/avr/HW_AVR.h`,
`hardware/avr/HW_AVR_defines.h`, `keywords.txt` e `Documentation/version.txt`
têm o mesmo SHA-256, e `version.txt` diz 1.01 (25 de Agosto de 2014).

O espelho é uma cópia da biblioteca original, redistribuída sob a mesma licença
CC BY-NC-SA 3.0; continua a não ser este repositório a redistribuí-la.
