// Endpoint para bloquear acesso direto a arquivos protegidos
export default function handler(req, res) {
  res.status(403).json({ 
    erro: 'Acesso negado',
    mensagem: 'Este recurso não está disponível diretamente.'
  });
}
