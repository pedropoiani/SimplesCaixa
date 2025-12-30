#!/bin/bash
# Script de execução do PDV-MF

# Vai para o diretório do script
cd "$(dirname "$0")"

# Executa o programa
python3 main.py

# Se houver erro, mostra mensagem
if [ $? -ne 0 ]; then
    echo "Erro ao executar o PDV-MF"
    echo "Verifique se o Python 3 está instalado"
    read -p "Pressione ENTER para fechar..."
fi
