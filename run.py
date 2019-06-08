# When creating packages, the import app below gets from
# __init__.py file`

from cryptoalpha import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
