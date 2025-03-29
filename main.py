from flask import Flask, render_template, request, jsonify
from sympy import symbols, Eq, solve, sympify, latex, SympifyError  # 添加导入

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve_equations():
    data = request.json
    equations = data['equations']
    print(f"接收到的方程是：{equations}")
    try:
        all_symbols = set()
        for eq in equations:
            if len(eq) == 2:
                for side in eq:
                    parsed_side = side.replace(' ', '').replace(')(', ')*(').replace('][', ']*[')
                    expr = sympify(parsed_side)
                    all_symbols.update(expr.free_symbols)
        
        base_symbols = {s for s in all_symbols if not any(t in str(s) for t in ['*', '/', '**'])}
        variables = sorted([str(s) for s in base_symbols], key=lambda x: x.lower())

        # Build equation list
        eqlist = []
        for i, equation in enumerate(equations, 1):
            try:
                lhs, rhs = equation[0], equation[1]
                eqlist.append(Eq(sympify(lhs), sympify(rhs)))
            except (IndexError, TypeError, SympifyError) as e:
                print(f"Equation {i} error: {e}")

        # Solve equations
        solutions = solve(eqlist, symbols(','.join(variables)), dict=True)

        # Serialize solutions
        serialized_solutions = {'solutions': [], 'variables': variables}
        if solutions:
            for sol in solutions:
                solution_dict = {}
                for var, val in sol.items():
                    solution_dict[str(var)] = {
                        'latex': latex(val.simplify()),
                        'str': str(val.simplify())
                    }
                if solution_dict:
                    serialized_solutions['solutions'].append(solution_dict)

        print(f"方程{data['equations']}的答案是：{serialized_solutions}")
        return jsonify(serialized_solutions)
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=False, port=5000)
