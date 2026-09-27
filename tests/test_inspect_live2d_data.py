import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'inspect_live2d_data.py'
SPEC = importlib.util.spec_from_file_location('inspect_live2d_data', SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'raw'
        self.source.mkdir()

    def model(self, name, texture=b'texture', extra=None):
        folder = self.source / name
        folder.mkdir()
        (folder / 'model.moc3').write_bytes(b'moc-fixture-not-runtime')
        (folder / 'texture.png').write_bytes(texture)
        refs = {'Moc': 'model.moc3', 'Textures': ['texture.png']}
        refs.update(extra or {})
        (folder / 'model.model3.json').write_text(json.dumps({'FileReferences': refs}), encoding='utf-8')
        return folder

    def execute(self):
        output = self.base / 'output'
        summary = audit.run(self.source, output)
        assets = [json.loads(line) for line in (output / 'manifest.jsonl').read_text().splitlines()]
        return output, summary, assets

    def test_static_is_not_runtime_and_inputs_unchanged(self):
        folder = self.model('character')
        before = {p.name: p.read_bytes() for p in folder.iterdir()}
        _, summary, assets = self.execute()
        self.assertEqual(summary['static_valid_models'], 1)
        self.assertFalse(assets[0]['runtime_load_tested'])
        self.assertFalse(assets[0]['render_tested'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in folder.iterdir()})

    def test_missing_userdata_and_motion_sound(self):
        self.model('broken', extra={'UserData': 'missing.userdata3.json',
                   'Motions': {'Idle': [{'File': 'missing.motion3.json', 'Sound': 'missing.wav'}]}})
        _, _, assets = self.execute()
        self.assertFalse(assets[0]['static_valid'])
        self.assertEqual(len(assets[0]['errors']), 3)

    def test_texture_variants_are_not_same_bundle(self):
        self.model('a')
        self.model('b')
        self.model('c', texture=b'other texture')
        output, _, _ = self.execute()
        groups = json.loads((output / 'duplicates.json').read_text())
        self.assertEqual(len(groups['identical_moc_files'][0]['paths']), 3)
        self.assertEqual(len(groups['identical_referenced_bundles'][0]['paths']), 2)

    def test_escape_and_symlink_rejected(self):
        external = self.base / 'external.png'
        external.write_bytes(b'texture')
        self.model('escape', extra={'Textures': ['../../external.png']})
        folder = self.model('symlink')
        (folder / 'texture.png').unlink()
        (folder / 'texture.png').symlink_to(external)
        _, summary, assets = self.execute()
        self.assertEqual(summary['static_valid_models'], 0)
        self.assertTrue(all(asset['errors'] for asset in assets))

    def test_malformed_json_and_schema(self):
        folder = self.model('bad-json')
        (folder / 'model.model3.json').write_text('{', encoding='utf-8')
        self.model('bad-schema', extra={'Expressions': None})
        folder = self.model('bad-reference', extra={'Physics': 'p.physics3.json'})
        (folder / 'p.physics3.json').write_text('[]', encoding='utf-8')
        _, summary, _ = self.execute()
        self.assertEqual(summary['models'], 3)
        self.assertEqual(summary['static_valid_models'], 0)

    def test_output_protection_and_repeatability(self):
        self.model('example')
        with self.assertRaises(ValueError):
            audit.run(self.source, self.source / 'output')
        output, _, _ = self.execute()
        with self.assertRaises(FileExistsError):
            audit.run(self.source, output)
        second = self.base / 'second'
        audit.run(self.source, second)
        for name in ('inventory.jsonl', 'manifest.jsonl', 'duplicates.json', 'summary.json'):
            self.assertEqual((output / name).read_bytes(), (second / name).read_bytes())


if __name__ == '__main__':
    unittest.main()
