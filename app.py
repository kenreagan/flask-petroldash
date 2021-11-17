from src import create_app

app = create_app(config_class='config.Config')


if __name__ == '__main__':
    try:
        app.run(port=5050, debug=True)
    except OSError as e:
        print('Port already occupied please choose other port ...')


