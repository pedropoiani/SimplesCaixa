# 🖥️ Guia de Instalação do PDV-MF no Linux Mint

Este guia explica passo a passo como instalar o sistema PDV-MF em um novo computador com Linux Mint.

---

## 📋 Requisitos

- **Sistema Operacional:** Linux Mint (qualquer versão recente)
- **Python:** 3.6 ou superior (já vem instalado no Linux Mint)
- **Tkinter:** Interface gráfica do Python

---

## 📦 Passo 1: Copiar os Arquivos do Sistema

### Opção A: Via Pendrive

1. Copie toda a pasta `pdvMF` para um pendrive
2. No novo computador, copie a pasta para o local desejado:
   - **Recomendado:** `/home/SEU_USUARIO/pdvMF`
   - Ou: `/home/SEU_USUARIO/Documentos/pdvMF`

### Opção B: Via Rede/Compartilhamento

1. Compacte a pasta: clique com botão direito → "Compactar..."
2. Transfira o arquivo `.zip` para o novo computador
3. Extraia no local desejado

---

## 🔧 Passo 2: Instalar Dependências

Abra o **Terminal** (Ctrl + Alt + T) e execute os comandos:

```bash
# Atualizar repositórios
sudo apt update

# Atualizar pacotes existentes
sudo apt upgrade -y

# Instalar Python 3 (caso não esteja instalado)
sudo apt install python3 -y

# Instalar pip (gerenciador de pacotes Python)
sudo apt install python3-pip -y

# Instalar Tkinter (interface gráfica - OBRIGATÓRIO)
sudo apt install python3-tk -y

# Instalar ferramentas de desenvolvimento Python (opcional, mas recomendado)
sudo apt install python3-dev -y

# Verificar se Python está instalado corretamente
python3 --version

# Verificar se Tkinter está funcionando
python3 -c "import tkinter; print('Tkinter OK - versão:', tkinter.TkVersion)"
```

### Comando Único (Copie e Cole)

Para instalar tudo de uma vez:

```bash
sudo apt update && sudo apt upgrade -y && sudo apt install python3 python3-pip python3-tk python3-dev -y
```

### Verificar Instalação

Após instalar, teste se tudo está funcionando:

```bash
# Testar Python
python3 --version

# Testar Tkinter (deve abrir uma janelinha de teste)
python3 -m tkinter
```

> **Nota:** Se o comando `python3 -m tkinter` abrir uma pequena janela cinza, o Tkinter está funcionando! Feche a janela para continuar.

---

## ⚙️ Passo 3: Dar Permissão de Execução

No Terminal, navegue até a pasta do PDV-MF e dê permissão aos scripts:

```bash
# Navegue até a pasta (ajuste o caminho conforme onde você salvou)
cd ~/pdvMF

# Dar permissão de execução aos scripts
chmod +x pdv.sh
chmod +x main.py
```

**Ou pelo Gerenciador de Arquivos:**
1. Navegue até a pasta `pdvMF`
2. Clique com botão direito em `pdv.sh`
3. Selecione "Propriedades"
4. Vá na aba "Permissões"
5. Marque "Permitir execução do arquivo como programa"

---

## 🧪 Passo 4: Testar a Execução

Antes de criar o atalho, teste se o sistema funciona:

```bash
# No Terminal, dentro da pasta pdvMF:
./pdv.sh

# Ou diretamente com Python:
python3 main.py
```

Se abrir a janela do sistema, está tudo funcionando! ✅

---

## 🖼️ Passo 5: Criar Atalho na Área de Trabalho

### Método 1: Criar Arquivo .desktop Manualmente (Recomendado)

1. Abra o Terminal e execute:

```bash
# Criar o arquivo de atalho
nano ~/Área\ de\ Trabalho/PDV-MF.desktop
```

> **Nota:** Em algumas versões do Linux Mint, a pasta pode se chamar `Desktop` ao invés de `Área de Trabalho`. Nesse caso, use:
> ```bash
> nano ~/Desktop/PDV-MF.desktop
> ```

