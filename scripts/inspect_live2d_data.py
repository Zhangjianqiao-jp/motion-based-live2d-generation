#!/usr/bin/env python3
"""Read-only Live2D inventory; outputs are metadata, not training labels."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import platform
import sys


ASSET_SUFFIXES = (
    '.model3.json', '.moc3', '.cmo3', '.can3', '.physics3.json',
    '.pose3.json', '.cdi3.json', '.motion3.json', '.exp3.json',
    '.userdata3.json', '.psd', '.png', '.jpg', '.jpeg', '.wav',
    '.zip', '.rar', '.7z',
)


def kind(path):
    name = path.name.lower()
    return next((suffix for suffix in ASSET_SUFFIXES if name.endswith(suffix)), None)


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_jsonl(path, rows):
    with path.open('w', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')


def scan(root):
    records, issues = [], []

    def walk_error(error):
        issues.append({'path': str(error.filename), 'error': str(error)})

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        dirs[:] = sorted(d for d in dirs if d not in {'__MACOSX', '.git'})
        for entry in list(dirs):
            path = Path(directory) / entry
            if path.is_symlink():
                dirs.remove(entry)
                issues.append({'path': str(path.relative_to(root)), 'error': 'symlink_skipped'})
        for name in sorted(files):
            if name.startswith('._') or name == '.DS_Store':
                continue
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                issues.append({'path': relative, 'error': 'symlink_skipped'})
                continue
            file_kind = kind(path)
            # Retain documentation as evidence candidates without interpreting rights.
            if file_kind is None and path.suffix.lower() not in {'.txt', '.md', '.pdf', '.html'}:
                continue
            try:
                records.append({'path': relative, 'kind': file_kind or 'document',
                                'bytes': path.stat().st_size, 'sha256': digest(path)})
            except OSError as error:
                issues.append({'path': relative, 'error': str(error)})
    return sorted(records, key=lambda row: row['path']), issues


def model_references(data):
    """Yield schema paths and filenames; malformed entries fail explicitly."""
    if not isinstance(data, dict) or not isinstance(data.get('FileReferences'), dict):
        raise ValueError('FileReferences must be an object')
    refs = data['FileReferences']
    if not isinstance(refs.get('Moc'), str) or not refs['Moc']:
        raise ValueError('Moc must be a nonempty filename')
    if not isinstance(refs.get('Textures'), list) or not refs['Textures']:
        raise ValueError('Textures must be a nonempty list')
    for key in ('Moc', 'Physics', 'Pose', 'DisplayInfo', 'UserData'):
        if key in refs:
            yield key, refs[key]
    for index, name in enumerate(refs['Textures']):
        yield f'Textures/{index}', name
    expressions = refs.get('Expressions', [])
    if not isinstance(expressions, list):
        raise ValueError('Expressions must be a list')
    motions = refs.get('Motions', {})
    if not isinstance(motions, dict):
        raise ValueError('Motions must be an object')
    groups = [('Expressions', expressions)] + [(f'Motions/{key}', val) for key, val in motions.items()]
    for group, entries in groups:
        if not isinstance(entries, list):
            raise ValueError(f'{group} must be a list')
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or 'File' not in entry:
                raise ValueError(f'{group}/{index} must contain File')
            yield f'{group}/{index}/File', entry['File']
            if 'Sound' in entry and entry['Sound'] != '':
                yield f'{group}/{index}/Sound', entry['Sound']


def validate_model(root, record, inventory):
    path = root / record['path']
    asset = {
        'asset_id': hashlib.sha256(record['path'].encode()).hexdigest()[:20],
        'model_path': record['path'], 'model_sha256': record['sha256'],
        'references': [], 'errors': [], 'static_valid': False,
        'runtime_load_tested': False, 'render_tested': False,
        'character_id': None, 'split': 'unassigned', 'license_status': 'unknown',
        'source_url': None, 'archive_provenance': None,
        'editor_psd_pairing': 'unverified',
    }
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        references = list(model_references(data))
    except (OSError, UnicodeError, ValueError) as error:
        asset['errors'].append(str(error))
        return asset
    for role, filename in references:
        ref = {'role': role, 'filename': filename}
        try:
            if not isinstance(filename, str) or not filename or '\\' in filename:
                raise ValueError('invalid or nonportable reference filename')
            if Path(filename).is_absolute():
                raise ValueError('absolute reference rejected')
            candidate = path.parent / filename
            relative = candidate.resolve().relative_to(root).as_posix()
            # Only files explicitly inventoried without following symlinks are accepted.
            lexical = Path(os.path.abspath(candidate)).relative_to(root).as_posix()
            if relative != lexical:
                raise ValueError('symlink reference rejected')
            if relative not in inventory:
                raise ValueError('reference missing, skipped, unreadable or unsupported')
            item = inventory[relative]
            if not item['bytes']:
                raise ValueError('empty referenced file')
            if candidate.suffix.lower() == '.json':
                value = json.loads(candidate.read_text(encoding='utf-8-sig'))
                if not isinstance(value, dict):
                    raise ValueError('referenced JSON must be an object')
            ref.update(path=relative, sha256=item['sha256'], exists=True)
        except (OSError, UnicodeError, ValueError) as error:
            ref.update(exists=False, error=str(error))
            asset['errors'].append(f'{role}: {error}')
        asset['references'].append(ref)
    asset['static_valid'] = not asset['errors']
    asset['moc_sha256'] = next((r.get('sha256') for r in asset['references'] if r['role'] == 'Moc'), None)
    if asset['static_valid']:
        # Role-sensitive content identity: textures and optional resources participate.
        payload = {'model': record['sha256'], 'resources': sorted(
            (r['role'], r['sha256']) for r in asset['references'])}
        asset['bundle_sha256'] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return asset


def duplicate_groups(rows, field, path_field):
    groups = defaultdict(list)
    for row in rows:
        if row.get(field):
            groups[row[field]].append(row[path_field])
    return [{'sha256': key, 'paths': sorted(paths)} for key, paths in sorted(groups.items()) if len(paths) > 1]


def run(source, output):
    source, output = source.resolve(), output.resolve()
    if not source.is_dir():
        raise ValueError('source must be an existing directory')
    if output == source or source in output.parents:
        raise ValueError('output must be outside source')
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'run.json', {'status': 'running', 'source': str(source),
               'python': platform.python_version(), 'command': sys.argv,
               'script_sha256': digest(Path(__file__)), 'schema_version': 1})
    records, issues = scan(source)
    inventory = {row['path']: row for row in records}
    assets = [validate_model(source, row, inventory) for row in records if row['kind'] == '.model3.json']
    moc_records = [row for row in records if row['kind'] == '.moc3']
    duplicates = {
        'identical_moc_files': duplicate_groups(moc_records, 'sha256', 'path'),
        'identical_referenced_bundles': duplicate_groups(assets, 'bundle_sha256', 'model_path'),
        'note': 'Neither hash grouping establishes independent character identity. No files removed.',
    }
    summary = {'inventory_counts': dict(sorted(Counter(row['kind'] for row in records).items())),
               'models': len(assets), 'static_valid_models': sum(a['static_valid'] for a in assets),
               'unique_moc_hashes': len({row['sha256'] for row in moc_records}),
               'scan_issues': len(issues), 'runtime_loads_tested': 0, 'renders_tested': 0,
               'training_ready': False}
    write_jsonl(output / 'inventory.jsonl', records)
    write_jsonl(output / 'manifest.jsonl', assets)
    write_jsonl(output / 'scan_issues.jsonl', issues)
    write_jsonl(output / 'documents.jsonl', [r for r in records if r['kind'] == 'document'])
    write_jsonl(output / 'archives.jsonl', [dict(r, integrity_tested=False, extracted_by_this_run=False)
                                          for r in records if r['kind'] in {'.zip', '.rar', '.7z'}])
    write_json(output / 'duplicates.json', duplicates)
    write_json(output / 'summary.json', summary)
    report = '\n'.join([
        '# Live2D asset preprocessing report', '',
        f"Model manifests: {summary['models']}",
        f"Static reference checks passed: {summary['static_valid_models']}",
        f"Distinct MOC hashes (not characters): {summary['unique_moc_hashes']}",
        f"Scan issues: {summary['scan_issues']}", '',
        'Original files were only read. Archives were inventoried, not extracted or CRC-tested.',
        'JSON/reference checks do not verify MOC compatibility, image decoding or rendering.',
        'Bundle hashes include manifest bytes; renamed/reformatted copies can remain ungrouped.',
        'Document inventory is not a license determination. Character IDs and splits are unassigned.',
        'Next: confirm provenance/permissions and character groups; verify SDK loading/rendering.',
        'DECISION REQUIRED: canonical state, interventions, physics policy and teacher labels.',
        'No RGB renders, motion labels, training data readiness or experimental results are claimed.',
        '', '## Research context', '',
        'Hu et al. (2017), Learning to Predict Part Mobility from a Single Static Snapshot.',
        'https://doi.org/10.1145/3130800.3130811',
        'Context only: this inventory does not implement or validate that method.', '',
    ])
    (output / 'REPORT.md').write_text(report, encoding='utf-8')
    run_info = json.loads((output / 'run.json').read_text(encoding='utf-8'))
    run_info['status'] = 'completed_with_scan_issues' if issues else 'completed'
    write_json(output / 'run.json', run_info)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.home() / 'Downloads')
    parser.add_argument('--output', type=Path, required=True, help='New output directory outside source')
    args = parser.parse_args()
    try:
        summary = run(args.source, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if summary['scan_issues'] or summary['models'] != summary['static_valid_models'] else 0


if __name__ == '__main__':
    sys.exit(main())
