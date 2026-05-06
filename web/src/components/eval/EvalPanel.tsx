import type { EvalJobStatus, EvalResult } from '../../types/eval'
import { MetricsCards } from './MetricsCards'
import { SampleTable } from './SampleTable'

type EvalPanelProps = {
  job?: EvalJobStatus | null
  result?: EvalResult | null
  busy: boolean
  error?: string
  onRun: () => Promise<void>
}

function EvalProgress({
  label,
  completed,
  total,
}: {
  label: string
  completed: number
  total: number
}) {
  const ratio = total > 0 ? Math.min(100, Math.round((completed / total) * 100)) : 0

  return (
    <div className="progress-card">
      <div className="progress-head">
        <strong>{label}</strong>
        <span>
          {completed} / {total || '--'}
        </span>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${ratio}%` }} />
      </div>
      <div className="progress-meta">{ratio}%</div>
    </div>
  )
}

export function EvalPanel({ job, result, busy, error, onRun }: EvalPanelProps) {
  const stackedProgress = job?.progress?.stacked_multi_agent ?? {
    completed_samples: 0,
    total_samples: 0,
  }
  const baselineProgress = job?.progress?.baseline_single_agent ?? {
    completed_samples: 0,
    total_samples: 0,
  }

  return (
    <section className="panel eval-panel">
      <div className="panel-header">
        <div>
          <h2>评测看板</h2>
          <p className="panel-subtitle">启动 run_eval 并查看指标与样本明细</p>
        </div>
        <button type="button" onClick={onRun} disabled={busy}>
          {busy ? '运行中...' : '运行评测'}
        </button>
      </div>
      {error ? <div className="error-banner">{error}</div> : null}
      <div className="job-status">
        <span>job_id: {job?.job_id ?? '--'}</span>
        <span>status: {job?.status ?? 'idle'}</span>
        <span>current_system: {job?.current_system ?? '--'}</span>
      </div>
      <div className="progress-stack">
        <EvalProgress
          label="stacked_multi_agent"
          completed={stackedProgress.completed_samples}
          total={stackedProgress.total_samples}
        />
        <EvalProgress
          label="baseline_single_agent"
          completed={baselineProgress.completed_samples}
          total={baselineProgress.total_samples}
        />
      </div>
      <div className="eval-section">
        <h3>Stacked Multi Agent</h3>
        <MetricsCards metrics={result?.stacked_multi_agent?.metrics} />
      </div>
      <div className="eval-section">
        <h3>Baseline Single Agent</h3>
        <MetricsCards metrics={result?.baseline_single_agent?.metrics} />
      </div>
      <SampleTable title="Stacked Samples" samples={result?.stacked_multi_agent?.samples ?? []} />
      <SampleTable title="Baseline Samples" samples={result?.baseline_single_agent?.samples ?? []} />
    </section>
  )
}
