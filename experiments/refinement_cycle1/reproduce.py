"""Git-only reconstruction of all 432 predictive fits, in recorded phase order."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from .paths import ROOT, run_root
from src.models.io import write_json


def execute(module, *args):
    command = [sys.executable, '-m', module, *map(str, args)]
    print('RUN', ' '.join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main(output):
    output = (ROOT / output).resolve()
    if output.exists() or not output.is_relative_to(ROOT) or output == ROOT:
        raise ValueError('Choose a new dedicated output within this checkout')
    os.environ['IT5006_REFINEMENT_RUN_ROOT'] = str(output)
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ.setdefault('MPLCONFIGDIR', str(output/'mpl-cache'))
    output.mkdir(parents=True)
    try:
        execute('experiments.refinement_cycle1.initial_reference.diagnostics', '--out', output/'initial_reference/results')
        execute('experiments.refinement_cycle1.initial_reference.audit')
        execute('src.models.refinement_finalize', '--output', output/'core', '--evidence', output/'initial_reference')
        from .core_verify import verify_core, verify_terminal
        verify_core(output/'core')
        execute('src.models.refinement_terminal', '--create-freeze', '--freeze', output/'core_terminal_freeze.json',
                '--bundles', output/'core', '--verification', output/'core/verification.json')
        execute('src.models.refinement_terminal', '--freeze', output/'core_terminal_freeze.json', '--output', output/'core_terminal')
        verify_terminal(output/'core_terminal', output/'core')
        execute('experiments.feature_selection_v3.runner', '--output', output/'screen')
        execute('experiments.feature_selection_v3.verify_screen', '--input', output/'screen')
        execute('experiments.feature_selection_v3.combination_runner', '--output', output/'combinations')
        execute('experiments.feature_selection_v3.verify_screen', '--input', output/'combinations')
        execute('experiments.feature_selection_v3.compare_combinations', '--input', output/'combinations')
        execute('experiments.feature_selection_v3.model_runner', '--output', output/'model_gate')
        execute('experiments.feature_selection_v3.verify_screen', '--input', output/'model_gate')
        execute('experiments.feature_selection_v3.compare_models', '--input', output/'model_gate')
        execute('experiments.feature_selection_v3.baseline_diagnostics', '--input', output/'model_gate')
        # The accepted history has a second descriptive diagnostic version
        # adding calendar-support evidence; it adds no predictive fit.
        execute('experiments.feature_selection_v3.baseline_diagnostics', '--input', output/'model_gate',
                '--output', output/'model_gate/baseline-diagnostics-v2')
        execute('src.models.refinement_selected', 'build', '--output', output/'final')
        execute('src.models.refinement_selected_verify', '--run', output/'final')
        execute('src.models.refinement_diagnostics', '--run', output/'final')
        execute('src.models.refinement_selected_terminal', '--run', output/'final', '--acknowledge-previously-inspected-terminal')
        execute('src.models.refinement_selected_terminal_verify', '--run', output/'final')
        execute('experiments.refinement_cycle1.evidence', 'compare', '--run', output)
        execute('experiments.refinement_cycle1.report_evidence', '--run', output/'final', '--verify')
        execute('experiments.refinement_cycle1.verify_decisions', '--run', output)
        execute('unittest', 'experiments.refinement_cycle1.initial_reference.test_diagnostics',
                'experiments.feature_selection_v3.test_runner', 'experiments.feature_selection_v3.test_combinations',
                'experiments.feature_selection_v3.test_model_gate', 'src.models.tests.test_refinement_selected',
                'src.models.tests.test_refinement_core', 'src.models.tests.test_refinement_terminal')
        write_json({'status':'passed','predictive_fits':432,'phases':{'initial_diagnostics':255,'core_final':8,'blocks':50,
                   'combinations':50,'model_gate':50,'final_application':19},'reused_results_not_new_fits':15,
                   'terminal_assessments':2,'terminal_is_previously_inspected':True}, output/'reproduction_verification.json')
    except Exception as error:
        write_json({'status':'failed_preserved','error':repr(error),'no_automatic_retry_or_retuning':True}, output/'reproduction_failure.json')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--acknowledge-previously-inspected-terminal', action='store_true')
    args = parser.parse_args()
    if not args.acknowledge_previously_inspected_terminal:
        parser.error('Full reconstruction includes both historical terminal diagnostics; explicit acknowledgement required')
    main(args.output)
