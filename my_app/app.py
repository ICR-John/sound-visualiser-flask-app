""" Group 17 Flask app """
""" Created by Ahmed Mohamud, Barraath Jeganathan, Beatrix Popa, Isaiah John, Saeeda Doolan """

from my_app import create_app, config

app = create_app(config.DevelopmentConfig)

if __name__ == '__main__':
    app.run()
