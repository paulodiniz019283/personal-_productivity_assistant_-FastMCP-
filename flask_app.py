from flask import Flask
from flask_restx import Api, Resource

app = Flask(__name__)
api = Api(app, doc='/swagger.json', version='1.0', title='Generic Problems API for AI Agent')

ns = api.namespace("problems", description="Operações relacionadas a problemas e chamados")

# 🔹 Banco de dados simulado para a IA poder consultar dados reais
MOCK_PROBLEMS = [
    {"id": 1, "title": "Servidor fora do ar", "status": "open", "user_id": 101, "category": "infra"},
    {"id": 2, "title": "Erro no login", "status": "closed", "user_id": 102, "category": "auth"},
    {"id": 3, "title": "Lentidão no banco de dados", "status": "open", "user_id": 101, "category": "database"}
]

# 1. Listar todos os problemas
@ns.route("/")
class ProblemList(Resource):
    def get(self):
        """Retorna todos os problemas cadastrados."""
        return MOCK_PROBLEMS

# 2. Buscar problema por ID
@ns.route("/<int:id>")
class ProblemByID(Resource):
    def get(self, id):
        """Retorna os detalhes de um problema específico pelo seu ID (número)."""
        problem = next((p for p in MOCK_PROBLEMS if p["id"] == id), None)
        if problem:
            return problem
        return {"error": "Problema não encontrado"}, 404

# 3. Listar meus problemas (Mock)
@ns.route("/my_problems")
class MyProblems(Resource):
    def get(self):
        """Retorna os problemas atribuídos ao usuário logado no momento."""
        # Simulando que o usuário logado é o 101
        return [p for p in MOCK_PROBLEMS if p["user_id"] == 101]

# 4. Filtrar por status
@ns.route("/status/<string:status>")
class ProblemsByStatus(Resource):
    def get(self, status):
        """Retorna problemas filtrados pelo status (ex: 'open' ou 'closed')."""
        return [p for p in MOCK_PROBLEMS if p["status"] == status.lower()]

# 5. Filtrar por categoria
@ns.route("/category/<string:category>")
class ProblemsByCategory(Resource):
    def get(self, category):
        """Retorna problemas filtrados por categoria (ex: 'infra', 'auth')."""
        return [p for p in MOCK_PROBLEMS if p["category"] == category.lower()]

# 6. Buscar problemas de um usuário específico
@ns.route("/user/<int:user_id>")
class ProblemsByUser(Resource):
    def get(self, user_id):
        """Retorna todos os problemas relatados por um ID de usuário específico."""
        return [p for p in MOCK_PROBLEMS if p["user_id"] == user_id]

# 7. Buscar problemas recentes
@ns.route("/recent")
class RecentProblems(Resource):
    def get(self):
        """Retorna os últimos problemas registrados no sistema."""
        # Apenas retornando os 2 últimos como simulação
        return MOCK_PROBLEMS[-2:]

# 8. Estatísticas dos problemas
@ns.route("/stats")
class ProblemStats(Resource):
    def get(self):
        """Retorna uma contagem de problemas abertos e fechados."""
        open_count = sum(1 for p in MOCK_PROBLEMS if p["status"] == "open")
        closed_count = sum(1 for p in MOCK_PROBLEMS if p["status"] == "closed")
        return {"open_problems": open_count, "closed_problems": closed_count, "total": len(MOCK_PROBLEMS)}

if __name__ == '__main__':
    # Mantendo a porta 8000
    app.run(port=8000, debug=True)