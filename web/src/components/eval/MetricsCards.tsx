import type { EvalMetrics } from '../../types/eval'

type MetricsCardsProps = {
  metrics?: EvalMetrics
}

const LABELS: Array<[keyof EvalMetrics, string]> = [
  ['task_success_rate', '任务成功率'],
  ['average_turns', '平均轮次'],
  ['slot_precision', '槽位 Precision'],
  ['slot_recall', '槽位 Recall'],
  ['slot_f1', '槽位 F1'],
]

export function MetricsCards({ metrics }: MetricsCardsProps) {
  return (
    <div className="metrics-grid">
      {LABELS.map(([key, label]) => (
        <div key={key} className="metric-card">
          <span>{label}</span>
          <strong>{metrics ? Number(metrics[key]).toFixed(4) : '--'}</strong>
        </div>
      ))}
    </div>
  )
}
