# -*- coding:utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from DataSet import create_app, db

app = create_app('development')
manager = Manager(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    # print app.url_map
    manager.run()
