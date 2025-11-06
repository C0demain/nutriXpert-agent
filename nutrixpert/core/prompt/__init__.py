"""
Pacote de prompts do sistema multi-agent NutriXpert.

Este módulo exporta as instruções (system prompts) de todos os agentes:
- Root Agent (coordenador)
- Agente Nutricional
- Agente Metabólico (MedGemma)
- Agente de Planejamento
- Agente Educativo

Cada prompt define o comportamento e o tom de atuação de um agente especializado.
"""

from .ROOT_AGENT_INSTR import ROOT_AGENT_INSTR
from .AGENT_NUTRICAO_INSTR import AGENT_NUTRICAO_INSTR
from .AGENT_METABOLICO_INSTR import AGENT_METABOLICO_INSTR
from .AGENT_PLANEJAMENTO_INSTR import AGENT_PLANEJAMENTO_INSTR
from .AGENT_EDUCATIVO_INSTR import AGENT_EDUCATIVO_INSTR
from .AGENT_ANAMNESE_INSTR import AGENT_ANAMNESE_INSTR
