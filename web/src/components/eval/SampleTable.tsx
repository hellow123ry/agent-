import type { EvalSample } from '../../types/eval'

type SampleTableProps = {
  title: string
  samples: EvalSample[]
}

export function SampleTable({ title, samples }: SampleTableProps) {
  return (
    <div className="sample-table-card">
      <div className="panel-header compact">
        <div>
          <h3>{title}</h3>
          <p className="panel-subtitle">样本数 {samples.length}</p>
        </div>
      </div>
      {samples.length === 0 ? (
        <div className="empty-state">暂无样本结果。</div>
      ) : (
        <div className="sample-table">
          <div className="sample-table-head">
            <span>ID</span>
            <span>Domain</span>
            <span>Success</span>
            <span>Turns</span>
          </div>
          {samples.map((sample, index) => (
            <details key={`${sample.sample_id ?? index}-${sample.domain ?? 'na'}`} className="sample-row">
              <summary>
                <span>{sample.sample_id ?? `sample_${index + 1}`}</span>
                <span>{sample.domain ?? 'unknown'}</span>
                <span className={sample.success ? 'ok' : 'bad'}>{String(sample.success)}</span>
                <span>{sample.turns ?? '--'}</span>
              </summary>
              <div className="sample-detail">
                <pre>{JSON.stringify(sample, null, 2)}</pre>
              </div>
            </details>
          ))}
        </div>
      )}
    </div>
  )
}
