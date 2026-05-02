import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    const area = params.area.toUpperCase();
    
    // Mocking area-specific data for the MVP Frontend visualization
    // Em produção, isso faria fetch para o FastAPI: /api/v1/students/me/knowledge-map?area=${area}
    
    const mockData: Record<string, any> = {
        'MT': {
            nodes: [
                { id: "MT_01", name: "Frações", x: 150, y: 150, mastery: 0.8 },
                { id: "MT_02", name: "Regra de Três", x: 350, y: 150, mastery: 0.4 },
                { id: "MT_03", name: "Porcentagem", x: 250, y: 300, mastery: 0.6 },
                { id: "MT_04", name: "Juros Simples", x: 250, y: 450, mastery: 0.2 },
            ],
            edges: [
                { source: "MT_01", target: "MT_03", type: "DEPENDS_ON" },
                { source: "MT_02", target: "MT_03", type: "DEPENDS_ON" },
                { source: "MT_03", target: "MT_04", type: "UNLOCKS" },
            ]
        },
        'CN': {
            nodes: [
                { id: "CN_01", name: "Cinemática Escalar", x: 200, y: 100, mastery: 0.7 },
                { id: "CN_02", name: "Leis de Newton", x: 200, y: 250, mastery: 0.5 },
                { id: "CN_03", name: "Trabalho e Energia", x: 350, y: 180, mastery: 0.3 },
                { id: "CN_04", name: "Eletrodinâmica", x: 300, y: 350, mastery: 0.1 },
            ],
            edges: [
                { source: "CN_01", target: "CN_02", type: "DEPENDS_ON" },
                { source: "CN_02", target: "CN_04", type: "UNLOCKS" },
                { source: "CN_03", target: "CN_04", type: "DEPENDS_ON" },
            ]
        },
        'CH': {
            nodes: [
                { id: "CH_01", name: "Idade Média", x: 150, y: 100, mastery: 0.9 },
                { id: "CH_02", name: "Feudalismo", x: 300, y: 150, mastery: 0.8 },
                { id: "CH_03", name: "Renascimento", x: 200, y: 280, mastery: 0.6 },
                { id: "CH_04", name: "Revolução Industrial", x: 250, y: 450, mastery: 0.3 },
            ],
            edges: [
                { source: "CH_01", target: "CH_02", type: "DEPENDS_ON" },
                { source: "CH_02", target: "CH_03", type: "UNLOCKS" },
                { source: "CH_03", target: "CH_04", type: "DEPENDS_ON" },
            ]
        },
        'LC': {
            nodes: [
                { id: "LC_01", name: "Figuras de Linguagem", x: 150, y: 150, mastery: 0.5 },
                { id: "LC_02", name: "Funções da Linguagem", x: 350, y: 150, mastery: 0.4 },
                { id: "LC_03", name: "Interpretação Textual", x: 250, y: 300, mastery: 0.7 },
                { id: "LC_04", name: "Gêneros Textuais", x: 250, y: 450, mastery: 0.6 },
            ],
            edges: [
                { source: "LC_01", target: "LC_03", type: "DEPENDS_ON" },
                { source: "LC_02", target: "LC_03", type: "DEPENDS_ON" },
                { source: "LC_03", target: "LC_04", type: "UNLOCKS" },
            ]
        }
    };
    
    // Default to MT if area is not recognized
    const fallbackData = mockData['MT'];
    const data = mockData[area] || fallbackData;
    
    return {
        area,
        nodes: data.nodes,
        edges: data.edges
    };
};