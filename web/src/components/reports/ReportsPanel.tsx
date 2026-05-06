import type { ReportArtifacts, ReportHistoryItem } from '../../types/eval'
import { getReportFileUrl } from '../../lib/api'

type ReportsPanelProps = {
  latest: ReportArtifacts | null
  history: ReportHistoryItem[]
}

export function ReportsPanel({ latest, history }: ReportsPanelProps) {
  return (
    <section className="panel reports-panel">
      <div className="panel-header">
        <div>
          <h2>报告文件</h2>
          <p className="panel-subtitle">latest 与历史结果入口</p>
        </div>
      </div>
      <div className="report-links">
        <a href={getReportFileUrl(latest?.latest_html ?? latest?.html)} target="_blank" rel="noreferrer">
          打开 latest.html
        </a>
        <a href={getReportFileUrl(latest?.latest_json ?? latest?.json)} target="_blank" rel="noreferrer">
          打开 latest.json
        </a>
      </div>
      <div className="history-list">
        {history.length === 0 ? (
          <div className="empty-state">暂无历史 JSON 报告。</div>
        ) : (
          history.map((item) => (
            <a key={item.path} href={getReportFileUrl(item.path)} target="_blank" rel="noreferrer">
              {item.name}
            </a>
          ))
        )}
      </div>
    </section>
  )
}