2. Cole o seguinte conteúdo (ajuste o caminho `/home/SEU_USUARIO/pdvMF` para o caminho real):

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=PDV-MF
Comment=Sistema de Controle de Caixa
Exec=/home/SEU_USUARIO/pdvMF/pdv.sh
Icon=/home/SEU_USUARIO/pdvMF/logos/logo_completa.png
Terminal=false
Categories=Office;Finance;
StartupNotify=true
```

3. Salve o arquivo:
   - Pressione `Ctrl + O` para salvar
   - Pressione `Enter` para confirmar
   - Pressione `Ctrl + X` para sair

4. Dê permissão de execução ao atalho:

```bash
chmod +x ~/Área\ de\ Trabalho/PDV-MF.desktop
# Ou se for Desktop:
chmod +x ~/Desktop/PDV-MF.desktop
```

5. Clique com botão direito no atalho na Área de Trabalho e selecione **"Permitir Execução"** ou **"Trust this application"**

---

### Método 2: Copiar e Editar o Arquivo Existente

1. Copie o arquivo `pdv-mf.desktop` da pasta do sistema para a Área de Trabalho:

```bash
cp ~/pdvMF/pdv-mf.desktop ~/Área\ de\ Trabalho/PDV-MF.desktop
# Ou se for Desktop:
cp ~/pdvMF/pdv-mf.desktop ~/Desktop/PDV-MF.desktop
```

2. Edite o arquivo para corrigir o caminho:

```bash
nano ~/Área\ de\ Trabalho/PDV-MF.desktop
```

3. Altere a linha `Exec=` para o caminho correto:
```ini
Exec=/home/SEU_USUARIO/pdvMF/pdv.sh
Icon=/home/SEU_USUARIO/pdvMF/logos/logo_completa.png
```

4. Salve e dê permissão:
```bash
chmod +x ~/Área\ de\ Trabalho/PDV-MF.desktop
```

---

### Método 3: Via Interface Gráfica

1. Navegue até a pasta `pdvMF`
2. Clique com botão direito no arquivo `pdv.sh`
3. Selecione **"Criar Link"** ou **"Make Link"**
4. Renomeie o link para `PDV-MF`
5. Arraste o link para a Área de Trabalho
6. Clique com botão direito no link → Propriedades → marque "Executável"

---

## 📍 Passo 6: Adicionar ao Menu de Aplicativos (Opcional)

Para ter o PDV-MF no menu de aplicativos:

```bash
# Copiar o arquivo .desktop para aplicativos locais
cp ~/pdvMF/pdv-mf.desktop ~/.local/share/applications/pdv-mf.desktop

# Editar para corrigir os caminhos
nano ~/.local/share/applications/pdv-mf.desktop
```

Ajuste as linhas `Exec=` e `Icon=` para os caminhos corretos e salve.

O aplicativo aparecerá no menu após alguns segundos ou após reiniciar.

---

## 🔄 Migrar Dados do Outro Computador (Opcional)

Se você quer trazer os dados (vendas, histórico) do computador antigo:

### No Computador Antigo:

1. Localize o banco de dados:
```bash
ls ~/.pdvmf/
```

2. Copie a pasta `.pdvmf` para o pendrive:
```bash
cp -r ~/.pdvmf /media/SEU_USUARIO/PENDRIVE/
```

### No Novo Computador:

1. Copie a pasta do pendrive para o home:
```bash
cp -r /media/SEU_USUARIO/PENDRIVE/.pdvmf ~/
```

2. Verifique se copiou corretamente:
```bash
ls ~/.pdvmf/
```
Deve mostrar: `pdvmf.db` e pasta `backups/`

---

## ✅ Resumo dos Comandos (Copie e Cole)

Execute esses comandos em sequência no Terminal (ajuste os caminhos):

```bash
# 1. Instalar Tkinter
sudo apt update && sudo apt install python3-tk -y

# 2. Navegar para a pasta (ajuste o caminho)
cd ~/pdvMF

# 3. Dar permissões
chmod +x pdv.sh main.py

# 4. Testar execução
./pdv.sh

# 5. Criar atalho na Área de Trabalho (ajuste SEU_USUARIO)
cat > ~/Área\ de\ Trabalho/PDV-MF.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=PDV-MF
Comment=Sistema de Controle de Caixa
Exec=/home/SEU_USUARIO/pdvMF/pdv.sh
Icon=/home/SEU_USUARIO/pdvMF/logos/logo_completa.png
Terminal=false
Categories=Office;Finance;
StartupNotify=true
EOF

# 6. Dar permissão ao atalho
chmod +x ~/Área\ de\ Trabalho/PDV-MF.desktop
```

> ⚠️ **Importante:** Substitua `SEU_USUARIO` pelo nome real do usuário no sistema. Para descobrir seu usuário, execute: `whoami`

---

## 🐛 Resolução de Problemas

### Erro: "Permissão negada"
```bash
chmod +x ~/pdvMF/pdv.sh
chmod +x ~/pdvMF/main.py
```

### Erro: "python3: command not found"
```bash
sudo apt install python3 python3-tk -y
```

### Erro: "tkinter not found"
```bash
sudo apt install python3-tk -y
```

### Atalho não funciona na Área de Trabalho
1. Clique com botão direito no atalho
2. Selecione "Permitir Execução" ou "Allow Launching"
3. Se não aparecer, vá em Propriedades → Permissões → Marque "Executável"

### O sistema abre em branco ou com erro
1. Abra o Terminal
2. Navegue até a pasta: `cd ~/pdvMF`
3. Execute: `python3 main.py`
4. Veja a mensagem de erro no Terminal

### Dados não aparecem (sistema zerado)
- Os dados ficam em `~/.pdvmf/`
- Se você migrou de outro computador, verifique se copiou essa pasta

---

---

## �📞 Suporte

Se tiver problemas:
1. Verifique se seguiu todos os passos
2. Teste executando pelo Terminal para ver erros
3. Verifique os caminhos nos arquivos .desktop

---

**PDV-MF** - Sistema de Controle de Caixa
Versão para Linux Mint
