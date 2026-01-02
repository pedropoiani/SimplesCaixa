// Serverless Function - Valida senha antes de retornar dados
// A senha fica em variável de ambiente (segura)

const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  // Permitir CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Preflight request
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Apenas POST
  if (req.method !== 'POST') {
    return res.status(405).json({ erro: 'Método não permitido' });
  }
  
  try {
    const { senha } = req.body;
    
    // Senha configurada no Vercel (Environment Variables)
    const senhaCorreta = process.env.SENHA_ACESSO;
    
    if (!senhaCorreta) {
      return res.status(500).json({ erro: 'Senha não configurada no servidor' });
    }
    
    if (!senha || senha !== senhaCorreta) {
      return res.status(401).json({ erro: 'Senha incorreta' });
    }
    
    // Senha correta - retornar dados
    const dadosPath = path.join(process.cwd(), 'docs', 'd8f3a2b9c1e7.json');
    
    if (!fs.existsSync(dadosPath)) {
      return res.status(404).json({ 
        erro: 'Dados não encontrados',
        movimentacoes: [] 
      });
    }
    
    const dados = JSON.parse(fs.readFileSync(dadosPath, 'utf8'));
    
    // Remover senha do retorno (segurança extra)
    delete dados.senha;
    
    return res.status(200).json(dados);
    
  } catch (error) {
    console.error('Erro na API:', error);
    return res.status(500).json({ erro: 'Erro interno do servidor' });
  }
}
