import json
from tests import BaseTestCase
from redash import models
from redash import import_export
from factories import user_factory, dashboard_factory


class ImportTest(BaseTestCase):
    def setUp(self):
        super(ImportTest, self).setUp()

        with open('flights.json') as f:
            self.dashboard = json.loads(f.read())
            self.user = user_factory.create()

    def test_imports_dashboard_correctly(self):
        importer = import_export.Importer()
        dashboard = importer.import_dashboard(self.user, self.dashboard)

        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.name, self.dashboard['name'])
        self.assertEqual(dashboard.slug, self.dashboard['slug'])
        self.assertEqual(dashboard.user, self.user)

        self.assertEqual(dashboard.widgets.count(),
                         reduce(lambda s, row: s + len(row), self.dashboard['widgets'], 0))

        self.assertEqual(models.Visualization.select().count(), dashboard.widgets.count())
        self.assertEqual(models.Query.select().count(), dashboard.widgets.count()-1)
        self.assertEqual(models.QueryResult.select().count(), dashboard.widgets.count()-1)

    def test_imports_updates_existing_models(self):
        importer = import_export.Importer()
        importer.import_dashboard(self.user, self.dashboard)

        self.dashboard['name'] = 'Testing #2'
        dashboard = importer.import_dashboard(self.user, self.dashboard)
        self.assertEqual(dashboard.name, self.dashboard['name'])
        self.assertEquals(models.Dashboard.select().count(), 1)

    def test_using_existing_mapping(self):
        dashboard = dashboard_factory.create()
        mapping = {
            'Dashboard': {
                "1": dashboard.id
            }
        }

        importer = import_export.Importer(object_mapping=mapping)
        imported_dashboard = importer.import_dashboard(self.user, self.dashboard)

        self.assertEqual(imported_dashboard, dashboard)