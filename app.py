from src import create_app

app = create_app(config_class='config.Config')


if __name__ == '__main__':
    app.run(port=5000, debug=True)


