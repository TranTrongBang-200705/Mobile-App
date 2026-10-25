"""Audit whether optimized EdNet paper IDs have usable live assets.

The historical demo question bank is deliberately excluded.
It does not deploy a benchmark paper or claim live NCD validity.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data' / 'Dense_EdNetTOEIC_Balanced90_90d'
IMAGE_DIR = ROOT / 'image_cache'


def audit(result_path):
    result = json.loads(result_path.read_text(encoding='utf-8'))
    content = json.loads((ROOT / 'pcat_live_questions.json').read_text(encoding='utf-8'))
    catalog = pd.read_csv(DATA / 'toeic_question_catalog.csv').set_index('q_idx')
    reports = {}
    for seed in result['seeds_evaluated']:
        stages = result['per_seed_details'][str(seed)]['selected_paper']
        selected = stages['full_30']
        missing_content = []
        missing_audio = []
        missing_images = []
        mismatched_answer_keys = []
        for q in selected:
            row = catalog.loc[q]
            item = content.get(str(q))
            part = int(row['part'])
            if (not item or item.get('question_id') != str(row['question_id'])
                    or not item.get('question_text') or not item.get('options')):
                missing_content.append(q)
            else:
                expected = ord(str(row['correct_answer']).lower()) - ord('a')
                if item.get('correct_answer_index') != expected:
                    mismatched_answer_keys.append(q)
            if part == 1 and not any((IMAGE_DIR / f'{q}{extension}').is_file()
                                     for extension in ('.png', '.jpg', '.jpeg')):
                missing_images.append(q)
            if part <= 4:
                audio_id = str(q) if part <= 2 else str(row['bundle_id'])
                if not (ROOT / 'audio_cache' / f'{audio_id}.mp3').exists():
                    missing_audio.append(q)
        reports[str(seed)] = {
            'missing_content_ids': sorted(set(missing_content)),
            'missing_audio_ids': sorted(set(missing_audio)),
            'missing_image_ids': sorted(set(missing_images)),
            'mismatched_answer_key_ids': sorted(set(mismatched_answer_keys)),
            'display_assets_complete': not any((missing_content, missing_audio, missing_images, mismatched_answer_keys)),
            'original_ednet_item_content_verified': False,
            'live_ncd_metrics_validated_for_this_content': False,
        }
    return {
        'benchmark': str(result_path),
        'note': 'Demo content is excluded. Display assets alone do not establish live NCD validity.',
        'per_seed': reports,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('result', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.result)
    output = args.output or args.result.with_name(args.result.stem + '_live_asset_audit.json')
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(output)
    for seed, details in report['per_seed'].items():
        print(f"seed {seed}: display_assets_complete={details['display_assets_complete']}, "
              f"missing_content={len(details['missing_content_ids'])}")


if __name__ == '__main__':
    main()
