export type EvalMetrics = {
  task_success_rate: number
  average_turns: number
  slot_precision: number
  slot_recall: number
  slot_f1: number
}

export type EvalSample = {
  sample_id?: string
  domain?: string
  success: boolean
  turns?: number
  final_reply?: string
  failure_reasons?: string[]
  predicted_slots?: Record<string, unknown>
  expected_slots?: Record<string, unknown>
}

export type SystemEvalResult = {
  metrics: EvalMetrics
  samples: EvalSample[]
}

export type ReportArtifacts = {
  json?: string
  html?: string
  svgs?: Record<string, string>
  latest_json?: string
  latest_html?: string
}

export type EvalJobStatus = {
  job_id: string
  status: string
  dataset_path?: string
  current_system?: string | null
  partial_metrics?: Record<string, EvalMetrics>
  progress?: Record<string, { completed_samples: number; total_samples: number }>
  error?: string
}

export type EvalResult = {
  stacked_multi_agent?: SystemEvalResult
  baseline_single_agent?: SystemEvalResult
  reports?: ReportArtifacts
}

export type ReportHistoryItem = {
  name: string
  path: string
}
