from agents.agents import *

class AgentOrchestrator:
    def orchestrate(self, zip_bytes):
        context = {'zip_bytes': zip_bytes}
        for AgentClass in [
            FileIngestAgent,
            ActivesConsolidationAgent,
            ElegibilityFilterAgent,
            DataMergingAgent,
            AdjustmentAgent,
            CalculationAgent,
            ExcelExportAgent
        ]:
            agent = AgentClass()
            context = agent.run(context)
        return context['output']